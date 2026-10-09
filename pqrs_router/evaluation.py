"""Leakage-free evaluation of the request classifier.

Within-distribution accuracy on templated data is misleadingly high, so this
module trains on one pool of phrasings and tests on a *disjoint* pool: the test
messages use wording the model never saw. It reports type accuracy, department
accuracy, and the train/test gap (large gap = overfitting, low scores =
underfitting).

Run with ``python -m pqrs_router.evaluation``.
"""

from __future__ import annotations

from dataclasses import dataclass

from sklearn.metrics import accuracy_score

from .classifier import RequestClassifier
from .generate import make_split_datasets


@dataclass
class EvalReport:
    type_accuracy: float
    type_train_accuracy: float
    type_gap: float
    department_accuracy: float
    department_gap: float
    n_train: int
    n_test: int


def phrase_disjoint_eval(seed: int = 17, holdout_frac: float = 0.3) -> EvalReport:
    tr_texts, tr_yt, tr_yd, te_texts, te_yt, te_yd = make_split_datasets(
        seed=seed, holdout_frac=holdout_frac
    )
    clf = RequestClassifier().fit(tr_texts, tr_yt, tr_yd)

    def preds(texts):
        results = [clf.classify(t) for t in texts]
        return (
            [r.request_type.value for r in results],
            [r.department.value for r in results],
        )

    te_pt, te_pd = preds(te_texts)
    tr_pt, tr_pd = preds(tr_texts)

    type_acc = accuracy_score(te_yt, te_pt)
    type_train = accuracy_score(tr_yt, tr_pt)
    dept_acc = accuracy_score(te_yd, te_pd)
    dept_train = accuracy_score(tr_yd, tr_pd)
    return EvalReport(
        type_accuracy=round(float(type_acc), 3),
        type_train_accuracy=round(float(type_train), 3),
        type_gap=round(float(type_train - type_acc), 3),
        department_accuracy=round(float(dept_acc), 3),
        department_gap=round(float(dept_train - dept_acc), 3),
        n_train=len(tr_texts),
        n_test=len(te_texts),
    )


if __name__ == "__main__":
    r = phrase_disjoint_eval()
    print("Phrase-disjoint evaluation (test wording never seen in training):")
    print(f"  train / test size    : {r.n_train} / {r.n_test}")
    print(f"  type accuracy        : {r.type_accuracy}  (chance ~0.20)")
    print(f"  type train-test gap  : {r.type_gap}  (small = not overfit)")
    print(f"  department accuracy  : {r.department_accuracy}  (chance ~0.17)")
    print(f"  department gap       : {r.department_gap}")
