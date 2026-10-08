from __future__ import annotations

import pytest

from pqrs_router.classifier import RequestClassifier
from pqrs_router.evaluation import phrase_disjoint_eval
from pqrs_router.taxonomy import Department, RequestType


def test_classify_complaint_to_customer_service(classifier):
    c = classifier.classify("I want to complain about the rude treatment by an agent.")
    assert c.request_type is RequestType.COMPLAINT
    assert c.department is Department.CUSTOMER_SERVICE
    assert c.top_terms


def test_classify_claim_to_billing(classifier):
    c = classifier.classify("I demand a correction of an incorrect charge on my invoice.")
    assert c.request_type is RequestType.CLAIM
    assert c.department is Department.BILLING


def test_unfitted_raises():
    with pytest.raises(RuntimeError):
        RequestClassifier().classify("anything")


def test_phrase_disjoint_generalisation_and_no_overfit():
    # Honest evaluation: train and test use disjoint pools of phrasings, so the
    # test wording is unseen. A random split would report a misleading ~1.0.
    report = phrase_disjoint_eval()
    # Not underfit: well above chance (type ~0.20, department ~0.17).
    assert report.type_accuracy >= 0.85
    assert report.department_accuracy >= 0.80
    # Not pathologically overfit: bounded train-test gaps.
    assert report.type_train_accuracy >= 0.95
    assert report.type_gap <= 0.15
    assert report.department_gap <= 0.20
