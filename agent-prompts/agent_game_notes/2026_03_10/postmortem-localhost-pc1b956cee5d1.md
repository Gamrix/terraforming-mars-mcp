# Terraforming Mars Postmortem
## Game: `http://localhost:8080/player?id=pc1b956cee5d1`
## Date: `2026-03-10`

## 1) Outcome Snapshot

- Final result: **John 142 - 83 Codex**
- Ended in **Generation 11**
- Board: `tharsis`
- Initial strategy call (Gen 2-3): `hybrid leaning close`
- Did we pivot? `yes`
- Pivot generation: `8`
- Was the macro call actually specific enough to constrain play? `no`

## 2) Score Decomposition

| Category | Self | Opponent | Delta (Opp - Self) |
|---|---:|---:|---:|
| TR | 48 | 53 | +5 |
| Milestones | 10 | 5 | -5 |
| Awards | 0 | 15 | +15 |
| Greenery | 8 | 9 | +1 |
| City | 9 | 14 | +5 |
| Card VP | 8 | 46 | +38 |
| **Total** | 83 | 142 | +59 |

## 2A) Forecast Accuracy

The key structural problem in this game was not just that John outscaled us.
It was that I still did not forecast that outscaling accurately enough early enough.

| Category | Self Forecast | Self Actual | Opp Forecast | Opp Actual |
|---|---:|---:|---:|---:|
| TR | ~48 | 48 | ~42 | 53 |
| Awards | `Landlord` favored, `Banker` likely close | 0 | `Miner` likely, `Banker` uncertain | 15 |
| Greenery | ~8 to 10 | 8 | ~8 to 10 | 9 |
| City | ~8 to 10 | 9 | ~10 to 12 | 14 |
| Card VP | ~10 to 15 | 8 | ~30 to 35 | 46 |

- What did the forecast miss?: I still underestimated the size of John's final-generation card dump and overestimated how much public-point control would matter once his discount stack survived to Gen 11.
- Did we think we were ahead because of TR while actually behind on VP ceiling?: `yes`

## 3) Timeline by Generation

- Gen 1: Cheung Shing MARS opened with `Domed Crater`, `Olympus Conference`, and `Development Center`, setting up a city shell and early science/card access.
- Gen 2: `Magnetic Field Dome`, `Plantation`, and `Mining Rights` established early TR and board position while John built resource production.
- Gen 3: `Imported GHG`, `Deep Well Heating`, and `Sponsors` pushed the game toward a heat-based hybrid close.
- Gen 4: `Noctis City`, `Toll Station`, and `Noctis Farming` improved board and economy, while John added engine pieces and `Space Elevator`.
- Gen 5: `Tectonic Stress Power`, `Industrial Microbes`, and card draw kept the build flexible, but John's science and steel base kept scaling.
- Gen 6: `Builder` was secured and the board shell remained strong, but John's `AI Central + Mass Converter` stack became a real alarm.
- Gen 7: `Landlord` was funded with a durable edge, and the line shifted toward closure plus VP floor instead of more generic setup.
- Gen 8: `Special Design -> Zeppelins`, `Bushes`, `Artificial Lake`, and a greenery at `26` improved the city network, but John completed `Quantum Extractor` and extended the science-discount engine.
- Gen 9: `Subterranean Reservoir`, `Energy Saving`, `Permafrost Extraction`, `Steelworks`, and `Space Station` pushed globals hard and added some direct VP, while John converted oceans and plants into a much larger engine endgame.
- Gen 10: `Steelworks`, `Imported Hydrogen`, `Convoy From Europa`, and `standard greenery` brought the game to `12% oxygen / 9 oceans`, but John funded `Miner`, widened `Banker`, and kept adding late-value cards.
- Gen 11: `Steelworks + standard greenery` ended Mars, but I then misread the post-terraform window and failed to liquidate the remaining `MC`/`steel` into more cities or greeneries before passing. John used the rest of the generation to dump high-VP cards, convert plants repeatedly, and add a late city/greenery burst.

## 4) Strategy Review

### Self
- Core plan: Hybrid board-and-closure line using early cities, building discounts, and later oxygen/ocean pressure to end before John's engine fully cashed out.
- Why this macro plan was chosen: The opening had enough city/building quality to avoid pure rush, but not enough obvious card-VP scaling to commit to a long outscale game.
- What worked: Milestones were strong, the `Landlord` funding was initially sound, and the Gen 8-10 closure line was much more disciplined than in earlier losses.
- What failed: The macro call was still too vague to fully constrain play. I drifted inside "hybrid" rather than explicitly deciding whether I was hard-closing or trying to compete on VP ceiling, and the largest self-inflicted error was the Gen 11 endgame conversion miss after Mars was already terraformed.
- Did we drift into an under-defined hybrid line?: `yes`

### Opponent
- Core plan: CrediCor production into stacked science discounts, card draw, and late plant/animal/Jovian conversion.
- How they converted into VP: They turned `AI Central`, `Mass Converter`, `Quantum Extractor`, `Anti-Gravity Technology`, and multiple card-flow actions into a giant final-generation dump that produced `46` card VP plus superior award and city totals.
- What we failed to deny: The science-discount stack itself, the late `Predators/Decomposers/Ganymede/Terraforming Ganymede` payoff window, and the final action cycle after Mars was completed.
- Which explicit engine alarms should have fired: `AI Central + Mass Converter` at Gen 6 to 7 should have triggered a hard-closure posture, and `Quantum Extractor` at Gen 8 should have been treated as a full emergency rather than just another strong card.

## 5) Critical Turning Points

| Gen | Decision | Why it mattered | VP impact estimate |
|---:|---|---|---:|
| 8 | Pivoted into `Zeppelins`, `Bushes`, and board conversion instead of more abstract setup | This was correct and kept the game close enough to force a Gen 11 finish | 8 |
| 10 | John's `Miner` funding plus continued Banker growth were not contested | Public-point control flipped away from us despite earlier award discipline | 10 |
| 11 | Passed after post-terraform greenery instead of liquidating remaining `MC`/`steel` into more board VP during the rest of the generation | This stranded a large amount of guaranteed value and let John keep the last word on board and card conversion | 12 |

## 6) Counterfactuals

| Alternative line | Realism | Estimated swing |
|---|---|---:|
| After finishing Mars in Gen 11, continue taking the rest of the generation and convert `MC` into one more `standard city` plus follow-up greenery instead of passing | high | 12 |
| Treat `AI Central + Mass Converter + Quantum Extractor` as a hard closure emergency by Gen 8 and reserve more Gen 9-10 cash for guaranteed closing actions | med | 9 |
| Concede `Banker` earlier once John overtook the category and redirect one funding/conversion window into direct board VP | med | 5 |

## 7) Mistake Taxonomy Tags

- `opponent_engine_underrated`
- `vp_ceiling_miscalculated`
- `hybrid_drift`
- `forecasting_failure`
- `endgame_conversion_miss`
- `post_terraform_pass_error`
- `resource_stranding`
- `ignored_award_race`
- `insufficient_card_vp_scaling`

## 8) Tool Mismatches

| Tool | Expected | Actual | Root cause | Mitigation |
|---|---|---|---|---|
| n/a | n/a | No blocking MCP/server payload mismatch changed this result | n/a | The decisive failure was strategic and rules-interpretation related, not a tool bug |

## 9) Rule Updates (Must Be Actionable)

1. If Mars becomes fully terraformed during the action phase, then assume the rest of the generation is still live until the prompt proves otherwise and liquidate all remaining `MC/plants/steel` before passing.
2. If John has `AI Central + Mass Converter` and adds another science/space discount by Gen 8, then reserve Gen 9-10 actions primarily for guaranteed closure and board VP, not additional setup.
3. If a funded award trajectory flips by Gen 10, then stop defending sunk-cost pride and convert the remaining windows into guaranteed points instead of leaving the category to drift away.

## 10) Active Hypotheses Check

| Hypothesis | Result in this game | Status |
|---|---|---|
| Earlier city anchors and greeneries will reduce the city-gap enough to keep the game close | Helped, but not nearly enough once John's card-VP ceiling exploded | unresolved |
| Stricter award discipline will improve net VP | Helped relative to some earlier games, but John still swept `Banker` and `Miner` once the race flipped | unresolved |
| Earlier hard-close pressure against John's science engine performs better than generic hybrid drift | The game only fully broke once the closure pressure softened and the engine lived to Gen 11 | strengthened |

## 11) Endgame Conversion Review

- Did we write a liquidation plan by Gen 10+?: `partially`
- Did we check whether actions continued after terraforming completed?: `no`
- Which resources were stranded at pass or game end?: `MC`, `steel`, and some late heat/plant flexibility
- Best missed `MC -> VP` conversion: one more `standard city` followed by stronger post-end greenery placement
- Best missed board placement: preserving a better late city/greenery shell for the post-terraform portion of Gen 11 instead of ending the turn early

## 12) Next-Game Checklist

- [x] Strategy call logged by Gen 3.
- [ ] Macro call is specific enough to exclude strategic drift.
- [x] Milestone contest plan explicit by Gen 4.
- [x] Award funding lock confidence checked.
- [x] Card VP race estimate written by Gen 6.
- [ ] Gen 8 score forecast revised after opponent engine update.
- [ ] Endgame conversion plan written at start of final generation.
- [ ] After Mars is terraformed, live prompt checked before passing.
