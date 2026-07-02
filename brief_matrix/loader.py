"""Tenant config loader. Reads and validates per-tenant directories."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = REPO_ROOT / "schemas"


class TenantError(Exception):
    """Raised when a tenant directory is malformed."""


@dataclass
class Tenant:
    path: Path
    config: dict[str, Any]
    sources: dict[str, Any]
    section_structure: list[dict[str, Any]]
    voice_overrides: dict[str, Any] = field(default_factory=dict)

    @property
    def id(self) -> str:
        return self.config["id"]

    @property
    def section_names(self) -> list[str]:
        return [s["name"] for s in self.section_structure]


def _load_yaml(path: Path) -> Any:
    if not path.exists():
        raise TenantError(f"missing required file: {path}")
    with path.open("r", encoding="utf-8") as fh:
        try:
            return yaml.safe_load(fh)
        except yaml.YAMLError as exc:
            # Surface a file-named TenantError instead of a raw scanner/parser
            # trace so cmd_validate can report it as a clean FAIL.
            raise TenantError(f"{path}: invalid YAML: {exc}") from exc


def _load_schema(name: str) -> dict[str, Any]:
    with (SCHEMA_DIR / name).open("r", encoding="utf-8") as fh:
        return json.load(fh)


def load_tenant(tenant_dir: str | Path) -> Tenant:
    """Load a tenant directory, validating against schemas."""
    tenant_dir = Path(tenant_dir).resolve()
    if not tenant_dir.is_dir():
        raise TenantError(f"not a directory: {tenant_dir}")

    config = _load_yaml(tenant_dir / "config.yaml")
    if not isinstance(config, dict):
        raise TenantError(f"{tenant_dir}/config.yaml must be a mapping")

    schema = _load_schema("tenant.schema.json")
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(config), key=lambda e: list(e.path))
    if errors:
        bullets = "\n".join(f"  - {e.message}" for e in errors)
        raise TenantError(f"tenant config failed schema:\n{bullets}")

    if config["id"] != tenant_dir.name:
        raise TenantError(
            f"tenant id '{config['id']}' does not match directory name "
            f"'{tenant_dir.name}'"
        )

    sources = _load_yaml(tenant_dir / config["source_registry"])
    if not isinstance(sources, dict) or "sources" not in sources:
        raise TenantError(
            f"{tenant_dir}/{config['source_registry']} must have a 'sources' key"
        )

    section_file = tenant_dir / config["spec_ledger_ref"] / "section-structure.yaml"
    section_doc = _load_yaml(section_file)
    if not isinstance(section_doc, dict) or "sections" not in section_doc:
        raise TenantError(f"{section_file} must have a 'sections' key")
    section_structure = section_doc["sections"]
    if not isinstance(section_structure, list) or not section_structure:
        raise TenantError(f"{section_file} 'sections' must be a non-empty list")

    voice_overrides: dict[str, Any] = {}
    if "voice_overrides" in config:
        override_file = tenant_dir / config["voice_overrides"]
        if override_file.exists():
            doc = _load_yaml(override_file)
            if doc is not None and not isinstance(doc, dict):
                raise TenantError(f"{override_file} must be a mapping or empty")
            voice_overrides = doc or {}
            _validate_voice_overrides(voice_overrides, override_file)

    return Tenant(
        path=tenant_dir,
        config=config,
        sources=sources,
        section_structure=section_structure,
        voice_overrides=voice_overrides,
    )


def _validate_voice_overrides(doc: dict[str, Any], origin: Path) -> None:
    """Per R-BM-008: overrides may extend, never remove shared terms."""
    from brief_matrix.voice_gate import BANNED_FAIL

    extra = doc.get("extra_banned", [])
    if extra is None:
        extra = []
    if not isinstance(extra, list) or not all(isinstance(t, str) for t in extra):
        raise TenantError(f"{origin}: 'extra_banned' must be a list of strings")

    shared_lower = {t.lower() for t in BANNED_FAIL}
    removed = [t for t in extra if t.lower().startswith("-")]
    for r in removed:
        bare = r.lstrip("-").strip().lower()
        if bare in shared_lower:
            raise TenantError(
                f"{origin}: voice override attempts to remove shared "
                f"banlist term '{bare}'. Overrides may only extend."
            )

    allow = doc.get("allow_after_marker", [])
    if allow is None:
        allow = []
    if not isinstance(allow, list):
        raise TenantError(
            f"{origin}: 'allow_after_marker' must be a list when present"
        )
