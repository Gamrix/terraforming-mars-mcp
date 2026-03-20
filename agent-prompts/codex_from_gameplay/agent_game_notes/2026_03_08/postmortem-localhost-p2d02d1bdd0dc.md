# Terraforming Mars Postmortem
## Game: `http://localhost:8080/player?id=p2d02d1bdd0dc`
## Date: `2026-03-08`

## 1) Outcome Snapshot

- Final result: **John 99 - 92 Codex**
- Ended in **Generation 10**
- Board: `tharsis`
- Initial strategy call (Gen 2-3): `hybrid`
- Did we pivot? `yes`
- Pivot generation: `7`

## 2) Score Decomposition

| Category | Self | Opponent | Delta (Opp - Self) |
|---|---:|---:|---:|
| TR | 49 | 44 | -5 |
| Milestones | 10 | 5 | -5 |
| Awards | 0 | 15 | +15 |
| Greenery | 5 | 8 | +3 |
| City | 9 | 12 | +3 |
| Card VP | 19 | 15 | -4 |
| **Total** | 92 | 99 | +7 |

## 3) Timeline by Generation

- Gen 1: Inventrix opener with Smelting Plant + Orbital Construction Yard; Mohole Area, Space Station, and Asteroid established early heat-space tempo.
- Gen 2: Methane From Titan + Import of Advanced GHG built a stronger VP-plus-production floor than prior rush games.
- Gen 3: Research, Geothermal Power, and a heat conversion kept science access open while preserving closure pace.
- Gen 4: Ice Asteroid, greenery conversion, Rad-Chem Factory, and Power Plant accelerated globals and started our own board network.
- Gen 5: Capital at 41 plus Rad-Suits converted tempo into city VP and card VP instead of staying single-lane terraforming.
- Gen 6: Terraformer claimed; Lava Flows + double heat conversion compressed the game while John's Earth Catapult engine kept growing.
- Gen 7: Industrial Microbes, Domed Crater at 50, Builder claim, greenery at 51, and another heat conversion deepened our board and public-point floor.
- Gen 8: Large Convoy, another greenery, Great Dam, Noctis Farming, and heat conversion continued strong liquidation while John built massive income.
- Gen 9: Herbivores, Plantation, Advanced Ecosystems, Small Animals, heat conversion, and Imported Hydrogen pivoted hard into endgame VP.
- Gen 10: Cupola City at 52, greenery at 62, standard city at 59, final heat conversion to +8 C, and animal-resource conversion closed the board efficiently.

## 4) Strategy Review

### Self
- Core plan: Hybrid tempo opening into earlier board/card-VP pivot, then endgame liquidation before John could exploit a full engine game.
- What worked: Early milestone control, stronger card VP than previous games, meaningful city/greenery network, and much better timing on pivoting away from pure TR.
- What failed: We still allowed John to own the award layer completely and did not deny enough late city/public scoring despite the improved board plan.

### Opponent
- Core plan: Tharsis Republic board-economy start into stacked earth/science/space discounts and very high income.
- How they converted into VP: Funded and won Banker, Miner, and Scientist; also finished ahead on greenery and city adjacency while keeping acceptable card VP.
- What we failed to deny: Midgame award setup, late city placements, and the economic runway that made three funded awards safe.

## 5) Critical Turning Points

| Gen | Decision | Why it mattered | VP impact estimate |
|---:|---|---|---:|
| 6 | Claimed Terraformer and kept closure pressure on temperature | Secured cheap public VP and prevented the game from stretching into a much worse engine contest | 6 |
| 7 | Domed Crater + Builder claim + greenery network pivot | This was the right structural adjustment and is a main reason the game stayed close | 8 |
| 9-10 | Opponent funded Banker, Miner, and Scientist uncontested | The 15 VP award swing was larger than the final margin and effectively decided the game | 15 |

## 6) Counterfactuals

| Alternative line | Realism | Estimated swing |
|---|---|---:|
| Fund Landlord or Thermalist earlier only if first-place hold is credible, instead of conceding all three live awards | med | 7 |
| Add one more denial-oriented city/greenery placement around John's cluster by Gen 8-9 rather than one extra pure terraforming action | med | 5 |
| Write an explicit Gen 7 award-race forecast and make a commit-or-ignore decision before John funds Banker/Miner | high | 6 |

## 7) Mistake Taxonomy Tags

- `award_funding_mislock`
- `ignored_award_race`
- `opponent_engine_underrated`
- `endgame_conversion_miss`
- `vp_ceiling_miscalculated`

## 8) Tool Mismatches

| Tool | Expected | Actual | Root cause | Mitigation |
|---|---|---|---|---|
| n/a | n/a | No blocking MCP/server mismatch occurred in this game | n/a | Continue polling state after any ambiguous action outcome, but no specific tool bug affected result here |

## 9) Rule Updates (Must Be Actionable)

1. If the opponent's projected award EV is concentrated in two or more categories by Gen 7, then make an explicit contest-or-concede call before they fund, rather than drifting into a free 10-15 VP swing.
2. If a city card can be converted into immediate adjacency value this generation, then prefer it over another generic TR push once one global is already within 3-4 steps of completion.
3. If the game is likely ending in Gen 10, then value late animal/card-VP setup only when it scores immediately or within one guaranteed follow-up action.

## 10) Next-Game Checklist

- [x] Strategy call logged by Gen 3.
- [x] Milestone contest plan explicit by Gen 4.
- [ ] Award funding lock confidence checked.
- [x] Card VP race estimate written by Gen 6.
- [x] Endgame conversion plan written at start of final generation.
