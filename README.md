# pqrs-router

An intake router for citizen requests. It reads an incoming message, classifies
it into a PQRS type (petition, complaint, claim, suggestion, report) and a target
department, assigns a priority, and computes the statutory response deadline — a
single, explainable routing decision ready to drop into a public-sector workflow.

PQRS (Petición, Queja, Reclamo, Sugerencia) is the standard public-service intake
model across much of Latin America, where each request type carries a legal
response window. pqrs-router turns a free-text message into the structured
decision an agency needs to act on it in time.

## Why it matters

Public bodies receive large volumes of unstructured requests and are legally
bound to answer each one within a set period. Misrouting or missing a deadline
has real consequences. pqrs-router automates the triage:

- **Classify.** What kind of request is this, and which department owns it?
- **Prioritise.** How urgent is it — does it mention safety, health, an outage,
  fraud, or a vulnerable person?
- **Schedule.** By when must it be answered, counting only business days?
- **Explain.** Every decision carries the words that drove the classification and
  the reasons for the priority, and a low-confidence classification is flagged for
  manual triage rather than routed blindly.

No LLM and no network: the classifiers are small, fast, deterministic linear
models, which is the right tool for high-volume, auditable routing.

## How it works

```
 request text        classify (ML)         rules                 decision
 ────────────   ──────────────────────  ─────────────────   ──────────────────
 free message ─▶ type + department   ─▶ priority (urgency) ─▶ route + priority +
                 (TF-IDF + logistic)     + SLA deadline        due date + reasons
                                         (business days)
```

1. **Classify (`classifier.py`).** Two logistic-regression models over a shared
   TF-IDF vectoriser predict the request type and the department, each with a
   confidence and the terms that drove the type decision.
2. **Rules (`rules.py`).** Priority starts from the request type and is raised to
   high when the text carries urgency. The deadline is the type's statutory window
   counted in business days from the received date.
3. **Route (`router.py`).** The two are combined into a `RoutingDecision`; a
   type confidence below the threshold marks the request uncertain for manual
   triage.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Classify and route a few sample requests:
python -m pqrs_router.cli demo

# Route one request:
python -m pqrs_router.cli route "I demand a correction of an incorrect charge."

# Run the HTTP API:
uvicorn pqrs_router.main:app --reload
```

Example API call:

```bash
curl -s -X POST localhost:8000/route -H 'content-type: application/json' -d '{
  "text": "There is a dangerous water leak on my street, it is urgent.",
  "received_date": "2026-01-05"
}'
```

## Configuration

Settings load from environment variables with the `PQ_` prefix (see
`.env.example`):

| Variable           | Default | Meaning                                              |
| ------------------ | ------- | ---------------------------------------------------- |
| `PQ_MIN_CONFIDENCE`| `0.45`  | Below this type confidence, flag for manual triage   |

The statutory response windows per request type live in `taxonomy.py`
(`SLA_BUSINESS_DAYS`); set them from the governing law for a real deployment.

## Testing

```bash
ruff check pqrs_router tests
pytest --cov=pqrs_router --cov-report=term-missing --cov-fail-under=80
```

The suite covers the classifiers (including a held-out accuracy check), the rules
(business-day arithmetic, per-type SLAs, priority and urgency), the router
(including the uncertainty flag), the HTTP API, and the CLI.

## Documentation

- `docs/architecture.md` — the full picture and the data flow.
- `docs/adr/` — the main design decisions and why they were made.
- `docs/estudio/` — a study guide in Spanish, for learning the project in depth.

## License

MIT. See [LICENSE](LICENSE).
