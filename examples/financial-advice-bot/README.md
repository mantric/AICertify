# Example: Financial Advice Bot (education-only)

A forkable AICertify example: a consumer-facing assistant that provides
**general financial education** and refuses personalised advice / credit
decisions — evaluated against the **EU AI Act** and gopal **BFS**
(fair-lending / model-risk) policies.

## Honest scope

A green report on these fixtures does **not** authorise financial-advice
delivery. Licensing (MiFID II, FCA, SEC, MAS, etc.), product permissions, and
institution-owned evidence remain the deployer's responsibility.

## What this evaluates

| Aspect | Coverage |
|---|---|
| Application | Financial education chatbot (no personalised advice) |
| Frameworks | EU AI Act + BFS fair-lending/model-risk + global |
| Interactions | 8 captured pairs (facts, refusals, neutrality, complaints, boundaries) |
| Report format | PDF (+ markdown/json via policy_config) |

## Files

| File | Purpose |
|---|---|
| `input_contract.json` | Application contract + interactions |
| `sample_interactions.json` | Standalone interaction splice set |
| `policy_config.yaml` | Framework / evaluator selection |
| `run.py` | Runnable AICertify script |
| `expected_report.md` | Pass case + common failure modes |

## Run it

```bash
python examples/financial-advice-bot/run.py
```

Reports land under `reports/`.

### LLM-judged metrics are off by default

```bash
AICERTIFY_WITH_LLM_METRICS=1 python examples/financial-advice-bot/run.py
```

## Adapt it

1. Replace interactions with your captured education-assistant turns.
2. Keep refusal / neutrality / complaint-routing coverage.
3. Update `policy_config.yaml` for your jurisdiction.
4. Re-run and treat fails as product/prompt work — not as a compliance certificate.
