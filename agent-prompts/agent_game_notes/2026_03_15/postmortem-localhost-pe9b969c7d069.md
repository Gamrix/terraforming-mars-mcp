# Terraforming Mars Postmortem
## Game: `http://localhost:8080/player?id=pe9b969c7d069`
## Date: `2026-03-15`

## 1) Outcome Snapshot

- Final result: **Codex 101 - 99 Claude**
- Opponent: `Claude`
- Ended in **Generation 12**
- Board: `tharsis`
- Initial strategy call (Gen 2-3): `hybrid leaning close`
- Did we pivot? `yes`
- Pivot generation: `8`
- Was the macro call actually specific enough to constrain play? `yes`

## 2) Score Decomposition

| Category | Self | Opponent | Delta (Opp - Self) |
|---|---:|---:|---:|
| TR | 48 | 49 | +1 |
| Milestones | 5 | 10 | +5 |
| Awards | 10 | 5 | -5 |
| Greenery | 8 | 10 | +2 |
| City | 16 | 0 | -16 |
| Card VP | 14 | 25 | +11 |
| **Total** | 101 | 99 | -2 |

## 2A) Forecast Accuracy

Record the best in-game forecast you had by Gen 6 to 8.

| Category | Self Forecast | Self Actual | Opp Forecast | Opp Actual |
|---|---:|---:|---:|---:|
| TR | 44 | 48 | 46 | 49 |
| Awards | 10 | 10 | 5 | 5 |
| Greenery | 7 | 8 | 8 | 10 |
| City | 14 | 16 | 0 | 0 |
| Card VP | 12 | 14 | 20 | 25 |

- What did the forecast miss? Claude's late `Farming`, `Rover Construction`, `Vesta Shipyard`, and repeated action-card liquidation added more greenery/card-VP than the Gen 8 forecast allowed.
- Did we think we were ahead because of TR while actually behind on VP ceiling? `No`. The in-game read was that we were behind on long-run ceiling and had to win on city plus awards before Claude's card-VP edge fully converted.

## 3) Timeline by Generation

- Gen 1: `Cheung Shing MARS` opened with `Experimental Forest` and `Mohole`, then established `Colonizer Training Camp`, `Inventors' Guild`, and `ArchaeBacteria`.
- Gen 2: `Restricted Area`, `Import of Advanced GHG`, and `SF Memorial` built a science-plus-closure shell instead of a pure rush shell.
- Gen 3: `Natural Preserve`, `Industrial Microbes`, and `Research` made the board anchor and science count real.
- Gen 4: `Land Claim` plus `Domed Crater` committed to a city cluster instead of floating on TR only.
- Gen 5: `Toll Station`, `Great Escarpment Consortium`, and `Trans-Neptune Probe` improved economy while also denying Claude's `Miner` line.
- Gen 6: `Mass Converter`, `Big Asteroid`, and `Comet` created the real closure pivot while stripping plants and finishing oceans.
- Gen 7: `Cupola City`, `Grass`, and `Scientist`/`Thermalist` funding pushed into a real city-award plan.
- Gen 8: The macro call became hard close once Claude's titanium/space line looked durable; we drafted denial/liquidation cards rather than more setup.
- Gen 9: `Nitrogen-Rich Asteroid` and continued board conversion kept pace pressure on while preserving the lower-right city cluster.
- Gen 10: `Ecological Zone` and continued action-card usage added a second VP lane instead of leaning only on TR and awards.
- Gen 11: `Eos Chasma National Park`, `Mangrove`, `Space Station`, and a greenery conversion were efficient but did not actually end the game.
- Gen 12: `Immigrant City`, `Imported Nitrogen`, `Underground City`, standard greenery, and final greenery liquidation produced the winning city delta.

## 4) Strategy Review

### Self
- Core plan: Early board-and-science setup into a hybrid leaning close line, then a hard-close liquidation plan once Claude's space economy became the main threat.
- Why this macro plan was chosen: The opening hand supported a compact science engine and discounted buildings, but not a true long-game card-VP race.
- What worked: We made a real macro call, built city adjacency early, funded only awards we could plausibly hold, and continued acting after terraforming completion.
- What failed: Forecasting still understated Claude's late card-VP/public-point cleanup, and some city placements were good rather than perfect because we improvised around legality.
- Did we drift into an under-defined hybrid line?: `No`. This was much more constrained than the older games.

### Opponent
- Core plan: Claude played `Point Luna` into an earth/space/titanium economy with blue-card actions, then converted the long game through `Security Fleet`, `Space Elevator`, `Farming`, and late Jovian/space VP.
- How they converted into VP: Claude won `Gardener` and `Builder`, took `Miner`, stayed roughly even on TR, and generated `25` card VP while adding late greeneries.
- What we failed to deny: We did not stop the sustained action economy from `Security Fleet`, `Space Elevator`, `Development Center`, and related draw/value turns.
- Which explicit engine alarms should have fired: By Gen 8 the alarm was "Claude can keep converting titanium and action cards for the rest of the game even without John's science-discount pattern", which meant our finish window was narrower than a normal Gen 12.

## 5) Critical Turning Points

| Gen | Decision | Why it mattered | VP impact estimate |
|---:|---|---|---:|
| 6 | `Mass Converter` into `Big Asteroid` and `Comet` | This created the tempo lead and plant denial needed to keep Claude from an even bigger greenery finish | 8 |
| 7 | `Cupola City` plus committed `Scientist` and `Thermalist` funding | This locked in the city-award win condition we eventually needed | 9 |
| 12 | `Immigrant City` + `Imported Nitrogen` + `Underground City` + double greenery liquidation | This was the exact conversion package that turned a likely close loss into a 2 VP win | 14 |

## 6) Counterfactuals

| Alternative line | Realism | Estimated swing |
|---|---|---:|
| Place the Gen 12 city package even more efficiently by precomputing all legal adjacency squares before paying for `Immigrant City` and `Underground City` | med | 3 |
| Treat Claude's action-economy engine as a harder closure alarm one generation earlier and convert one extra Gen 9-10 action into board VP | med | 4 |
| Skip a low-impact midgame setup card in favor of one earlier direct VP conversion to reduce dependence on perfect Gen 12 liquidation | low | 3 |

## 7) Mistake Taxonomy Tags

- `vp_ceiling_miscalculated`
- `opponent_engine_underrated`
- `inefficient_city_placement`

## 8) Tool Mismatches

| Tool | Expected | Actual | Root cause | Mitigation |
|---|---|---|---|---|
| `choose_or_option` / `select_space` | Direct greenery-space submit should succeed from the greenery prompt | The first direct `select_space` failed because the prompt still needed the enclosing `or` response shape | Branch-specific prompt handling | When `waiting_for.input_type` is `or`, always route greenery placement through the `or` wrapper first even if the nested action is a space selection |

## 9) Rule Updates (Must Be Actionable)

1. If the opponent is `Claude`, then do not reuse John's specific science-discount alarm thresholds; classify the actual live engine before deciding how hard to close.
2. If a Gen 12 city line is likely to decide the game, then inspect legal city spaces before paying so the best adjacency square is not lost to avoidable placement errors.
3. If Mars becomes terraformed and actions still continue, then script both the post-terraform action order and the mandatory final greenery placement before passing.

## 10) Active Hypotheses Check

List 1 to 3 hypotheses that were being tested in this game.

| Hypothesis | Result in this game | Status |
|---|---|---|
| Earlier explicit macro calls reduce hybrid drift and improve conversion quality | The game had a clear macro path and much cleaner late decisions than the older losses | strengthened |
| Early city anchors can offset a card-VP deficit if the finish is forced tightly enough | We still lost card VP badly, but the city delta was the main reason we won | strengthened |
| Continuing actions after terraforming completion materially changes close games | The Gen 12 post-terraform sequence and final greenery absolutely mattered | strengthened |

## 11) Endgame Conversion Review

- Did we write a liquidation plan by Gen 10+?: `Yes`, but it was partly improvised at placement level.
- Did we check whether actions continued after terraforming completed?: `Yes`
- Which resources were stranded at pass or game end?: `66 MC`, `4 steel`, `36 heat` remained after production because the game had already ended and no further scoring conversion existed.
- Best missed `MC -> VP` conversion: Better legal planning for the two late city cards was the main missed edge; after that, there was no comparable cash conversion left.
- Best missed board placement: One of the Gen 12 city placements was probably improvable if legal adjacency had been mapped before paying.

## 12) Next-Game Checklist

- [x] Strategy call logged by Gen 3.
- [x] Macro call is specific enough to exclude strategic drift.
- [x] Milestone contest plan explicit by Gen 4.
- [x] Award funding lock confidence checked.
- [x] Card VP race estimate written by Gen 6.
- [x] Gen 8 score forecast revised after opponent engine update.
- [x] Endgame conversion plan written at start of final generation.
- [x] After Mars is terraformed, live prompt checked before passing.
