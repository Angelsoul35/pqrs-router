"""Orchestration: fit the classifier and route requests."""

from __future__ import annotations

from dataclasses import asdict
from datetime import date

from .classifier import RequestClassifier
from .config import Settings, get_settings
from .router import Router


class PQRSService:
    def __init__(
        self,
        settings: Settings | None = None,
        classifier: RequestClassifier | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.classifier = classifier or RequestClassifier().fit()
        self.router = Router(self.classifier, min_confidence=self.settings.min_confidence)

    def route(self, text: str, received: date | None = None) -> dict:
        decision = self.router.route(text, received=received)
        result = asdict(decision)
        result["request_type"] = decision.request_type.value
        result["department"] = decision.department.value
        result["priority"] = decision.priority.value
        return result
