# Post-Mortem: Game 9 (Claude red vs John blue) — Tharsis, 2-player, Prelude, 12 gens

**Result: Lost 108–134 (–26 VP)** — second-closest margin (only Game 1's –2 was closer). Best structural game yet.

## Final Score Breakdown

| Category | Claude (red) | John (blue) |
|---|---|---|
| TR | 41 | 57 |
| Milestones | **15 (Mayor + Builder + Planner — FIRST SWEEP)** | 0 |
| Awards | 5 (Banker 1st, self-funded) | 10 (Miner + Scientist) |
| Greenery tiles | 8 | 13 |
| City adjacency | 15 | 22 |
| Card VP | 24 (27 – 3 negative) | 32 (36 – 4 negative) |
| **Total** | **108** | **134** |

## Corporations

- **Claude (Tharsis Republic)**: free city + MC prod per any city. + Self-Sufficient Settlement + Smelting Plant preludes.
- **John (Cheung Shing MARS)**: building discount + massive draw engine (AI Central, Restricted Area, Inventors' Guild, Business Contacts, SF Memorial) + plant mega-engine (Insects +6, NRA +4 → 15 plant prod).

## What Went RIGHT (breakthroughs)

### 1. MILESTONE SWEEP 15–0 (first ever)
- **Mayor gen 1**: Tharsis free city + SSS prelude city + Corporate Stronghold (enabled by Power Plant SP) = 3 cities gen 1, claimed same generation. Sold a dead card for the 8th MC.
- **Builder gen 5**: building tags accumulate naturally with Tharsis/steel play.
- **Planner gen 7**: my perpetually-bloated hand (17 cards) turned into 5 VP. Check Planner eligibility every gen — it's free VP for a draw-engine deck.
- Sweeping also CLOSED THE CAP on John: his TR 37+ never got Terraformer.

### 2. FIRST SELF-FUNDED AWARD WIN (Banker) + award-slot denial
- Funded Banker gen 10 at 22 vs 12 when **only one award slot remained** — this simultaneously locked my best category AND made Thermalist unfundable (John had 24 heat cubes + Mohole-style engine ready).
- John chased hard (Medical Lab +8, Cartel, Noctis City, Gene Repair → 32) — I defended by playing Capital, Space Hotels, Eos, Kelp Farming late (→ 40). **Defend a funded award with production plays, not hope.**
- Awards ended 5–10 instead of the usual 0–15.

### 3. City cluster planning worked
- Cities 40/42/54/46/51 + Capital 56 with shared greenery slots (41,47,48,49,50,53,55) — greenery at 47 touched THREE cities (4 VP for one conversion). City VP 15 (best ever vs 0/6/10/10/9/8/9/5 history).

### 4. Game-end control
- Held Lake Marineris and played it final gen to cap oceans, denying John extra greenery generations. Also used Virus (–2 Predators animals) and Deimos Down (wiped 10 of John's plants + 3 temp TR) as tempo denial.

### 5. Board adjacency rule corrected
The doc's adjacency rule had mirrored up-diagonals in ALL three row bands (found for y>4 empirically in-game; y<4 and y=4 confirmed against server `Board.computeAdjacentSpaces` post-game). Correct: y<4 up `(x,y-1),(x+1,y-1)` / down `(x-1,y+1),(x,y+1)`; y=4 up `(x,y-1),(x+1,y-1)` / down `(x,y+1),(x+1,y+1)`; y>4 up `(x-1,y-1),(x,y-1)` / down `(x,y+1),(x+1,y+1)`. All 61 space lines (ids, coords, types, bonuses, volcanic flags) verified correct vs TharsisBoard.ts. Trust server space lists over hand computation.

## What Went WRONG

### 1. TR gap 41 vs 57 (–16) ← THE decisive category
John's TR came from: 15 plant prod → greenery oxygen steps, Regolith Eaters oxygen, heat conversions, ocean placements (Convoy, Ice Cap, Artificial Lake), Giant Ice Asteroid/NRA events, Terraforming Ganymede +5. I terraformed ~14 steps total vs his ~27.
**Lesson: milestones+awards+cities cannot cover a 16-TR gap. Need ~2 TR/gen minimum from gen 4 (heat conversion cadence, cheap TR events like Release of Inert Gases — which I bought and never played!).**

### 2. Plant-engine differential: 6 vs 15 plant prod
Birds/Herbivores/Livestock each took "-1 any plant production" from John, but he added Insects (+6 for 9 MC!), NRA (+4), Grass/Heather/Moss/Bushes. Insects (plant prod per plant tag) is the single scariest plant card — **hate-draft Insects against a plant-tag deck**.

### 3. Unplayed value ~40 MC
Release of Inert Gases (2 TR!), Comet, Imported Hydrogen, Birds all died in hand; ~13 buys never played. Same lesson #35 as Game 8 — with a 12-gen clock, stop buying non-immediate cards around gen 9.

### 4. Draw-engine gap persists (but narrowed)
Business Network + Dev Center + Olympus vs John's 5-engine stack. He played 63 tableau cards vs my 35. His card VP 36 vs my 27 despite my 3 VP-per-resource cards (Livestock 7, Herbivores 3 — Livestock via Large Convoy's 4-animal dump was excellent, ~7 VP from one card).

### 5. Special-tile blocking by John
John dropped Restricted Area (39), Industrial Center (53), Commercial District (48 — scored 2 VP off MY cities) into my cluster's greenery slots. **Special tiles are placement weapons; consider doing the same to his clusters, and leave fewer open shared slots.**

## Validated / new rules

1. **Mayor rush via Tharsis+city prelude+cheap city card is a gen-1 lock.** Repeatable.
2. **Planner is claimable by accident with a big hand — check it every gen.**
3. **Fund the LAST award slot even at 20 MC when you lead a category** — it's +5 for me AND –5 denial in one action.
4. **Energy-requirement trap**: Corporate Stronghold/Domed Crater need energy prod ≥1; with 0, budget +11 for Power Plant SP first.
5. **Payment JSON**: server needs lowercase `megacredits` and ALL payment fields present; standard projects via choose_or_option with full payment, or pay_for_project_card. In submit_multi_actions, option indices SHIFT after each action — only chain when indices are stable (space selections after a card are fine; a second or-menu pick usually is not).
6. **Immigration Shuttles in a Tharsis game**: 4 VP + 5 MC prod — excellent.
7. **Heat Trappers on the opponent's heat engine** (-2 heat prod, -1 VP) crippled John's Thermalist... but he rebuilt with GHG Factories. Denial buys ~2-3 gens, not the game.
