"""Fixture fetcher. Returns the tenant's sources.yaml entries as the
candidate set; no network access. v0.1 placeholder for live ingest."""

from __future__ import annotations

from typing import Any

from brief_matrix.loader import Tenant


def run(tenant: Tenant) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for src in tenant.sources.get("sources", []):
        for fix in src.get("fixture_items", []) or []:
            items.append(
                {
                    "source_id": src.get("id"),
                    "kind": src.get("kind"),
                    **fix,
                }
            )
    return items
