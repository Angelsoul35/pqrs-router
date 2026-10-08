# ADR 0001: Split learning from policy

## Status

Accepted.

## Context

A routing decision mixes two very different kinds of judgement:

- **What the request is** — its PQRS type and the department that owns it. This is
  a language-understanding problem.
- **How it must be handled** — its priority and its legal deadline. This is a
  policy problem with statutory weight.

Folding both into one learned model would make the deadlines and urgency policy
implicit in model behaviour: impossible to audit, and changed only by retraining.
Folding both into rules would make type/department classification brittle and
unable to generalise over phrasing.

## Decision

Keep the two separate:

- **Classification** (type, department) is **learned** from data with linear
  models.
- **Priority and deadlines** are **deterministic rules** encoded in `rules.py` and
  `taxonomy.py`, not learned.

The router combines their outputs into one decision.

## Consequences

- **Auditable policy.** The statutory windows and the urgency rules are explicit
  data and code; a lawyer or administrator can read and change them without ML.
- **Flexible classification.** The classifier can be retrained or replaced without
  touching the deadlines.
- **Clear responsibility.** When a decision is questioned, it is obvious whether
  the issue is a classification (the model) or a policy (the rules).
- **Trade-off.** Two mechanisms instead of one. The separation is worth it: the
  part with legal consequences stays deterministic and reviewable, and the part
  that benefits from learning stays learnable.
