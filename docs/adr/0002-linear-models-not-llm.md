# ADR 0002: Linear classifiers, not an LLM

## Status

Accepted.

## Context

Request classification could be done with a large language model. But this system
runs at the intake of a public body: potentially high volume, latency-sensitive,
cost-sensitive, and subject to audit. Every routing decision may need to be
justified to a citizen or an oversight body.

## Decision

Classify with **TF-IDF features and logistic regression** — small, linear models
— rather than an LLM.

## Consequences

- **Fast and cheap.** Classification is microseconds and costs nothing per
  request, which matters at intake volumes.
- **Deterministic.** The same message always routes the same way, so behaviour is
  reproducible and testable.
- **Explainable.** A linear model's decision is a weighted sum of words; the top
  contributing terms are the explanation, with no extra machinery.
- **No external dependency.** No API key, no network, no provider outage to handle
  at a critical intake point.
- **Trade-off.** Linear models are less robust to very unusual phrasing than a
  large model. Two things mitigate this: the confidence threshold routes
  low-confidence messages to a human (see ADR 0003), and the `classify` interface
  lets a stronger model be slotted in later if evidence shows it is needed. For
  the common, templated phrasing of citizen requests, the linear models are both
  accurate and the responsible default.
