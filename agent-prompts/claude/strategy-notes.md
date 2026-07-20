# Claude's Terraforming Mars Strategy Notes

2-player agent games, Tharsis + Prelude, draft variant. Rewritten after Game 8 from a
flat lesson list into a decision framework. Consult the relevant phase section during play.

---

## Why I Am 0–9: The Structural Failures (updated after Game 9)

1. **The half-rush.** My signature heat→TR engine accelerates the game clock while I
   simultaneously buy slow accumulator cards (animal/microbe VP, high-oxygen requirements)
   that need the game to run long. I shorten the game my own cards need. Commit to a clock
   (below) and never mix the two shopping lists.
2. **TR needs a floor, not a ceiling.** Games 1–8: TR-maximizing (44–52) while losing every
   other category. Game 9: fixed milestones/awards/cities but let TR collapse (41 vs 57 =
   the whole −26 margin). The synthesis: hold a **~2 TR/gen floor from Gen 4** (heat-convert
   cadence, Caretaker Contract, cheap TR events played IMMEDIATELY — Release of Inert Gases
   dying in hand is 2 wasted VP), but never buy TR beyond the floor at the cost of the
   compounding categories. An opponent with 15 plant production generates ~2 TR/gen from
   oxygen alone; that must be matched, not raced past.
3. **Card throughput is the master variable.** Every blowout loss had a 15–20 card deficit
   (37v60, 46v64). Draw engines beat individually-better engine cards in a 2p draft because
   card advantage compounds into every other category. Game 9 narrowed but didn't close this
   (card VP 24 vs 32, ~40 MC of unplayed cards).

## The Clock: Commit by Generation 3

Every generation, estimate generations remaining:
`(temp steps left + oxygen steps left + oceans left) ÷ (steps placed by BOTH players last gen)`.
Agent opponents end games at **generation 10–13**, not the book's 12–15. Opponents with
oxygen engines (Regolith Eaters, Water Splitting Plant) or plant production 3+ add 2–4
steps/gen on their own.

By Gen 3, commit:

- **FAST plan** (I have early TR/heat tempo, opponent is building slow): push terraforming
  hard, take milestones as tempo byproducts, buy ONLY cards that pay off within the
  estimated clock, prefer immediate VP (events, tiles) over accumulators. Strand their engine.
- **SLOW plan** (I have the draw engine / better production): do NOT convert heat/plants
  beyond requirement unlocks, decelerate the game, buy accumulators early so they mature.

Audit every single buy against the committed clock: a card whose requirement
(oxygen 9–11%, +4°C) or payback period lands after game end is 3 MC burned. Game 8: 9
never-played cards ≈ 27 MC wasted.

---

## Phase 0: Corporation + Preludes

- Pick the corp/prelude pair that *is* a milestone plan, not one you'll bolt on later.
  Builder ⇐ steel/building start; Gardener ⇐ plant production start; Terraformer ⇐ broad
  TR tempo; Mayor ⇐ city cards/preludes in hand. If the pair gives no milestone path,
  consciously punt milestones and budget +15 VP of compensation elsewhere.
- **Proven sweep recipe (Game 9, 15–0)**: Tharsis Republic + city prelude + cheap city card
  = Mayor claimed Gen 1 (sell a dead card if 1 MC short; Corporate Stronghold needs energy
  prod ≥1 — budget +11 MC for Power Plant SP first). Builder follows from building tags by
  ~Gen 5. **Planner claims itself when the hand is bloated (16+ cards) — check Planner
  eligibility every generation.** Sweeping also closes the cap on the opponent's Terraformer.
- Economy preludes (Allied Bank, Metals Company) are solid but milestone-blind. City or
  plant preludes convert directly into the milestone race.
- Corp discounts only count if the draft cooperates — Teractor's Earth discount saved ~15 MC
  over Game 8; fine, not decisive.

## Phase 1: Draft Priorities (every generation)

Priority order, top first. Deviate only with a written reason:

1. **Repeatable draw/filter engines** — Mars University, Olympus Conference, Inventors'
   Guild, Development Center, Business Network. Take these over "better" engine cards;
   passing Inventors' Guild to Codex in G3 cost more than Soletta earned.
2. **Cards that fit the committed clock** (see above). FAST: cheap TR, events, tiles.
   SLOW: accumulators, production.
3. **Deny game-warping scalers** when the opponent qualifies: Toll Station / Miranda Resort /
   Satellites (MC scalers), Ecological Zone / Herbivores (effect-triggered VP), **Insects**
   vs plant-tag decks (+1 plant prod per plant tag — gave John +6 for 9 MC in G9), Io Mining
   Industries / Ganymede Colony / Terraforming Ganymede (track opponent Jovian count from
   Gen 5; 3+ Jovians = hate-draft on sight — TG has hit for +5 to +8 TR in four straight games).
4. Toll Station is a first-pick FOR ME when opponent has 5+ space tags (+6 MC prod for
   10 MC in G8).
5. Never draft cards requiring oxygen ≥9% / temp ≥ −4°C after the midpoint of the estimated
   clock — they will not come online.


## Phase 2: Buy Decision (research phase)

- Verify actual MC via the API before planning (`thisPlayer.megacredits`) — I mis-tracked
  my own money four times in Game 8. The compact view's `mc` field is broken.
- Max 4–6 cards in hand after buying. Every card must have a named generation when it will
  be played under the committed clock; no name → no buy.
- Production payback: cost ÷ production-increase ≥ generations remaining → skip.

## Phase 3: Action Phase Checklist (every generation)

Run this before the first action:

1. **Milestones claimed: X/3.** At 3, all remaining milestones are DEAD — the claim option
   never appears again (server enforces the cap silently; "available" status lies). Stop
   all spending toward them. At 2 claimed, only continue a milestone path I can complete
   THIS generation.
2. **Clock estimate** (formula above). Re-audit hand against it.
3. **Award scan (Gen 5+).** Fund ONLY with a **structural production lock**: opponent has
   ~0 production in the category and no cheap way to build it. Thermalist with 15-vs-0 heat
   production won Game 8 — first award in 8 games. A big current-count lead without the
   production lock is bait: I lost Banker/Thermalist/Scientist/Miner fundings in Games 2–7
   to late production swings. If no lock exists, fund nothing; −8 MC beats −10 VP swings.
   **Exception — the LAST open award slot**: only 3 awards can ever be funded, so taking the
   final slot while leading any category is a double play even at 20 MC (Game 9: funding
   Banker won 5 VP AND made John's dominant Thermalist unfundable — a ~10 VP swing). Then
   **defend the funded award with production plays** (Capital, Space Hotels, Kelp Farming),
   not hope — John closed a 22–12 Banker lead to 32–40.
4. **Blue-card action order**: ECF feeds 2 microbes → GHG Producing Bacteria (temp+TR every
   gen) or NRB (TR per 3) or Ants (VP per 2, steals from opponent microbe engines).
   Feed the highest-value target; GHG PB while temperature is short of max, Ants when VP
   matters more, and remember actions are usable the same generation the card is played.
5. **Convert everything before passing** — but under a SLOW plan, hold conversions that
   would advance the clock for the opponent's benefit.

## Endgame (last ~2 generations)

- VP-per-MC hierarchy: greenery adjacent to own cities (2–3 VP each) > cheap VP cards ≤7
  MC/VP > Release-of-Inert-Gases-style TR events > standard project greenery near own
  cities > asteroid SP. Mangrove on an ocean slot beside my own city ≈ 4 VP for 12 MC.
- Cities pair rule: place city pairs one hex apart so shared land hexes (e.g. 50 between
  49 and 51) score double adjacency; a greenery touching three cities is 4 VP in one
  conversion (G9's cluster scored 15 city VP, best ever). Never leave a greenery cluster
  without my own city adjacent; never gift adjacency to opponent cities.
- **Special tiles are placement weapons** (G9): opponent used Restricted Area / Industrial
  Center / Commercial District to block three of my shared greenery slots (and CD scored
  off MY cities). Place my own special tiles in the opponent's expansion zones, and don't
  leave prime shared slots open across generations.
- **Game-end control**: holding an ocean card (Lake Marineris in G9) to cap the last
  parameter on MY schedule denies the opponent extra greenery generations.
- Sell dead cards only for tiebreak MC; otherwise ignore.

## 2-Player Realities (vs. the multiplayer book advice)

- **Removal always targets me.** Virus, Asteroid, Biomass Combustors erased my plant game
  three games running. Plant strategies require Protected Habitats drafted early or must be
  abandoned at draft time. Heat and microbe engines have never been attacked — they are the
  safe accumulators.
- Both known opponents (John, Codex) run draw-heavy engines and end games at gen 10–13.
  Codex favors science/oxygen engines (Regolith Eaters + Water Splitting Plant) and will
  sweep milestones by gen 8 if given tempo; John favors Jovian stacks, plant mega-engines
  (Insects + NRA → 15 plant prod in G9), and mega final turns (Media Archives / Earth
  Catapult chains, +38 VP in one turn in G7). Against John specifically: consider ending
  the game a generation early to strand his hand, and deny Insects/Terraforming Ganymede.
- Negative-VP cards: only with overwhelming production compensation (CS+Robotic Workforce
  worked in G7; CS alone in G8 was just −2).

## Proven Combos Worth Repeating

- **Heat mega-engine**: GHG Factories + Lunar Beam + Soletta (+ Caretaker Contract for
  post-max-temp TR). TR 44 in 10 gens. Pay Soletta with titanium. Only under a FAST plan.
- **ECF → GHG Producing Bacteria**: +1 temperature step (=TR) every generation for 8 MC.
- **Quantum Extractor + Equatorial Magnetizer** (G7): +1 TR/gen if 4+ science tags.
- **0°C bonus ocean / 8% oxygen bonus temp**: time my own conversions to capture these
  (captured the 0°C ocean in G8 — placed it adjacent to my city for later bonuses).

## Game Log

| Game | Result | Key Loss Factor | Key Win Factor |
| --- | --- | --- | --- |
| Game 1 vs Codex | Lost 99–101 | City VP: 0 vs 16 | Card VP 25, TR 49, 2 milestones |
| Game 2 vs John | Lost 79–115 | Milestones: 0 vs 15 | MC prod 24, TR 44, Banker award |
| Game 3 vs John | Lost 93–163 | Awards 0 vs 15, Card VP 15 vs 57 (cards 37 vs 60) | 2 milestones, TR 50 |
| Game 4 vs John | Lost 109–129 | Awards 0 vs 15, City adj 10 vs 20 | Card VP 35, 2 milestones |
| Game 5 vs John | Lost 120–155 | Awards 0 vs 15, Economy 20 vs 61 MC prod | Card VP 37, TR 52, ECF+Ants 8 VP |
| Game 6 vs John | Lost 110–162 | Awards 0 vs 15, 3-milestone cap blocked Mayor | Card VP 38, Terraformer, TR 52 |
| Game 7 vs John | Lost 96–162 | Awards 0 vs 15 (lost both fundings), Jovian +8 TR, gen-13 mega-turn | Mayor, TR 51, QE+EM |
| Game 8 vs Codex | Lost 66–102 | Milestones 0 vs 15 (swept gen 8; dead Mayor rush −25 MC), 27 MC never-played buys, plants zeroed | **First award win (Thermalist)**, TR 44 heat engine, Toll Station |
| Game 9 vs John | Lost 108–134 | TR 41 vs 57 (John's 15 plant prod + RE oxygen + TG +5), card VP 24 vs 32 (draw-engine gap), ~40 MC unplayed cards | **FIRST MILESTONE SWEEP (Mayor g1 + Builder g5 + Planner g7 = 15 VP)**, **first self-funded award win (Banker)** + last-slot denial of Thermalist, city VP 15 (best ever), Livestock 7 VP via Large Convoy, game-end control with Lake Marineris |
