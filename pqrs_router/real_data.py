"""Real citizen-request text for benchmarking the classifier.

The bundled training data (:mod:`pqrs_router.generate`) is synthetic templated text,
which is ideal for a leakage-free phrase-disjoint evaluation but is not real intake.
This module adds the other half: a **real**, large public corpus of free-text
complaints — the U.S. Consumer Financial Protection Bureau (CFPB) consumer-complaint
narratives, via the Hugging Face ``fathyshalab/complaints`` mirror — labelled by the
financial *product* the complaint is about. Routing a real narrative to the right
product category is the same shape of task as routing a request to the right
department, so it measures whether the classifier's approach (word + char TF-IDF +
logistic regression) generalises on messy, real-world language.

A balanced subset is vendored under ``datasets/complaints_real.jsonl``;
``fetch_complaints`` refreshes it.
"""

from __future__ import annotations

import json
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_DATASET_PATH = _REPO_ROOT / "datasets" / "complaints_real.jsonl"

_DS = "fathyshalab%2Fcomplaints"
_ROWS = (
    "https://datasets-server.huggingface.co/rows?dataset={ds}"
    "&config=default&split=train&offset={off}&length=100"
)


def load_complaints(path: str | Path | None = None) -> tuple[list[str], list[str], list[str]]:
    """Return ``(texts, labels, label_names)`` for the vendored real complaints."""
    target = Path(path) if path is not None else _DATASET_PATH
    if not target.exists():
        raise FileNotFoundError(
            f"Vendored complaints not found at {target}. Refresh with "
            "pqrs_router.real_data.fetch_complaints()."
        )
    texts: list[str] = []
    labels: list[str] = []
    for line in target.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        texts.append(row["text"])
        labels.append(row["product"])
    label_names = sorted(set(labels))
    return texts, labels, label_names


def fetch_complaints(
    path: str | Path | None = None,
    per_class: int = 300,
    target_classes: int = 10,
    min_len: int = 40,
    max_len: int = 600,
) -> int:
    """Download a balanced real subset of CFPB complaints into the vendored JSONL.

    Pages the Hugging Face datasets-server, buckets by product, keeps the most-filled
    classes that reach ``per_class``. Returns the number of rows written.
    """
    import time
    import urllib.request
    from collections import defaultdict

    target = Path(path) if path is not None else _DATASET_PATH

    def get(off: int, tries: int = 5) -> dict:
        url = _ROWS.format(ds=_DS, off=off)
        for i in range(tries):
            try:
                with urllib.request.urlopen(url, timeout=60) as resp:
                    return json.load(resp)
            except Exception:  # noqa: BLE001 - network retry
                if i == tries - 1:
                    raise
                time.sleep(2**i)
        return {}

    buckets: dict[str, list[str]] = defaultdict(list)
    off = 0
    while off < 60000:
        rows = get(off).get("rows", [])
        if not rows:
            break
        for row in rows:
            r = row["row"]
            product = (r.get("Product") or "").strip()
            text = (r.get("text") or "").strip()
            if not product or len(text) < min_len:
                continue
            if len(buckets[product]) < per_class:
                buckets[product].append(text[:max_len])
        off += 100
        if sum(1 for v in buckets.values() if len(v) >= per_class) >= target_classes:
            break

    ranked = sorted(buckets.items(), key=lambda kv: len(kv[1]), reverse=True)
    keep = [(p, v) for p, v in ranked if len(v) >= per_class][:target_classes]

    target.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with open(target, "w") as f:
        for product, texts in keep:
            for text in texts[:per_class]:
                f.write(json.dumps({"text": text, "product": product}) + "\n")
                n += 1
    return n
