"""Voice gate. Shared banlist plus per-tenant additive overrides."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

BANNED_FAIL: tuple[str, ...] = (
    "leverage",
    "synergy",
    "synergies",
    "game-changer",
    "game changer",
    "revolutionary",
    "disrupt",
    "disruption",
    "unlock",
    "unleash",
    "delve",
    "delves",
    "in today's fast-paced world",
    "in conclusion",
    "moreover",
    "furthermore",
    "best-in-class",
    "world-class",
    "cutting-edge",
    "seamless",
    "seamlessly",
    "robust",
    "elevate",
    "supercharge",
)


@dataclass
class VoiceResult:
    passed: bool
    hits: list[str]

    def __bool__(self) -> bool:
        return self.passed


def merged_banlist(tenant_overrides: Iterable[str] | None = None) -> list[str]:
    base = list(BANNED_FAIL)
    if tenant_overrides:
        for term in tenant_overrides:
            if term and term not in base:
                base.append(term)
    return base


def check(text: str, tenant_overrides: Iterable[str] | None = None) -> VoiceResult:
    """Return a VoiceResult naming any banned terms present in `text`."""
    banlist = merged_banlist(tenant_overrides)
    hits: list[str] = []
    lowered = text.lower()
    for term in banlist:
        pattern = r"\b" + re.escape(term.lower()) + r"\b"
        if re.search(pattern, lowered):
            hits.append(term)
    return VoiceResult(passed=not hits, hits=hits)


def check_tenant(text: str, tenant) -> VoiceResult:
    """Convenience wrapper that pulls extra_banned from a loaded Tenant."""
    extras = (tenant.voice_overrides or {}).get("extra_banned", []) or []
    return check(text, extras)
