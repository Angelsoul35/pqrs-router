"""The PQRS vocabulary: request types, departments, priorities, and the SLAs.

PQRS is the standard public-sector intake model in much of Latin America:
Petición, Queja, Reclamo, Sugerencia (plus a Denuncia / report). Each type has a
statutory response window, counted in business days, which drives the deadline.
"""

from __future__ import annotations

from enum import StrEnum


class RequestType(StrEnum):
    PETITION = "petition"  # petición: a request for information or action
    COMPLAINT = "complaint"  # queja: dissatisfaction with conduct or service
    CLAIM = "claim"  # reclamo: a demand to fix a specific failure
    SUGGESTION = "suggestion"  # sugerencia: an improvement proposal
    REPORT = "report"  # denuncia: a report of a possible irregularity


class Department(StrEnum):
    BILLING = "billing"
    TECHNICAL = "technical"
    LEGAL = "legal"
    CUSTOMER_SERVICE = "customer_service"
    INFRASTRUCTURE = "infrastructure"
    GENERAL = "general"


class Priority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# Statutory response window per request type, in business days. These are
# illustrative defaults; a real deployment sets them from the governing law.
SLA_BUSINESS_DAYS: dict[RequestType, int] = {
    RequestType.PETITION: 15,
    RequestType.COMPLAINT: 15,
    RequestType.CLAIM: 15,
    RequestType.SUGGESTION: 30,
    RequestType.REPORT: 10,
}

# Words that raise urgency regardless of request type.
URGENCY_TERMS: tuple[str, ...] = (
    "urgent",
    "emergency",
    "immediately",
    "danger",
    "dangerous",
    "safety",
    "health",
    "no water",
    "no power",
    "outage",
    "leak",
    "elderly",
    "disabled",
    "minor",
    "child",
    "fraud",
)
