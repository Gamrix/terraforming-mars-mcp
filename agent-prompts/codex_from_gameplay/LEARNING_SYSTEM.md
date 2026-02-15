# Gameplay Learning System

This workflow turns each finished game into reusable strategy updates.

## Files

- Template postmortem:
`agent-prompts/codex_from_gameplay/postmortem-template.md`
- Structured summary template:
`agent-prompts/codex_from_gameplay/game-summary-template.json`
- Taxonomy tags:
`agent-prompts/codex_from_gameplay/decision-taxonomy.md`
- Summary records folder:
`agent-prompts/codex_from_gameplay/game-summaries/`
- Persistent dataset:
`agent-prompts/codex_from_gameplay/game-learning-dataset.jsonl`
- Auto-generated rollup:
`agent-prompts/codex_from_gameplay/game-learning-rollup.md`
- Automation script:
`scripts/tm_learning.py`

## Per-Game Workflow

1. Write full postmortem using the template.
2. Create one JSON summary from the template.
3. Append summary to dataset and refresh rollup.

## Commands

Initialize a summary skeleton:

```bash
python3 scripts/tm_learning.py init-summary \
  --output agent-prompts/codex_from_gameplay/game-summaries/summary-YYYY-MM-DD-01.json \
  --game-url "https://terraforming-mars.herokuapp.com/player?id=..." \
  --game-date "YYYY-MM-DD"
```

Append one completed summary and regenerate rollup:

```bash
python3 scripts/tm_learning.py append \
  --summary agent-prompts/codex_from_gameplay/game-summaries/summary-YYYY-MM-DD-01.json
```

Regenerate rollup from dataset:

```bash
python3 scripts/tm_learning.py rollup
```

## Required Summary Quality

- Include `mistake_tags` using taxonomy names.
- Include at least one `counterfactual` with estimated VP swing.
- Include at least one concrete `rule_update`.
- Keep breakdown values consistent with final score.
