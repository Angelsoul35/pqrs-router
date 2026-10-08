from __future__ import annotations

from datetime import date

from fastapi.testclient import TestClient

from pqrs_router.config import Settings
from pqrs_router.router import Router
from pqrs_router.service import PQRSService


def test_router_full_decision(classifier):
    router = Router(classifier, min_confidence=0.45)
    decision = router.route(
        "I demand a correction of an incorrect charge on my invoice.",
        received=date(2026, 1, 5),
    )
    assert decision.request_type.value == "claim"
    assert decision.department.value == "billing"
    assert decision.due_date == "2026-01-26"
    assert decision.sla_business_days == 15
    assert decision.uncertain is False


def test_router_flags_uncertain(classifier):
    router = Router(classifier, min_confidence=0.99)  # force uncertainty
    decision = router.route("hello there", received=date(2026, 1, 5))
    assert decision.uncertain is True


def _service(classifier) -> PQRSService:
    return PQRSService(settings=Settings(), classifier=classifier)


def test_service_route_dict(classifier):
    result = _service(classifier).route(
        "There is a dangerous water leak, it is urgent.", received=date(2026, 1, 5)
    )
    assert result["priority"] == "high"
    assert result["department"] == "infrastructure"


def test_api(classifier):
    import pqrs_router.main as main

    main._service = _service(classifier)
    client = TestClient(main.app)

    assert client.get("/health").json() == {"status": "ok"}

    resp = client.post(
        "/route",
        json={
            "text": "I want to complain about the rude treatment by an agent.",
            "received_date": "2026-01-05",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["request_type"] == "complaint"
    assert body["department"] == "customer_service"

    bad = client.post("/route", json={"text": "x", "received_date": "not-a-date"})
    assert bad.status_code == 422

    assert client.post("/route", json={"text": ""}).status_code == 422
