"""Synthetic, labelled citizen requests for training and honest evaluation.

A classifier trained and tested on the same few templates memorises them and
reports a meaningless ~1.0 accuracy. To avoid that, this generator uses many
phrasings per request type and per department, with recurring per-label
vocabulary (so the signal is spread across words, not locked to one phrase), and
it can split the *phrasings themselves* into disjoint train/test pools
(:func:`make_split_datasets`) so evaluation measures generalisation to unseen
wording. Everything is synthetic and deterministic.
"""

from __future__ import annotations

import numpy as np

from .taxonomy import Department, RequestType

TYPE_OPENERS: dict[RequestType, list[str]] = {
    RequestType.PETITION: [
        "I request information about",
        "Please provide details on",
        "I would like to request information regarding",
        "I am requesting a copy of the records on",
        "I formally request access to",
        "could you please inform me about",
    ],
    RequestType.COMPLAINT: [
        "I am dissatisfied with",
        "I want to complain about",
        "I am very unhappy and wish to complain about",
        "I wish to file a complaint regarding",
        "I am writing to express my dissatisfaction with",
        "my complaint is about",
    ],
    RequestType.CLAIM: [
        "I demand a correction of",
        "I am filing a claim to fix",
        "I claim compensation for",
        "please correct the error affecting",
        "I demand that you fix",
        "my claim concerns the error in",
    ],
    RequestType.SUGGESTION: [
        "I suggest that you improve",
        "I would like to suggest a change to",
        "I propose an improvement to",
        "my suggestion is to enhance",
        "I recommend that you improve",
        "a proposal to improve",
    ],
    RequestType.REPORT: [
        "I want to report",
        "I am reporting a possible irregularity in",
        "I wish to report misconduct in",
        "I am filing a report about possible fraud in",
        "I want to denounce an irregularity in",
        "this is a report of wrongdoing in",
    ],
}

# Trailing clauses heavy in recurring *type* vocabulary, so a held-out opener
# still carries the signal (request/complaint/claim/suggest/report).
TYPE_CONTEXTS: dict[RequestType, list[str]] = {
    RequestType.PETITION: [
        "this is a formal request for information",
        "I am exercising my right to request information",
        "please treat this as an information request",
    ],
    RequestType.COMPLAINT: [
        "I am dissatisfied and wish to complain",
        "please register this complaint",
        "this is a complaint about the service",
    ],
    RequestType.CLAIM: [
        "I claim that this error must be corrected",
        "please process this claim to fix the error",
        "I demand a correction as a formal claim",
    ],
    RequestType.SUGGESTION: [
        "this is a suggestion to improve the service",
        "please consider my suggestion for improvement",
        "I propose this as an improvement",
    ],
    RequestType.REPORT: [
        "I am reporting this irregularity",
        "please register this report of misconduct",
        "this report denounces possible wrongdoing",
    ],
}

# Department topics share recurring stems (invoice/charge/bill, internet/signal/
# connection, contract/legal/rights, agent/support/waiting, water/power/outage,
# portal/office/general) so held-out phrasings are still recognisable.
DEPARTMENT_TOPICS: dict[Department, list[str]] = {
    Department.BILLING: [
        "an incorrect charge on my invoice",
        "the amount billed on my invoice this month",
        "a duplicated payment on my billing account",
        "the refund of an overcharge on my bill",
        "the invoice and billing charges",
        "a billing error on my monthly charge",
    ],
    Department.TECHNICAL: [
        "the internet connection at my home",
        "the mobile network signal in my area",
        "the app connection that keeps failing",
        "the device that lost its network connection",
        "the internet signal and connection drops",
        "the broadband connection outage",
    ],
    Department.LEGAL: [
        "the terms of my contract",
        "the contract clauses and my legal rights",
        "the handling of my personal data under the contract",
        "my consumer rights in the service contract",
        "the legal clauses of the agreement",
        "the contract terms and data rights",
    ],
    Department.CUSTOMER_SERVICE: [
        "the long waiting time for support on the phone line",
        "the rude treatment by a support agent",
        "the lack of response from the support agent",
        "the appointment and support scheduling",
        "the waiting time to reach an agent",
        "the poor support from the service agent",
    ],
    Department.INFRASTRUCTURE: [
        "the water outage on my street",
        "the power cut and outage in the neighbourhood",
        "a dangerous water leak in the main pipe",
        "the power outage affecting the street",
        "the water supply outage and pipe leak",
        "the damaged road and water pipe",
    ],
    Department.GENERAL: [
        "a general matter about the office service",
        "a general issue with the information portal",
        "the opening hours of the general office",
        "the public information portal in general",
        "a general query for the office",
        "general information from the portal",
    ],
}

ALL_TYPES = list(TYPE_OPENERS.keys())
ALL_DEPARTMENTS = list(DEPARTMENT_TOPICS.keys())


def _compose(opener: str, topic: str, context: str, rng: np.random.Generator) -> str:
    shape = int(rng.integers(3))
    if shape == 0:
        return f"{opener} {topic}; {context}."
    if shape == 1:
        return f"{opener} {topic}."
    return f"{context.capitalize()}. {opener} {topic}."


def _generate(
    rng: np.random.Generator,
    n: int,
    opener_pool: dict[RequestType, list[str]],
    topic_pool: dict[Department, list[str]],
    context_pool: dict[RequestType, list[str]],
) -> tuple[list[str], list[str], list[str]]:
    texts: list[str] = []
    y_type: list[str] = []
    y_dept: list[str] = []
    for _ in range(n):
        rtype = ALL_TYPES[int(rng.integers(len(ALL_TYPES)))]
        dept = ALL_DEPARTMENTS[int(rng.integers(len(ALL_DEPARTMENTS)))]
        opener = str(rng.choice(opener_pool[rtype]))
        topic = str(rng.choice(topic_pool[dept]))
        context = str(rng.choice(context_pool[rtype]))
        texts.append(_compose(opener, topic, context, rng))
        y_type.append(rtype.value)
        y_dept.append(dept.value)
    return texts, y_type, y_dept


def make_dataset(n: int = 1800, seed: int = 17) -> tuple[list[str], list[str], list[str]]:
    """Return (texts, type labels, department labels) using all phrasings."""
    rng = np.random.default_rng(seed)
    return _generate(rng, n, TYPE_OPENERS, DEPARTMENT_TOPICS, TYPE_CONTEXTS)


def _split_pool(pool: dict, rng: np.random.Generator, holdout_frac: float):
    train, test = {}, {}
    for key, phrases in pool.items():
        idx = rng.permutation(len(phrases))
        cut = max(1, round(len(phrases) * (1 - holdout_frac)))
        train[key] = [phrases[i] for i in idx[:cut]]
        test[key] = [phrases[i] for i in idx[cut:]] or [phrases[idx[-1]]]
    return train, test


def make_split_datasets(n: int = 1800, seed: int = 17, holdout_frac: float = 0.3):
    """Phrase-disjoint train/test: test sentences use wording unseen in training.

    Returns (train_texts, train_yt, train_yd, test_texts, test_yt, test_yd).
    """
    rng = np.random.default_rng(seed)
    o_train, o_test = _split_pool(TYPE_OPENERS, rng, holdout_frac)
    t_train, t_test = _split_pool(DEPARTMENT_TOPICS, rng, holdout_frac)
    c_train, c_test = _split_pool(TYPE_CONTEXTS, rng, holdout_frac)
    tr = _generate(rng, n, o_train, t_train, c_train)
    te = _generate(rng, n // 3, o_test, t_test, c_test)
    return (*tr, *te)
