from __future__ import annotations

from datetime import date

from pqrs_router.rules import add_business_days, assess_priority, sla_due
from pqrs_router.taxonomy import Priority, RequestType


def test_add_business_days_skips_weekends():
    # Friday + 1 business day = Monday.
    assert add_business_days(date(2026, 1, 2), 1) == date(2026, 1, 5)
    # Monday + 5 business days = next Monday.
    assert add_business_days(date(2026, 1, 5), 5) == date(2026, 1, 12)


def test_sla_due_uses_type_window():
    due, days = sla_due(date(2026, 1, 5), RequestType.PETITION)
    assert days == 15
    assert due == date(2026, 1, 26)


def test_report_is_high_by_default():
    priority, reasons = assess_priority("I wish to denounce an irregularity.", RequestType.REPORT)
    assert priority is Priority.HIGH
    assert reasons


def test_suggestion_is_low_by_default():
    priority, _ = assess_priority("I propose a change to the portal.", RequestType.SUGGESTION)
    assert priority is Priority.LOW


def test_urgency_raises_priority():
    priority, reasons = assess_priority(
        "There is a dangerous leak, this is urgent.", RequestType.PETITION
    )
    assert priority is Priority.HIGH
    assert any("urgency" in r for r in reasons)
