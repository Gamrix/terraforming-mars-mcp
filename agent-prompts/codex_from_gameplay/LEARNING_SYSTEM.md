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

## Payload Format Notes

Use these exact payload shapes when `waiting_for.input_type` is `or`.

- Raw `or` wrapper (strict keys only):

```json
{
  "type": "or",
  "index": 2,
  "response": { "type": "option" }
}
```

- `or` -> `projectCard` branch (must use `card`, not `cards`; must include full `payment` object):

```json
{
  "type": "or",
  "index": 2,
  "response": {
    "type": "projectCard",
    "card": "Anti-Gravity Technology",
    "payment": {
      "megaCredits": 13,
      "steel": 0,
      "titanium": 0,
      "heat": 0,
      "plants": 0,
      "microbes": 0,
      "floaters": 0,
      "lunaArchivesScience": 0,
      "spireScience": 0,
      "seeds": 0,
      "auroraiData": 0,
      "graphene": 0,
      "kuiperAsteroids": 0
    }
  }
}
```

- `or` -> `card` branch:

```json
{
  "type": "or",
  "index": 1,
  "response": { "type": "card", "cards": ["Security Fleet"] }
}
```

- `card` prompt with `min=0,max=0` (for example Inventors' Guild when card cannot be bought):

```json
{ "type": "card", "cards": [] }
```

### Known Mismatch (2026-02-15, game `pedaac22da042`)

- `Open City` appeared in `waiting_for.options[*].detail.cards` and in hand, but `or -> projectCard` submit returned:
  - `HTTP 400 POST /player/input: Unknown card name Open City`
- This failed across multiple payload encodings (direct params and legacy `request` wrapper).
- Workaround used in-game: pivot to standard project city / other legal actions.
