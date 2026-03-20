# Terraforming Mars Postmortem
## Game: `http://localhost:8080/player?id=p9f21c8d3fef2`
## Date: `2026-03-10`

## 1) Outcome Snapshot

- Final result: **John 118 - 99 Codex**
- Ended in **Generation 11**
- Board: `tharsis`
- Initial strategy call (Gen 2-3): `hybrid`
- Did we pivot? `yes`
- Pivot generation: `7`

## 2) Score Decomposition

| Category | Self | Opponent | Delta (Opp - Self) |
|---|---:|---:|---:|
| TR | 50 | 42 | -8 |
| Milestones | 5 | 10 | +5 |
| Awards | 10 | 5 | -5 |
| Greenery | 10 | 10 | 0 |
| City | 7 | 11 | +4 |
| Card VP | 17 | 40 | +23 |
| **Total** | 99 | 118 | +19 |

## 3) Timeline by Generation

- Gen 1: Cheung Shing MARS opened with Aquifer Turbines and Dome Farming; Domed Crater plus GHG Factories established an early board anchor and heat plan.
- Gen 2: Geothermal Power, Imported GHG, and Adapted Lichen converted the opening into reliable heat and plant production while John accelerated with Giant Ice Asteroid.
- Gen 3: Mohole Area, Power Plant, Thermalist funding, and double heat conversion committed hard to a closure-heavy hybrid line.
- Gen 4: Space Elevator into Builder claim plus two heat conversions gave us strong public-point control, but John added Gardener, a second city, and more titanium scaling.
- Gen 5: Methane From Titan, a greenery, and another heat step kept pace high while John continued board expansion with Industrial Center.
- Gen 6: Big Asteroid, Land Claim, and double heat conversion were the clearest successful denial turns of the game and kept John off an easy plant burst.
- Gen 7: Ecological Zone, Eos Chasma National Park, Banker funding, a greenery, and two more heat conversions were the intended VP-floor pivot and the best stretch of our game.
- Gen 8: Tundra Farming, Zeppelins, two heat conversions, and Bushes improved income and plants, but John's science draw package started to turn into a real late-game card-VP threat.
- Gen 9: Medical Lab, greenery conversion, standard greenery, and Rover Construction increased our direct VP, but John kept adding card draw and protected engine pieces.
- Gen 10: Magnetic Field Dome, Noctis Farming, two greeneries, and the final ocean pushed globals to the brink, yet John converted a huge plant/animal burst with Large Convoy and other space events.
- Gen 11: Terraforming Ganymede plus a standard greenery ended the game on our turn, but John's previous-generation stack of Fish, Birds, Livestock, Decomposers, and late science discounts had already created an insurmountable card-VP ceiling.

## 4) Strategy Review

### Self
- Core plan: Hybrid tempo opening into a heat-driven closure line, then a Gen 7 pivot into plant/card/board VP while preserving Banker and Thermalist.
- What worked: Milestone timing was better, award funding was disciplined, and endgame liquidation was much cleaner than in earlier games.
- What failed: We still gave John too much time to assemble a full science-discount plus animal conversion engine, and our own card-VP ceiling never got high enough to keep pace once that engine came online.

### Opponent
- Core plan: Tharsis Republic board economy into stacked science and space discounts, then a late plant/animal explosion backed by Inventors' Guild, Olympus Conference, Mass Converter, Anti-Gravity Technology, and Space Station.
- How they converted into VP: They stayed close enough on public points, then won decisively through 40 card VP from Fish, Livestock, Birds, Decomposers, Advanced Ecosystems, Jovian scoring, and late-value space cards.
- What we failed to deny: The science discount stack, repeated card-flow actions, and the late animal package that transformed one extra generation into a huge VP swing.

## 5) Critical Turning Points

| Gen | Decision | Why it mattered | VP impact estimate |
|---:|---|---|---:|
| 6 | Big Asteroid plus immediate plant denial and continued heat conversions | This was the right line and bought time against John's plant engine | 7 |
| 7 | Ecological Zone + Eos Chasma + Banker funding pivot | This fixed earlier failure modes and gave us a real VP floor instead of pure TR play | 9 |
| 10 | John's Anti-Gravity Technology / Space Station turn after earlier science setup | That discount-stack completion made his final generation dramatically more valuable than ours | 12 |

## 6) Counterfactuals

| Alternative line | Realism | Estimated swing |
|---|---|---:|
| Treat John's science-discount stack as the hard alarm by Gen 8 and force an even faster close, even at the cost of one medium-value engine card | med | 8 |
| Convert one more midgame action into direct city-denial or board pressure around John's eventual animal/greenery cluster instead of another generic heat/TR step | med | 6 |
| Start a higher-ceiling card-VP lane one generation earlier instead of relying mostly on public points plus two awards | med | 7 |

## 7) Mistake Taxonomy Tags

- `opponent_engine_underrated`
- `vp_ceiling_miscalculated`
- `insufficient_card_vp_scaling`
- `ignored_award_race`

## 8) Tool Mismatches

| Tool | Expected | Actual | Root cause | Mitigation |
|---|---|---|---|---|
| n/a | n/a | No blocking MCP/server mismatch occurred in this game | n/a | Continue using action-tool return state as primary state source; no specific tooling bug changed the outcome |

## 9) Rule Updates (Must Be Actionable)

1. If the opponent completes a science-discount stack by Gen 8, then immediately switch to maximum closure mode unless our own card-VP ceiling is already competitive.
2. If our win plan is public-points heavy, then require at least one additional scalable card-VP lane by Gen 7 instead of trusting TR plus awards to hold.
3. If temperature and oceans are already closed or nearly closed, then value oxygen-ending greenery lines above almost all remaining setup cards unless a card scores immediately this generation.

## 10) Next-Game Checklist

- [x] Strategy call logged by Gen 3.
- [x] Milestone contest plan explicit by Gen 4.
- [x] Award funding lock confidence checked.
- [x] Card VP race estimate written by Gen 6.
- [x] Endgame conversion plan written at start of final generation.
