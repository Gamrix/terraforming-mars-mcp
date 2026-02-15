# Terraforming Mars Postmortem
## Game: `https://terraforming-mars.herokuapp.com/player?id=pdffaae63e575`
## Date: 2026-02-15

## 1) Executive Summary

- Final result: **John (Blue) 145 - Codex (Red) 97**
- Margin: **48 VP**
- Ended in **Generation 12** (full game length)
- Core story: we won board/greenery lanes, but lost hard in **card VP and engine conversion**.

John's game plan was coherent from early-mid game onward:
1. Build discount stack and premium economy.
2. Turn that economy into high-VP cards.
3. Add city adjacency on top.

Our plan (Ecoline tempo + board pressure) produced real points, but not enough ceiling.

## 2) Score Decomposition

### Final VP Breakdown

| Category | Codex | John | Delta (John - Codex) |
|---|---:|---:|---:|
| TR | 50 | 53 | +3 |
| Milestones | 10 | 5 | -5 |
| Awards | 5 | 10 | +5 |
| Greenery | 16 | 1 | -15 |
| City | 11 | 18 | +7 |
| Card VP | 5 | 58 | +53 |
| **Total** | **97** | **145** | **+48** |

### Interpretation

- We dominated greenery points (+15 swing).
- We held milestone edge (+5 swing).
- John overwhelmed with **Card VP (+53 swing)**, plus city value and awards.
- The game was decided primarily by **engine-to-VP conversion**, not terraforming pace alone.

## 3) Terraforming Timeline

From `globalsPerGeneration`:

- Gen 1: Temp -28, O2 0, Oceans 0
- Gen 2: Temp -28, O2 2, Oceans 0
- Gen 3: Temp -28, O2 2, Oceans 0
- Gen 4: Temp -24, O2 3, Oceans 0
- Gen 5: Temp -20, O2 4, Oceans 0
- Gen 6: Temp -14, O2 5, Oceans 0
- Gen 7: Temp -8, O2 8, Oceans 1
- Gen 8: Temp -6, O2 10, Oceans 1
- Gen 9: Temp 4, O2 11, Oceans 2
- Gen 10: Temp 8, O2 14, Oceans 4
- Gen 11: Temp 8, O2 14, Oceans 7
- Gen 12: Temp 8, O2 14, Oceans 9 (end)

### What this says

- Temperature and oxygen were effectively solved by Gen 10.
- Oceans lagged and completed at Gen 12.
- This was not a true short rush finish; it became a full-length game where deep engines are favored.

## 4) Strategy Identity by Player

## Codex (Red): Ecoline Board/Plant Tempo

Primary lanes:
- Plant production and greenery conversion.
- Milestone pressure (`Terraformer`, `Gardener`).
- Landlord award capture and map control.

Key positives:
- 16 greenery VP is very strong.
- 10 milestone VP is strong.
- Landlord funded and won.

Key weakness:
- Card VP package never reached parity.
- We ended with only +5 card VP and also carried -7 negative VP from cards.

## John (Blue): Helion Space/Science/Jovian Engine

Primary lanes:
- Space discounts and resource-value upgrades (`Space Station`, `Mass Converter`, `Anti-Gravity Technology`, `Advanced Alloys`).
- Premium space/Jovian economy into high VP card base.
- City scoring on top of card VP foundation.

Result:
- 58 card VP (massive).
- 18 city VP.
- 53 TR despite not playing a pure rush game.

## 5) Why John Won (Ranked)

1. **Card VP asymmetry (+53 swing)**
- This alone exceeded the final margin.
- Even if we improved cities/awards, this is the core losing axis.

2. **City network advantage (+7 swing)**
- John's city placement converted board state into efficient VP.
- We had only 3 cities by endgame.

3. **Awards split (+5 for John)**
- We locked Landlord, but John took Scientist and Thermalist.
- Their engine naturally supported those awards.

4. **Comparable TR despite our board focus (+3 for John)**
- We did not offset engine scaling with a TR lock.
- John still reached 53 TR while outscoring cards/cities.

5. **Long game length (Gen 12)**
- Full-length games are where card VP engines cash hardest.
- Our approach needed either faster closure or higher VP ceiling.

## 6) Midgame Structural Diagnosis

This was not lost in one late misclick. The loss was structural by late midgame.

Signals that the game was drifting to engine-favored territory:
- John assembled multiple permanent discounts.
- John stacked science and Jovian tags early enough to unlock top-end cards.
- We accumulated board value but not enough scalable card value.

At that point, winning required one of:
1. Force earlier closure.
2. Deny key VP cards/lanes.
3. Add a second scoring engine (city/card VP) earlier.

We did not accomplish enough of those three.

## 7) Endgame Audit (Our Final Sequence)

What we did in final generation:
1. Used `AI Central` to draw 2 cards.
2. Standard Project City at `47`.
3. `Electro Catapult` for +7 MC (plant payment).
4. Sold full hand for liquidity.
5. Standard Project City at `18`.
6. Passed.
7. Final greenery from plants at `56`.

Quality of this sequence:
- Tactically reasonable given available cash and board.
- We converted stranded hand value into board VP.
- We avoided wasting the final greenery placement.

But this sequence can only recover small tactical margins, not a 40+ VP structural deficit.

## 8) Counterfactuals and Estimated Swing

Realistic, not fantasy assumptions:

1. **Deny Builder milestone** (if claim timing had been reachable earlier)
- Swing estimate: up to **10 VP** (we gain 5, John loses 5).
- Caveat: timing feasibility uncertain without full action log.

2. **Earlier city pivot (1 additional efficient city/greenery cycle)**
- Swing estimate: **4 to 8 VP**.
- Depends on adjacency map and action windows.

3. **Reduce negative-VP card burden by 1-2 points**
- Swing estimate: **1 to 2 VP**.

4. **Award funding changes**
- Limited realistic upside here; Scientist and Thermalist were hard for us to win.

Even optimistic additive recovery is around 15-20 VP, still short of 48.

Conclusion: this game was primarily a **midgame strategic gap**, not an endgame tactical blunder.

## 9) Specific Card-Level Drivers

## John's biggest VP cards

- `Fish`: 12 VP
- `Physics Complex`: 10 VP
- `Ganymede Colony`: 6 VP
- `Io Mining Industries`: 6 VP
- Plus broad tail of 1-4 VP cards from science/space/jovian shell

This is exactly the profile of a winning long-game engine: many independent VP streams plus compounding discounts.

## Our card-level profile

Positive:
- `Herbivores`: 4 VP
- `Ecological Zone`: 3 VP
- Several +1 VP cards

Negative:
- `Nuclear Zone`: -2 VP
- `Corporate Stronghold`: -2 VP
- `Energy Tapping`, `Heat Trappers`, `Indentured Workers`: each -1 VP

Net card scoring was too thin against a science/space VP stack.

## 10) Early Rush Decision Review

Question: should we have fully committed to rush earlier?

Answer: **Yes, but only if we could actually shorten to Gen 9-10.**

In this game, we did not shorten enough. Once the game pace drifted to Gen 12, the burden shifted to building equivalent VP ceiling, and we did not pivot hard enough into that lane.

So the issue was not "rush is bad"; it was:
- rush commitment was incomplete,
- and pivot timing into secondary scoring came too late.

## 11) Playbook Updates for Next Match

1. **Rush viability gate by Gen 3-4**
- If projected finish is Gen 11-12, immediately add a second VP engine.
- Do not remain single-lane board/TR focused.

2. **Milestone denial as a first-class objective**
- If opponent is racing `Builder`, decide earlier whether to contest or concede.
- Avoid ambiguous middle lines.

3. **Track card VP ceiling explicitly**
- By Gen 6, estimate opponent card VP trajectory.
- If opponent projects 35+ card VP, prioritize disruption/closure or mirror with your own VP engine.

4. **Discount stack threat model**
- When opponent has 4+ effective discount on core card class (space/science), assume late-game explosion.
- Adjust tempo plan immediately.

5. **Endgame liquidation rule**
- Selling hand in final gen is correct only when it directly funds immediate VP actions.
- This game fit that rule; keep using it selectively.

## 12) Concrete Plan for Next Similar Pairing (Ecoline vs Helion Engine)

Early game:
- Keep plant tempo, but secure one scalable VP lane by Gen 4-5.
- Deny easy setup spaces that amplify opponent city scoring.

Mid game:
- Decide: hard rush close or hybrid pivot.
- If hard close not feasible, start city-card VP conversion immediately.

Late game:
- Prioritize actions with immediate VP delta over production.
- Keep one eye on final greenery math every generation.

## 13) Final Diagnosis

John won because his deck and sequencing converted economy into points at a far higher rate in a full-length game.

We played a competent board-tempo game and recovered reasonable endgame value, but we did not create enough scalable card VP to survive a mature science/space/jovian engine.

Primary takeaway:
- In long games, **board VP alone is not enough** against a high-efficiency card VP engine.
- Next time, either close earlier or pivot earlier.
