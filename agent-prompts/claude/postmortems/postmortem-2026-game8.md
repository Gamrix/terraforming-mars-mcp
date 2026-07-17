# Post-Mortem: Game 8 (Claude red vs Codex blue) — Tharsis, 2-player, Prelude, 10 gens

**Result: Lost 66–102 (–36 VP)**

## Final Score Breakdown

| Category | Claude (red) | Codex (blue) |
|---|---|---|
| TR | 44 | 48 |
| Milestones | **0** | **15** (Builder + Gardener + Terraformer) |
| Awards | 5 (Thermalist won!) | 10 (Scientist + Landlord) |
| Greenery tiles | 2 | 7 |
| City adjacency | 5 | 7 |
| Card VP | 10 | 15 |
| Negative VP | −2 (Corporate Stronghold) | −1 |
| **Total** | **66** | **102** |

## Corporations

- **Claude (Teractor)**: Earth discount used well (Pets, BC, IH, Olympus, IS, Sponsors). Heat mega-engine: GHG Factories + Lunar Beam + Soletta = 15 heat prod by gen 6.
- **Codex (Valley Trust)**: science discount + Earth Catapult + Inventors' Guild/Search For Life draw. Oxygen engine: Regolith Eaters + Water Splitting Plant. Swept milestones by gen 8.

## What Went Right

### 1. FIRST AWARD WIN IN 8 GAMES — Thermalist (5 VP)
Funded gen 8 at 8 MC with a 46–3 heat-cube lead and 15-vs-0 heat production. This is what a **structural lock** looks like: opponent had zero heat production and no path to catch up. The new funding rule (structural production lock, not just a big number) is validated.

### 2. Heat engine produced TR 44 in a 10-gen game
GHG Factories (gen 1!) + Lunar Beam + Soletta (gen 4, paid 7 Ti) = 15 heat prod. Converted 8-heat→temp ~8 times. Plus 0°C bonus ocean, Rad-Chem, RIG, NRB cycle. Soletta at 35 MC paid for itself ~3x.

### 3. Toll Station timing (+6 MC prod for 10 MC)
Played when Codex had 6 space tags. Best economy card of my game.

### 4. Denial drafting worked
Took Herbivores, Medical Lab, Urbanized Area, Toll Station away from Codex at the right moments. Codex never got a VP-per-resource engine going.

## What Went Wrong

### 1. MILESTONE SWEEP AGAIN: 0 vs 15 (–15 VP)
Codex claimed Builder (gen 6), Gardener (gen 7), Terraformer (gen 8). Root cause: their tempo (steel prod from prelude → building tags; plant prod → greeneries; broad TR from oxygen+oceans) hit every milestone threshold before I hit any.
**Worse: I spent 25 MC on SP City in gen 10 to "claim Mayor" AFTER the 3-milestone cap had closed it.** My own notes (lesson #20) warned exactly this. The claim option never appeared because the cap was reached — I only realized after checking the server state.

### 2. Bought cards I never played (~27 MC wasted)
Never played: Predators (bought g2!), Livestock, Medical Lab, Bushes, Methane From Titan, Water Import From Europa, Beam From A Thorium Asteroid, Mars University, Urbanized Area. That's 9 cards × 3 MC = 27 MC of buys, plus planning attention. In a game that ends gen 10, a 26–30 MC card bought gen 5+ rarely gets played. **Count remaining generations before buying, not just card quality.**

### 3. Game ended 2–3 gens earlier than my plans assumed
I planned like a 12–14 gen game (buying Predators for oxygen 11%, Livestock for oxygen 9%). Codex's Regolith Eaters + Water Splitting Plant added ~2 oxygen steps/gen on top of greeneries; the game hit all maxes at gen 10. My engine cards (Ants gen 10, Herbivores gen 9) had 0–1 generations to accumulate.

### 4. Economy still second-best: MC prod peaked ~23 vs Codex ~30+
Better than past games but still behind. Also consistently overestimated my own MC (off-by-a-few errors four times) — track actuals via API, not mental math.

### 5. Plant production never got going (0–1 all game)
Biomass Combustors killed Lichen's +1; Virus and Asteroid ate my plant stockpiles twice (2-player: they always target me). Result: 2 greeneries vs 7. Greenery+city adjacency was 7 VP vs 14.

## Key Lessons for Game 9

1. **Check the milestone cap BEFORE any milestone investment.** Write the claimed count into every generation's planning. When 3 are claimed, Mayor/Planner are dead — stop pathing toward them.
2. **The award rule works — keep it**: fund only with a structural production lock (opponent production ≈ 0 in that category). Thermalist via heat-engine is a repeatable pattern with GHG Factories/Soletta-type builds.
3. **Estimate game end every generation from parameter velocity** (steps remaining ÷ steps/gen). Codex-style oxygen engines end games at gen 10. Stop buying cards whose requirements or payback need more generations than remain.
4. **In 2-player, plant strategies need Protected Habitats or must be abandoned early.** Two plant-removal hits + one plant-prod steal = my plant game never existed. Either draft protection or skip plant cards entirely and lean harder into heat/microbes (they were never attacked).
5. **Heat engine + Caretaker Contract is my best archetype so far** — but it caps at ~2 TR/gen. It needs a second VP source that survives a short game: cheap immediate VP (Mangrove-style tiles, RIG) beats slow accumulators (Predators, Livestock) when the clock is fast.
