# ADR 0004: Deadlines in business days per request type

## Status

Accepted.

## Context

Public bodies must answer each request within a legal window, and those windows
differ by request type. Crucially, the windows are almost always counted in
**business days**, not calendar days — a deadline that lands on a weekend, or that
ignores weekends, is wrong and can breach the law.

## Decision

Store the statutory window per request type as **business days** in
`SLA_BUSINESS_DAYS`, and compute the due date by adding that many business days to
the received date, skipping Saturdays and Sundays (`add_business_days`). The due
date and the window length travel with the routing decision.

## Consequences

- **Legally meaningful deadlines.** The computed date reflects how the law
  actually counts time, so the deadline is one an agency can rely on.
- **Per-type correctness.** A suggestion (30 days) and a report (10 days) get
  different, correct deadlines from the same mechanism.
- **Transparent.** The decision reports both the due date and the number of
  business days, so the basis is visible.
- **Trade-off.** The current calendar skips weekends but not public holidays, and
  holidays vary by country and year. `add_business_days` is the single, obvious
  place to add a holiday calendar; keeping it isolated means that extension does
  not touch anything else. The windows themselves are data, set from the governing
  law per deployment rather than hard-coded assumptions.
