from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture
def procurement_tenant_dir(repo_root) -> Path:
    return repo_root / "tenants" / "procurement-analyst"


@pytest.fixture
def fixture_brief(repo_root) -> Path:
    return repo_root / "review-queue" / "procurement-analyst" / "2026-W34.md"
