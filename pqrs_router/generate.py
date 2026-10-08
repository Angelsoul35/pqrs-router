"""Synthetic, labelled citizen requests for training the classifier.

Each request is a short message a citizen might send, labelled with its PQRS type
and the department that should handle it. Built from type openers and
department-topic phrases, so it is realistic enough to learn from and fully
deterministic.
"""

from __future__ import annotations

import numpy as np

from .taxonomy import Department, RequestType

TYPE_OPENERS: dict[RequestType, list[str]] = {
    RequestType.PETITION: [
        "I request information about",
        "Please provide details on",
        "I would like to know about",
        "I am requesting a copy of",
    ],
    RequestType.COMPLAINT: [
        "I am dissatisfied with",
        "I want to complain about",
        "I am very unhappy with",
        "I wish to file a complaint regarding",
    ],
    RequestType.CLAIM: [
        "I demand a correction of",
        "I was wrongly affected by",
        "I am filing a claim for",
        "please fix the error in",
    ],
    RequestType.SUGGESTION: [
        "I suggest that you improve",
        "it would be better if you",
        "I propose a change to",
        "a recommendation to enhance",
    ],
    RequestType.REPORT: [
        "I want to report",
        "I am reporting a possible irregularity in",
        "there appears to be misconduct in",
        "I wish to denounce",
    ],
}

DEPARTMENT_TOPICS: dict[Department, list[str]] = {
    Department.BILLING: [
        "an incorrect charge on my invoice",
        "the amount billed this month",
        "a duplicated payment on my account",
        "the refund of an overcharge",
    ],
    Department.TECHNICAL: [
        "the internet connection at my home",
        "the mobile signal in my area",
        "the app that keeps crashing",
        "the device that stopped working",
    ],
    Department.LEGAL: [
        "the terms of my contract",
        "the handling of my personal data",
        "my rights as a consumer",
        "the clauses of the service agreement",
    ],
    Department.CUSTOMER_SERVICE: [
        "the long waiting time on the phone line",
        "the rude treatment by an agent",
        "the lack of response from support",
        "the appointment scheduling process",
    ],
    Department.INFRASTRUCTURE: [
        "the water outage on my street",
        "the power cut in the neighbourhood",
        "a dangerous leak in the main pipe",
        "the damaged road near the station",
    ],
    Department.GENERAL: [
        "a general matter about the service",
        "an issue not covered elsewhere",
        "the opening hours of the office",
        "the public information portal",
    ],
}

ALL_TYPES = list(TYPE_OPENERS.keys())
ALL_DEPARTMENTS = list(DEPARTMENT_TOPICS.keys())


def make_dataset(
    n: int = 1500, seed: int = 17
) -> tuple[list[str], list[str], list[str]]:
    """Return (texts, type labels, department labels)."""
    rng = np.random.default_rng(seed)
    texts: list[str] = []
    y_type: list[str] = []
    y_dept: list[str] = []
    for _ in range(n):
        rtype = ALL_TYPES[int(rng.integers(len(ALL_TYPES)))]
        dept = ALL_DEPARTMENTS[int(rng.integers(len(ALL_DEPARTMENTS)))]
        opener = str(rng.choice(TYPE_OPENERS[rtype]))
        topic = str(rng.choice(DEPARTMENT_TOPICS[dept]))
        texts.append(f"{opener} {topic}.")
        y_type.append(rtype.value)
        y_dept.append(dept.value)
    return texts, y_type, y_dept
