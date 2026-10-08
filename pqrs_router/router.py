"""Combine the classifier and the rules into a single routing decision."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from .classifier import RequestClassifier
from .rules import assess_priority, sla_due
from .taxonomy import Department, Priority, RequestType


@dataclass
class RoutingDecision:
    request_type: RequestType
    type_confidence: float
    department: Department
    department_confidence: float
    priority: Priority
    priority_reasons: list[str]
    received_date: str
    due_date: str
    sla_business_days: int
    uncertain: bool
    top_terms: list[tuple[str, float]] = field(default_factory=list)


class Router:
    def __init__(self, classifier: RequestClassifier, min_confidence: float = 0.45) -> None:
        self.classifier = classifier
        self.min_confidence = min_confidence

    def route(self, text: str, received: date | None = None) -> RoutingDecision:
        received = received or date.today()
        c = self.classifier.classify(text)
        priority, reasons = assess_priority(text, c.request_type)
        due, days = sla_due(received, c.request_type)
        uncertain = c.type_confidence < self.min_confidence

        return RoutingDecision(
            request_type=c.request_type,
            type_confidence=c.type_confidence,
            department=c.department,
            department_confidence=c.department_confidence,
            priority=priority,
            priority_reasons=reasons,
            received_date=received.isoformat(),
            due_date=due.isoformat(),
            sla_business_days=days,
            uncertain=uncertain,
            top_terms=c.top_terms,
        )
