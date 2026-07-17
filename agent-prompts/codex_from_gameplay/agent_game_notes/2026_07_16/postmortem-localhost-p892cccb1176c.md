# Terraforming Mars Postmortem
## Game: `http://localhost:8080/player?id=p892cccb1176c`
## Date: `2026-07-16`

## 1) Outcome Snapshot

- Final result: **Codex 102 - 66 Claude**
- Opponent: `Claude`
- Ended in **Generation 10**
- Board: `tharsis`
- Initial strategy call (Gen 2-3): `outscale`
- Did we pivot? `yes`
- Pivot generation: `7`
- Was the macro call actually specific enough to constrain play? `yes`

The opening call was to use the Valley Trust/Earth Catapult science-discount shell to outscale while preserving an oxygen-and-board closure fallback. By Gen 7, after `Water Splitting Plant`, `Towing A Comet`, and the milestone sweep became available, the plan tightened into a closure line: win milestones and board categories, let Claude spend into temperature, and personally finish oxygen and oceans.

## 2) Score Decomposition

| Category | Self | Opponent | Delta (Opp - Self) |
|---|---:|---:|---:|
| TR | 48 | 44 | -4 |
| Milestones | 15 | 0 | -15 |
| Awards | 10 | 5 | -5 |
| Greenery | 7 | 2 | -5 |
| City | 7 | 5 | -2 |
| Card VP | 15 | 10 | -5 |
| **Total** | **102** | **66** | **-36** |

## 2A) Forecast Accuracy

The only explicit in-game Gen 6 forecast was a total-score range: roughly **75-90 Codex** versus **65-85 Claude**, with the call `outscale leaning close`. The category values below are the best reconstruction from the contemporaneous board state, not a category forecast that was actually written during play. That missing table is a process failure.

| Category | Self Forecast | Self Actual | Opp Forecast | Opp Actual |
|---|---:|---:|---:|---:|
| TR | 42 | 48 | 44 | 44 |
| Awards | 5 | 10 | 5 | 5 |
| Greenery | 7 | 7 | 4 | 2 |
| City | 5 | 7 | 4 | 5 |
| Card VP | 12 | 15 | 17 | 10 |

- What did the forecast miss? It missed the full three-milestone sweep, understated our award and card-VP conversion, and overestimated Claude's animal/microbe card-VP ceiling because the game closed before those engines matured.
- Did we think we were ahead because of TR while actually behind on VP ceiling? `No`. The plan explicitly relied on milestones, oxygen, board control, and awards rather than TR alone.
- Gen 8 revision: no formal category-by-category rewrite was recorded. The live decisions did correctly recognize that Claude's heat engine would finish temperature and that our job was to finish oxygen/oceans while liquidating into public points.

## 3) Timeline by Generation

- Gen 1: `Earth Catapult`, `Technology Demonstration`, `Martian Survey`, `Standard Technology`, `Acquired Company`, and `Nuclear Power` established discounts, cards, and energy.
- Gen 2: `Search For Life`, `Regolith Eaters`, and `Optimal Aerobraking` created two repeatable VP/terraforming lanes and a space-event rebate.
- Gen 3: `Inventors' Guild` added card selection while `Regolith Eaters` accumulated its first oxygen conversion.
- Gen 4: `Natural Preserve`, `Mass Converter`, `Magnetic Field Generators`, `Local Heat Trapping`, a greenery at `30`, and a Regolith oxygen step produced the first major board/TR jump.
- Gen 5: `Hired Raiders`, `Convoy From Europa`, `Trans-Neptune Probe`, `Commercial District`, and `Research Coordination` improved economy, board position, and tag flexibility.
- Gen 6: `Colonizer Training Camp` made Builder claimable; Builder was immediately claimed, `Water Splitting Plant` was deployed and activated, a greenery went to `38`, and `Virus` plus `Biomass Combustors` suppressed Claude's plant lane.
- Gen 7: `Shuttles` reduced future space costs; `Towing A Comet` placed ocean `32`; greenery `40` made Gardener claimable; Builder and Gardener were secured; `Cartel` and `Building Industries` improved the late economy.
- Gen 8: Terraformer was claimed for a full milestone sweep. `Scientist` was funded, `Cartel` and `Moss` improved production, and oxygen continued through `Water Splitting Plant` and Regolith.
- Gen 9: `Large Convoy`, `Asteroid`, `Satellites`, and `Lava Tube Settlement` converted the engine into oceans, TR, city/greenery points, and income. Greeneries at `47` and `21` reinforced the board lead.
- Gen 10: `Ice Asteroid` placed two oceans, a greenery at `41` completed oxygen with Claude's follow-up, two standard aquifers completed oceans, `Landlord` was funded, `Advanced Ecosystems`, `Windmills`, and `Lagrange Observatory` added direct VP, and `Greenhouses` enabled the final greenery at `53`.

## 4) Strategy Review

### Self
- Core plan: Build a discounted science/space engine, secure milestones through buildings and board conversion, then close through oxygen and oceans while Claude handled temperature.
- Why this macro plan was chosen: `Valley Trust`, `Earth Catapult`, `Mass Converter`, `Optimal Aerobraking`, and strong energy production made science and space cards unusually efficient, while `Regolith Eaters` and `Water Splitting Plant` gave deterministic oxygen control.
- What worked: The discount stack was converted into public parameters rather than endless setup; all three milestones were claimed; `Scientist` and `Landlord` were funded only with durable leads; Claude's plant production was attacked; and the post-terraform prompt was checked before passing.
- What failed: The Gen 6 forecast was only a total range, the Gen 8 forecast was not formally rewritten, and the final-generation liquidation sequence was calculated incrementally rather than written as a complete script before execution.
- Did we drift into an under-defined hybrid line?: `No`. The pivot from outscale to closure was visible in the card and action choices from Gen 7 onward.

### Opponent
- Core plan: `Teractor` earth economy plus `Soletta`, `GHG Factories`, `Lunar Beam`, bacteria, and heat actions to dominate temperature, with `Pets`, `Decomposers`, and `Herbivores` as the card-VP finish.
- How they converted into VP: Claude reached 44 TR, won `Thermalist`, scored 10 card VP, and used three cities for 5 city VP.
- What we failed to deny: `Pets` was protected from removal, and Claude still established several animal/microbe engines. Their slow conversion window was denied by ending in Gen 10 rather than by removing the engines themselves.
- Which explicit engine alarms should have fired: `Soletta` plus 15 heat production was a hard temperature-closure alarm; `Viral Enhancers` plus `Decomposers` and `Herbivores` was a card-VP ceiling alarm. Both correctly pushed us away from more generic setup.

## 5) Critical Turning Points

| Gen | Decision | Why it mattered | VP impact estimate |
|---:|---|---|---:|
| 6 | Play `Colonizer Training Camp`, claim Builder, then deploy `Water Splitting Plant` | Secured 5 milestone VP and made oxygen a deterministic personal track | 9 |
| 7 | Play `Towing A Comet`, place greenery `40`, and claim Gardener | Combined two TR, an ocean, board value, and another 5 milestone VP | 10 |
| 8 | Claim Terraformer and fund Scientist | Completed the 15-VP milestone sweep and locked a durable 5-VP award lead | 10 |
| 10 | `Ice Asteroid`, two aquifers, Landlord, and post-terraform VP liquidation | Finished oceans, secured the second award, and converted the remaining hand/resources into 6+ direct and board VP | 15 |

## 6) Counterfactuals

| Alternative line | Realism | Estimated swing |
|---|---|---:|
| Play `Equatorial Magnetizer` one generation earlier and activate it twice, assuming it does not displace an award or closure action | med | +1 |
| Play `Designed Microorganisms` before the temperature requirement closed, at the cost of delaying part of the Gen 7 milestone/space line | low | 0 |
| Write the entire Gen 10 liquidation order before the first action, including the award, direct-VP cards, post-terraform actions, and final greenery math | high | +1 |

The small estimated swings are important: the executed line was already close to locally optimal. The postmortem should not manufacture a major strategic error in a 36-point win.

## 7) Mistake Taxonomy Tags

- `forecasting_failure`
- `liquidation_plan_missing`
- `tool_payload_shape_mismatch`
- `tool_response_interpretation_error`

## 8) Tool Mismatches

| Tool | Expected | Actual | Root cause | Mitigation |
|---|---|---|---|---|
| `pay_for_project_card` / `submit_multi_actions` | The restarted MCP helper would send the server's lowercase `megacredits` payment field | The loaded helper still normalized to the stale payment shape and the server returned `payment is not a valid type` | Runtime tool schema/client remained stale after the server-side model edit | Use an explicitly wrapped `submit_raw_entity` payload with the complete lowercase payment object; restart/reload the MCP client before the next game |
| `get_game_state` compact player summary | `mc` should show the live megacredit balance | It repeatedly showed `0` while the full player model contained the real lowercase `megacredits` value | Response normalization still reads the old resource field | Inspect the full model or fix compact normalization; do not infer affordability from compact `mc` until fixed |
| Draft `card` prompt | After selecting a card, the next visible card list should clearly indicate whether it is a new draft hand or the still-editable current hand | The still-editable remainder looked like the next draft round, causing one accidental selection change | Prompt title/state does not expose selection lock clearly enough | After each draft choice, wait for the card set to change before selecting again; never choose from a `You can change your selection` remainder |

## 9) Rule Updates (Must Be Actionable)

1. If the Gen 6 forecast is only a total-score range, then stop and write TR, milestones, awards, greenery, city, and card-VP estimates for both players before taking another setup action.
2. If a draft response says the selection can still be changed, then wait for a genuinely new card set instead of selecting from the displayed remainder.
3. If the compact state reports `mc: 0` while legal paid actions remain, then read `raw_player_model.players[*].megacredits` and calculate the liquidation budget from that value.
4. If the game can end this generation, then script closure, awards, direct VP, post-terraform actions, production, and final greenery before executing the first action.

## 10) Active Hypotheses Check

| Hypothesis | Result in this game | Status |
|---|---|---|
| Earlier explicit macro calls reduce hybrid drift and improve late conversion quality | The outscale call had a specific oxygen/board fallback and pivoted cleanly into a Gen 10 close | strengthened |
| Early board and city anchors can offset or prevent a card-VP deficit | The initial city cluster supported 7 city VP, 7 greenery VP, and a 5-point Landlord win while card VP was also won | strengthened |
| Continuing actions after terraforming completion materially changes outcomes | Post-terraform `Windmills`, `Lagrange Observatory`, `Greenhouses`, and final greenery added 3 direct/card/board VP even though the margin was already safe | strengthened |

## 11) Endgame Conversion Review

- Did we write a liquidation plan by Gen 10+?: `Partly`. The ocean/oxygen closure was planned, but the full award-plus-card sequence was improvised in stages.
- Did we check whether actions continued after terraforming completed?: `Yes`
- Which resources were stranded at pass or game end?: After the mandatory production step the model showed `66 MC`, `6 steel`, and `8 heat`; these were generated after action opportunities had ended. Before passing, cash and steel had been spent down and plants were set up for the final greenery.
- Best missed `MC -> VP` conversion: No clear profitable conversion was missed. The alternative `Vesta Shipyard` line could not be combined with both `Lagrange Observatory` and the final-greenery setup using the available pre-production cash.
- Best missed board placement: None with a confident positive swing. Final greenery `53` avoided feeding an opponent city, while the earlier city clusters were fully surrounded.

## 12) Next-Game Checklist

- [x] Strategy call logged by Gen 3.
- [x] Macro call is specific enough to exclude strategic drift.
- [x] Milestone contest plan explicit by Gen 4.
- [x] Award funding lock confidence checked.
- [ ] Card VP race estimate written by Gen 6.
- [ ] Gen 8 score forecast revised after opponent engine update.
- [ ] Endgame conversion plan written at start of final generation.
- [x] After Mars is terraformed, live prompt checked before passing.
