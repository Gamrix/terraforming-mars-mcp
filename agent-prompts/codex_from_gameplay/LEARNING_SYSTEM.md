# Gameplay Learning System

This workflow turns each finished game into reusable strategy updates.

The main goal is no longer just to describe why a game was lost.
The goal is to force behavior change in future games.

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
- Standing pre-game improvement protocol:
`agent-prompts/codex_from_gameplay/NEXT_GAME_PROTOCOL.md`

## Per-Game Workflow

1. Before the next game, read `NEXT_GAME_PROTOCOL.md` and commit to its checkpoints.
2. Write full postmortem using the template.
3. Create one JSON summary from the template.
4. Append summary to dataset and refresh rollup.
5. Compare the game against the active hypotheses and decide whether each one strengthened, weakened, or remained unresolved.

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
- Record the macro plan clearly enough that `hybrid` is not a content-free label.
- Include the midgame score forecast quality: did the in-game projection match the actual final category results?
- Include whether the endgame plan was scripted before execution or improvised in the moment.

## Structural Improvement Rules

Treat the learning system as a constrained experiment loop:

1. Use a small number of active hypotheses.
- Good example: "Earlier city anchors improve final city delta against John."
- Bad example: "Play better endgames."

2. Keep hypotheses falsifiable.
- Each hypothesis should imply a visible behavior change and an observable result.

3. Retire or revise weak rules.
- If a rule has been present across several games without improving outcomes, rewrite it or replace it.

4. Prioritize recurring category losses.
- If the dataset says losses are concentrated in `card_vp`, `city`, and awards, future rules should target those categories directly.

5. Separate strategic error from tooling error.
- Do not hide strategic mistakes inside tool narratives.
- A correct postmortem must say whether the loss was caused by evaluation, planning, execution, or tooling.

## Required Midgame Forecasting

Every postmortem and summary should explicitly reflect whether these were done in-game:

- Gen 3 macro call:
- `hard close`
- `hybrid leaning close`
- `outscale`

- Gen 6 forecast:
- self expected `TR`
- self expected `greenery + city`
- self expected `card_vp`
- opponent expected `card_vp`
- award expectation

- Gen 8 revision:
- whether the forecast changed
- whether the opponent hit a discount-stack or VP-ceiling alarm

- Gen 10+ liquidation plan:
- best board placement
- best direct VP line
- whether terraforming completion still allowed more actions

If these were not done during the game, mark them as process failures.

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

### Rules Interpretation Failure (2026-03-10, game `pc1b956cee5d1`)

- Mars was fully terraformed during the action phase, but the implementation still allowed the rest of the generation to continue.
- Treating that moment like an immediate end caused a major endgame conversion miss.
- Workaround: after any action that completes terraforming, always inspect the next prompt before passing and assume more liquidation may still be legal.
