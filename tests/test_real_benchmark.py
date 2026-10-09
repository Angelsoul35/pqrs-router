"""Functional tests for the real CFPB-complaint benchmark.

They prove the vendored data is the real, balanced corpus, that the classifier's
approach generalises on real complaint text (held-out accuracy well above chance, a
regularisation path showing the gap is train-side, not wasted generalisation), and
that the signal is real (shuffling the labels collapses it to chance).
"""

from __future__ import annotations

import json

import numpy as np
import pytest

from pqrs_router.real_benchmark import RealBenchmarkReport, format_report, run_benchmark
from pqrs_router.real_data import load_complaints


@pytest.fixture(scope="module")
def data():
    texts, labels, names = load_complaints()
    return texts, labels, names


@pytest.fixture(scope="module")
def report(data):
    texts, labels, _ = data
    return run_benchmark((texts, labels))


def test_loads_the_real_balanced_corpus(data):
    texts, labels, names = data
    assert len(texts) == len(labels) == 3000
    assert len(names) == 10  # ten product classes
    counts = {n: labels.count(n) for n in names}
    assert set(counts.values()) == {300}  # balanced, 300 per class
    assert all(isinstance(t, str) and t for t in texts)


def test_classifier_generalises_on_real_complaints(report):
    chance = report.chance
    assert report.cv_accuracy >= 5 * chance  # well above the 0.10 chance rate
    assert report.cv_accuracy <= 0.95
    assert report.test_accuracy >= 0.55
    assert report.test_macro_f1 >= 0.55
    assert report.verdict.startswith("well-fit")


def test_gap_is_train_side_not_overfitting(report):
    # Held-out accuracy barely moves across the regularisation path: the train/test
    # gap is memorisation of the training set, not wasted generalisation.
    assert len(report.reg_path) == 5
    assert report.test_stable_across_c
    tests = [t for _, _, t in report.reg_path]
    assert max(tests) - min(tests) <= 0.05


def test_shuffled_labels_collapse_to_chance(data):
    texts, labels, _ = data
    y = np.asarray(labels)
    shuffled = np.random.default_rng(1).permutation(y).tolist()
    r = run_benchmark((texts, shuffled))
    assert r.cv_accuracy <= 2 * r.chance  # near the 0.10 chance line
    assert not r.verdict.startswith("well-fit")


def test_verdict_branches():
    def rep(cv, shuf, chance=0.1):
        return RealBenchmarkReport(
            3000, int(1 / chance), chance, chance, cv, 0.02, cv, 0.99, cv - 0.01, cv - 0.01,
            shuf, [(0.2, 0.86, 0.67), (2.0, 0.99, 0.68)]
        )

    assert rep(0.20, 0.10).verdict.startswith("weak")  # 2x chance, too close
    assert rep(0.70, 0.40).verdict.startswith("leaky")  # shuffled didn't collapse
    assert rep(0.70, 0.10).verdict.startswith("well-fit")


def test_format_report_renders_the_path(report):
    text = format_report(report)
    assert "CFPB consumer complaints" in text
    assert "regularisation path" in text
    assert f"{report.cv_accuracy:.3f}" in text


def test_main_prints_the_report(capsys):
    from pqrs_router.real_benchmark import main

    main()
    assert "real-data benchmark" in capsys.readouterr().out


def test_loader_rejects_a_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_complaints(tmp_path / "nope.jsonl")


def test_fetch_buckets_and_balances(tmp_path, monkeypatch):
    import pqrs_router.real_data as rd

    # Three products; only two reach the per_class cap of 2.
    rows = [
        {"row": {"Product": "Mortgage", "text": "x" * 60}},
        {"row": {"Product": "Mortgage", "text": "y" * 60}},
        {"row": {"Product": "Mortgage", "text": "z" * 60}},  # capped at 2
        {"row": {"Product": "Debt collection", "text": "a" * 60}},
        {"row": {"Product": "Debt collection", "text": "b" * 60}},
        {"row": {"Product": "Student loan", "text": "short"}},  # too short, dropped
    ]
    calls = {"n": 0}

    def fake_urlopen(url, timeout=0):
        calls["n"] += 1
        body = {"rows": rows} if calls["n"] == 1 else {"rows": []}

        class _R:
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def read(self):
                return json.dumps(body).encode()

        return _R()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    dest = tmp_path / "c.jsonl"
    n = rd.fetch_complaints(dest, per_class=2, target_classes=2, min_len=40)
    assert n == 4  # two full classes x 2
    texts, labels, names = rd.load_complaints(dest)
    assert sorted(names) == ["Debt collection", "Mortgage"]
    assert labels.count("Mortgage") == 2 and labels.count("Debt collection") == 2
