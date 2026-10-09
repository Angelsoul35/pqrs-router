# Datasets

## `complaints_real.jsonl` — real consumer complaints (CFPB)

A balanced real subset of the U.S. Consumer Financial Protection Bureau (CFPB)
consumer-complaint database, used to benchmark the classifier's approach on real,
free-text intake rather than only on synthetic templates (see *Validated on real
complaints* in the top-level README).

**Source.** The Hugging Face mirror
[`fathyshalab/complaints`](https://huggingface.co/datasets/fathyshalab/complaints) of
the public CFPB consumer-complaint narratives. Each record is a free-text complaint and
the financial **product** it is about.

**Why this fits.** pqrs-router routes a free-text request to a target department. The
real analogue is routing a real complaint narrative to the right product category — the
same word + char TF-IDF + logistic-regression pipeline, on messy real language.

**Contents.** 3,000 complaints, balanced at 300 each across the 10 most frequent product
categories. Note that the CFPB taxonomy changed over time, so some categories overlap
(e.g. *Credit reporting* vs *Credit reporting, credit repair services, or other personal
consumer reports*; *Credit card* vs *Credit card or prepaid card*). That overlap makes
the task genuinely hard — a realistic measure, not an inflated one.

| Field     | Meaning                                    |
| --------- | ------------------------------------------ |
| `text`    | the complaint narrative (truncated to 600 chars) |
| `product` | the CFPB product category (the label)      |

### Regenerating

```bash
python -c "from pqrs_router.real_data import fetch_complaints; print(fetch_complaints())"
```

Needs outbound access to `datasets-server.huggingface.co`. The CFPB data is a public
U.S. government record; the Hugging Face mirror's terms apply. This slice is vendored for
reproducible benchmarking only.
