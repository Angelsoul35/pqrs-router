from __future__ import annotations

import numpy as np
import pytest
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from pqrs_router.classifier import RequestClassifier
from pqrs_router.generate import make_dataset
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


def test_held_out_accuracy_is_high():
    texts, yt, yd = make_dataset(n=1200, seed=3)
    idx = np.arange(len(texts))
    tr, te = train_test_split(idx, test_size=0.25, random_state=0)
    clf = RequestClassifier().fit(
        [texts[i] for i in tr], [yt[i] for i in tr], [yd[i] for i in tr]
    )
    pt = [clf.classify(texts[i]).request_type.value for i in te]
    assert accuracy_score([yt[i] for i in te], pt) > 0.95
