# Post-Game Improvement Notes (2026-02-14)

Game result reference:
- Codex 72 VP vs John 112 VP
- Biggest deficits were TR, card VP, and awards

## What To Do Better Next Time

1. Commit to a game plan earlier.
- By Generation 6, choose one path: `engine` or `rush`.
- If behind on production/card quality by midgame, pivot hard to terraforming rush and game-end pressure.

2. Stop funding awards when trailing.
- Do not fund an award unless projection says at least 2nd place.
- Treat award funding as a point investment, not a tempo move.

3. Prioritize endgame timing over medium-value setup.
- When oxygen reaches 9-10 and temperature is close to max, shift to finishing lines.
- Prefer actions that immediately increase TR or lock board VP.

4. Draft with a stricter ROI filter.
- Buy fewer speculative cards in late generations.
- Prefer direct VP/TR cards over cards that need multiple future turns to pay back.

5. Improve city and greenery conversion efficiency.
- Place cities only where expected greenery adjacency is realistic.
- Avoid city placements that are hard to capitalize with later greenery.

6. Play stronger denial when behind.
- Draft/hold cards that cut opponent production or block their award/milestone race.
- Deny key categories the opponent is clearly leading (banking, science, etc.).

7. Avoid negative-VP/low-impact late plays unless they force tempo.
- In final generations, every card must clearly convert to points or deny opponent points.
- Skip low-ceiling tempo cards that do not change final scoring math.

8. Execute cleaner through MCP flow constraints.
- In `choose_or_option` + `projectCard`, always send full payment object fields.
- Precompute payment exactly once to avoid retries/timeouts.
- If a card appears playable but rejects (e.g. unknown name), pivot immediately instead of re-attempting multiple times.

## Simple In-Game Checklist

- Gen 1-3: build economy only if ROI is strong and fast.
- Gen 4-6: decide `engine` vs `rush` and commit.
- Gen 7+: if behind, accelerate game end and deny opponent scaling.
- Before funding award: verify likely placement.
- Before buying card: ask “Does this score before game end?”
- Before action: choose highest immediate VP/TR impact.
