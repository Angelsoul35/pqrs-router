from __future__ import annotations

import pytest

from pqrs_router.classifier import RequestClassifier


@pytest.fixture(scope="session")
def classifier() -> RequestClassifier:
    # Fit once and share across tests; training is deterministic.
    return RequestClassifier().fit()
