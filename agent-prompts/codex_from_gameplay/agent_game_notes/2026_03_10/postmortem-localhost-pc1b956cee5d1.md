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
It was that I still did not forecast that outscaling accurately enough early enough, so I kept making locally reasonable plays inside the wrong global plan.

| Category | Self Forecast | Self Actual | Opp Forecast | Opp Actual |
|---|---:|---:|---:|---:|
| TR | ~48 | 48 | ~42 | 53 |
| Awards | `Landlord` favored, `Banker` likely close | 0 | `Miner` likely, `Banker` uncertain | 15 |
| Greenery | ~8 to 10 | 8 | ~8 to 10 | 9 |
| City | ~8 to 10 | 9 | ~10 to 12 | 14 |
| Card VP | ~10 to 15 | 8 | ~30 to 35 | 46 |

- What did the forecast miss?: I underestimated the size of John's eventual `card_vp` explosion, overestimated the durability of my award/public-point shell, and failed to see that the handicap was already being neutralized because John was winning both `TR` and the higher-density scoring categories.
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
- What worked: Milestones were strong, the city shell was established early, and the Gen 8-10 closure line was more disciplined than in earlier losses.
- What failed: The plan never became a true winning identity. It was not fast enough to deny John's engine, not scalable enough to beat it in `card_vp + city`, and not controlling enough to hold awards once his production exploded. The Gen 11 endgame conversion miss was large, but it sat on top of a deeper failure: I had already allowed the game to become exactly the sort of Generation 11 payoff environment John's deck wanted.
- Did we drift into an under-defined hybrid line?: `yes`

### Opponent
- Core plan: CrediCor production into stacked science discounts, card draw, and late plant/animal/Jovian conversion.
- How they converted into VP: They assembled a layered late-game scoring architecture rather than just a good engine. `AI Central`, `Mass Converter`, `Quantum Extractor`, `Anti-Gravity Technology`, `Shuttles`, `Earth Office`, and repeated draw actions made every surviving generation dramatically more valuable. That engine then converted into `46` card VP, `15` award VP, a stronger city network, and enough `TR` to erase the handicap.
- What we failed to deny: The science-discount stack itself, the transition from "engine" into "scoring engine", the award flips once his economy overtook ours, and the exact game length his deck wanted.
- Which explicit engine alarms should have fired: `AI Central + Mass Converter` at Gen 6 to 7 should have triggered a hard-closure posture, and `Quantum Extractor` at Gen 8 should have been treated as a full emergency rather than just another strong card.

## 5) Critical Turning Points

| Gen | Decision | Why it mattered | VP impact estimate |
|---:|---|---|---:|
| 7-8 | Failed to convert the engine alarm into a truly different macro plan | From this point on, I still played many "good hybrid" actions in a game state that required either hard close or a real VP race. This let John keep building the exact endgame his deck wanted | 15 |
| 9-10 | Lost scoreboard control on awards and late category forecasting | John overtook `Banker`, funded and won `Miner`, and closed the gap on `Landlord`, which meant the public-point shell I thought I was protecting was already collapsing | 12 |
| 11 | Passed after post-terraform greenery instead of liquidating remaining `MC`/`steel` into more board VP during the rest of the generation | This stranded a large amount of guaranteed value and turned a bad position into a blowout | 12 |

## 6) Counterfactuals

| Alternative line | Realism | Estimated swing |
|---|---|---:|
| Replace the vague Gen 7-8 hybrid posture with a true hard-close plan once John's science-discount stack is live, even if that means giving up medium-value setup cards and some economy | med | 15 |
| Re-run the midgame score model around categories instead of TR, recognize that John is winning the future `card_vp + city + awards` race, and redirect Gen 9-10 actions into closure and board denial accordingly | med | 12 |
| After finishing Mars in Gen 11, continue the rest of the generation and liquidate `MC` and `steel` into at least one more city/greenery sequence instead of passing | high | 12 |

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
- `alarm_threshold_missed`
- `sunk_cost_award_defense`

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
| Earlier city anchors and greeneries will reduce the city-gap enough to keep the game close | The board was more stable than in some earlier losses, but the city improvement was far too small to matter against a `-38` card-VP gap | weakened |
| Stricter award discipline will improve net VP | It helped avoid the worst earlier award punts, but it was not enough without stronger scoreboard forecasting and earlier contest-or-concede decisions | unresolved |
| Earlier hard-close pressure against John's science engine performs better than generic hybrid drift | This game strongly supports that view; once the engine lived to Gen 11, the outcome was structurally bad | strengthened |

## 11) Endgame Conversion Review

- Did we write a liquidation plan by Gen 10+?: `partially`
- Did we check whether actions continued after terraforming completed?: `no`
- Which resources were stranded at pass or game end?: `MC`, `steel`, and some late heat/plant flexibility
- Best missed `MC -> VP` conversion: one more `standard city` followed by stronger post-end greenery placement
- Best missed board placement: preserving a better late city/greenery shell for the post-terraform portion of Gen 11 instead of ending the turn early

## 12) Structural Why-Loss

John did not win by `59` because of one missed line.
He won because he won the shape of the game.

The structural reasons:

- He erased the handicap and still finished ahead on `TR`.
- He built a real scoring engine, while I built a partially effective tempo shell.
- He won `awards`, `city`, and especially `card_vp` at the same time.
- I never forced a game length that punished his deck.
- I kept making individually reasonable actions inside a strategically losing game state.

The result was a layered defeat:

- `TR`: I failed to turn the handicap into either a short game or a stable public-point edge.
- `Awards`: I misread durability and let the scoreboard flip.
- `City/board`: I created a board shell but not a dominant board engine.
- `Card VP`: I never matched his scoring density, so every extra generation favored him heavily.
- `Endgame`: after Mars was complete, I still left points on the table.

That is why the margin was so large.
The game was not close and then thrown away.
It was structurally unfavorable by late midgame, then made worse by the final conversion error.

## 13) Next-Game Checklist

- [x] Strategy call logged by Gen 3.
- [ ] Macro call is specific enough to exclude strategic drift.
- [x] Milestone contest plan explicit by Gen 4.
- [x] Award funding lock confidence checked.
- [x] Card VP race estimate written by Gen 6.
- [ ] Gen 8 score forecast revised after opponent engine update.
- [ ] Endgame conversion plan written at start of final generation.
- [ ] After Mars is terraformed, live prompt checked before passing.
