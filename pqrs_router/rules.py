"""Deterministic rules: statutory deadlines (SLA) and priority.

The classifier decides *what* a request is; these rules decide *how urgently* it
must be handled and *by when*. Deadlines are counted in business days per request
type; priority starts from the type and is raised to high when the text carries
urgency (safety, health, outages, fraud, vulnerable people).
"""

from __future__ import annotations

from datetime import date, timedelta

from .taxonomy import SLA_BUSINESS_DAYS, URGENCY_TERMS, Priority, RequestType

# Baseline priority by request type, before urgency is considered.
_BASE_PRIORITY: dict[RequestType, Priority] = {
    RequestType.SUGGESTION: Priority.LOW,
    RequestType.PETITION: Priority.LOW,
    RequestType.COMPLAINT: Priority.MEDIUM,
    RequestType.CLAIM: Priority.MEDIUM,
    RequestType.REPORT: Priority.HIGH,
}


def add_business_days(start: date, days: int) -> date:
    """Add ``days`` business days (Mon-Fri) to ``start``."""
    current = start
    added = 0
    while added < days:
        current += timedelta(days=1)
        if current.weekday() < 5:
            added += 1
    return current


def sla_due(received: date, request_type: RequestType) -> tuple[date, int]:
    days = SLA_BUSINESS_DAYS[request_type]
    return add_business_days(received, days), days


def assess_priority(text: str, request_type: RequestType) -> tuple[Priority, list[str]]:
    reasons: list[str] = []
    priority = _BASE_PRIORITY[request_type]
    reasons.append(f"{request_type.value} has baseline priority {priority.value}")

    low = text.lower()
    hits = [term for term in URGENCY_TERMS if term in low]
    if hits:
        priority = Priority.HIGH
        reasons.append("raised to high by urgency terms: " + ", ".join(hits))
    return priority, reasons
