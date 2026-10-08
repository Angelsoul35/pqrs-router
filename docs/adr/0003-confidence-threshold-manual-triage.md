# ADR 0003: A confidence threshold that routes to manual triage

## Status

Accepted.

## Context

A classifier will sometimes be unsure — an unusual message, a mix of concerns, or
phrasing far from anything it has seen. Routing such a request on a weak guess can
send it to the wrong department and burn part of a legal deadline before the error
is noticed. But refusing to act on everything uncertain would defeat the purpose.

## Decision

Use the type classifier's **confidence**. When it is below a configured threshold
(`PQ_MIN_CONFIDENCE`), mark the decision `uncertain` so the request is sent to a
human for manual triage — while still providing the predicted department, the
priority, and the deadline so the triage starts from a useful draft rather than a
blank form.

## Consequences

- **Weak guesses do not route silently.** A low-confidence type becomes an
  explicit "a human should decide", not a wrong automatic route.
- **Still helpful when unsure.** The department guess, the urgency-based priority,
  and the computed deadline accompany the flag, so manual triage is faster.
- **Tunable per agency.** The threshold is a single configurable number, trading
  automation against safety.
- **Trade-off.** Some confidently-correct classifications just below the threshold
  will be sent to triage unnecessarily, and some confident-but-wrong ones above it
  will still route automatically. The threshold is where an agency sets that
  balance; the urgency rules act regardless of it, so an urgent request is never
  down-prioritised just because its type was uncertain.
