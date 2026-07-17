# Terraforming Mars Postmortem
## Game: `http://localhost:8080/player?id=pfbd56b2de0df`
## Date: `2026-07-17`

## 1) Outcome Snapshot

- Final result: **John 153 - 111 Codex**
- Ended in **Generation 14**
- Board: `tharsis`
- Corporations: `Valley Trust` (Codex) vs. `Vitor` (John)
- Initial strategy call (Gen 2-3): `outscale`
- Did we pivot? `yes`
- Pivot generation: `12`
- Was the macro call actually specific enough to constrain play? `no`

The opening had the shell of an engine plan: Valley Trust, Earth Catapult, Mass Converter, AI Central, science tags, and space discounts. The call failed the strategy guide's actual outscale test, however, because it never established a credible route to beat John's projected `card VP + city VP`. By the time the plan became a hard-close line, John already had Mars University, Research Outpost, Io Mining Industries, Callisto Penal Mines, Shuttles, Vesta Shipyard, and multiple animal/microbe scorers. Gen 13 closed oxygen and oceans, but temperature survived into Gen 14, giving the stronger engine one decisive extra generation.

## 2) Score Decomposition

| Category | Self | Opponent | Delta (Opp - Self) |
|---|---:|---:|---:|
| TR | 52 | 57 | +5 |
| Milestones | 10 | 5 | -5 |
| Awards | 10 | 10 | 0 |
| Greenery | 10 | 7 | -3 |
| City | 5 | 11 | +6 |
| Card VP | 24 | 63 | +39 |
| **Total** | **111** | **153** | **+42** |

The loss was overwhelmingly a scoring-ceiling loss. Public scoring was competitive: Codex led milestones and greenery and tied awards. John won only 11 more points across TR and city after those offsets, but won card VP by 39.

## 2A) Forecast Accuracy

No category-by-category Gen 6 forecast was written during the game. The table below is a reconstruction of the implicit expectations visible in the line, not a contemporaneous forecast. That is itself a process failure.

| Category | Self Forecast | Self Actual | Opp Forecast | Opp Actual |
|---|---:|---:|---:|---:|
| TR | 50 | 52 | 50 | 57 |
| Awards | 10 | 10 | 10 | 10 |
| Greenery | 9 | 10 | 7 | 7 |
| City | 7 | 5 | 9 | 11 |
| Card VP | 28 | 24 | 42 | 63 |

- What did the forecast miss? John's card ceiling by roughly 21 VP, the +8 TR burst from `Terraforming Ganymede`, the scale of his Jovian package, and the compounding value of Predators, Herbivores, Small Animals, and Tardigrades.
- Did we think we were ahead because of TR while actually behind on VP ceiling? Not exactly: Codex was not relying on TR alone, but the public-point lead was treated as if it could compensate for an unmeasured card-VP deficit. It could not.
- Gen 8 revision: none was formally written. Visible alarms were noted tactically, but they did not force an immediate macro recommit.

## 3) Timeline by Generation

- Gen 1-3: Valley Trust used preludes and early science/card-flow plays to establish a broad engine. `Arctic Algae`, `Technology Demonstration`, `Business Network`, and science-tag flexibility created options, but the macro call remained the content-light label `outscale` rather than a category win condition.
- Gen 4-5: `AI Central`, `Mass Converter`, energy production, and card draw made the engine operational. John developed Vitor rebates, building/space production, and early microbe infrastructure.
- Gen 6-7: `Earth Catapult`, `Space Station`, `Gene Repair`, and other discounts improved efficiency. Codex began accumulating the building count and hand size needed for Builder and Planner, while John assembled Mars University, Research Outpost, Shuttles, Vesta Shipyard, and stronger titanium/Jovian production.
- Gen 8-9: Codex secured `Builder` and `Planner` and expanded the red board cluster around city `18`. John claimed `Terraformer` and continued into Io Mining Industries, Callisto Penal Mines, Small Animals, Herbivores, and Predators. This was the point where the outscale thesis should have been rejected.
- Gen 10-11: Codex kept adding useful but diffuse infrastructure—Standard Technology, Mining Area/Rights, Immigrant City, Advanced Ecosystems, and production cards—without matching John's scalable card-VP ceiling. The Gen 8 score forecast and discount-stack alarm were still not formalized.
- Gen 12: The plan finally pivoted toward closure and scoring. Codex funded Scientist, protected a Landlord lead, and prepared oxygen/ocean/temperature conversion, but the pivot came after John's engine had already become the favorite in any extra generation.
- Gen 13: Codex executed a strong closure sequence: `Towing A Comet`, greenery `11`, `Nuclear Zone`, heat conversion, `Lava Flows`, bonus ocean `63`, and a standard asteroid. Oxygen and oceans maxed; temperature reached +4 during Codex's line and +6 after John's conversion. Codex also played `Interstellar Colony Ship`, `Decomposers`, `CEO's Favorite Project`, used AI Central, and placed greeneries at `35` and `24`. John deliberately exhausted actions and allowed production into Gen 14 rather than ending immediately.
- Gen 14: Codex bought and played `Eos Chasma National Park`, `Mangrove`, and `Tectonic Stress Power`; used Electro Catapult and AI Central; drew and played `Lagrange Observatory`; placed greeneries at `07` and `12`; and used Business Network to find `Asteroid Mining Consortium`. John finished temperature, then converted his superior engine into `Physics Complex`, `Fish`, `Methane From Titan`, `Water Import From Europa`, `Terraforming Ganymede`, `Media Archives`, `Capital`, `Noctis Farming`, `Grass`, and two final greeneries.

## 4) Strategy Review

### Self
- Core plan: Build a Valley Trust science/discount engine, claim Planner and Builder, control the board and awards, then pivot to terraforming closure.
- Why this macro plan was chosen: The opening offered excellent draw and discount infrastructure, and Valley Trust naturally rewards science density.
- What worked: Both targeted milestones were claimed; Landlord was won 13-9; Scientist still returned 5 VP through a tie; greenery finished 10-7; the Gen 13-14 liquidation was disciplined; and post-terraform actions were correctly exhausted.
- What failed: The engine produced flexibility rather than a competitive VP ceiling. Only one city was established, card VP remained mostly fixed rather than scalable, the Gen 6/8 forecast checkpoints were skipped, and closure began several generations after John's discount/Jovian/animal stack became visible.
- Did we drift into an under-defined hybrid line?: `yes`. The label was `outscale`, but the actual line mixed engine pieces, milestone setup, production, board control, and late closure without proving which final categories would beat John.

### Opponent
- Core plan: Vitor rebates plus science discounts, card cycling, titanium/Jovian production, and animal/microbe accumulators.
- How they converted into VP: 63 card VP, including `Predators` 9, `Io Mining Industries` 8, `Water Import From Europa` 8, `Tardigrades` 3, `Small Animals` 3, `Herbivores` 3, `Anti-Gravity Technology` 3, and a broad set of one- and two-point cards. `Terraforming Ganymede` also delivered 8 TR in the final action stack.
- What we failed to deny: The extra generation itself. Once direct card denial was unavailable, the only realistic denial was earlier closure.
- Which explicit engine alarms should have fired: Mars University plus Research Outpost; Io Mining plus Callisto; Shuttles/Vesta Shipyard; and, finally, Anti-Gravity Technology. The combination was already beyond a fair outscale race before Anti-Gravity appeared.

## 5) Critical Turning Points

| Gen | Decision | Why it mattered | VP impact estimate |
|---:|---|---|---:|
| 8 | Continue the outscale thesis after John's science, titanium, and Jovian package was visibly live | Preserved the game length that John's engine needed instead of making closure the only priority | 12 |
| 10 | Continue broad infrastructure without a written `card VP + city VP` forecast | Codex's engine stayed efficient but did not acquire a scalable scoring lane or enough city anchors | 8 |
| 12 | Pivot to hard close | The pivot was directionally correct, but two to four generations later than the alarm threshold required | 10 |
| 13 | Max oxygen and oceans but leave two temperature steps for another generation | Gen 14 enabled John's largest VP/TR conversion burst; the immediate Gen 13 line itself was close to locally optimal, so the root cause was earlier closure capacity | 18 |

## 6) Counterfactuals

| Alternative line | Realism | Estimated swing |
|---|---|---:|
| Treat the Mars University/Research Outpost plus Io/Callisto/Shuttles package as a hard-close alarm by Gen 8-9 and prioritize global steps over generic setup | med | +18 |
| Build a second city anchor and reserve more greeneries for city adjacency instead of relying on one fully surrounded city at `18` | med | +6 |
| Require a scalable card-VP lane by Gen 7—Jovians, protected animals, or resource VP—and reject `outscale` if none is available | med | +10 |
| Script enough temperature capacity before Gen 13 to finish all remaining steps in the same generation | low | +15 |

These swings overlap and should not be added. No single tactical correction erases 42 VP; the realistic win path required changing both game length and scoring architecture several generations earlier.

## 7) Mistake Taxonomy Tags

- `strategy_misread`
- `late_strategy_pivot`
- `hybrid_drift`
- `insufficient_card_vp_scaling`
- `forecasting_failure`
- `opponent_engine_underrated`
- `discount_stack_ignored`
- `vp_ceiling_miscalculated`
- `alarm_threshold_missed`

## 8) Tool Mismatches

| Tool | Expected | Actual | Root cause | Mitigation |
|---|---|---|---|---|
| Typed project-card payment helper | Submit the nested project-card choice with the server's accepted full payment object | Nested payment submission failed; explicitly wrapped `submit_raw_entity` with lowercase `megacredits` worked | Loaded helper/schema normalization did not match the live server payload | Continue using the strict raw outer-`or` payload until the typed helper is verified by tests and a live smoke test |
| `select_space` | Commit the placement and return when control came back | The greenery at `12` committed, but the call waited on John's turn and timed out after 600 seconds | Response helper coupled successful mutation to opponent-turn polling | After a timeout, verify game age/board state before retrying; never resubmit a placement that may already have committed |

The rejected Asteroid Mining Consortium payment was not a tool defect. The card has a Jovian tag but no space tag, so titanium was not legal payment; the corrected 11 M€ payment succeeded.

## 9) Rule Updates (Must Be Actionable)

1. If an `outscale` call cannot show a plausible advantage in projected `card VP + city VP` by Gen 6, then revoke the call and switch to hard close or a named scoring lane.
2. If John has Mars University or equivalent card cycling plus two of Research Outpost, Shuttles, Io Mining, Callisto, or another discount/production multiplier by Gen 8, then treat every non-scoring setup action as suspect and calculate the fastest closure line.
3. If only one city anchor exists by Gen 7 and its adjacency ring is nearly full, then either establish a second city immediately or stop valuing future greeneries as city-multiplied points.
4. If the game is likely to end in the next two generations, then count exact remaining global steps and assign a funded action/card to every step before spending on direct VP.
5. If a mutating MCP call times out while waiting for the opponent, then inspect the state before retrying because the mutation may already be committed.

## 10) Active Hypotheses Check

| Hypothesis | Result in this game | Status |
|---|---|---|
| Earlier explicit macro calls reduce hybrid drift and improve late conversion quality | A macro label existed, but it lacked a category forecast and did not constrain play; the game drifted until Gen 12 | weakened |
| Early city anchors can offset or prevent a card-VP deficit | One city scored only 5 against John's 11 city VP and could not offset the 39-point card gap | weakened |
| Continuing actions after terraforming completion materially changes outcomes | Codex added multiple direct/card/board VP after terraforming completed and avoided a repeat of the prior pass error | strengthened |

## 11) Endgame Conversion Review

- Did we write a liquidation plan by Gen 10+?: `Partly`. A detailed Gen 13 closeout was reconstructed and followed, but no complete Gen 10-12 closure script existed before the pivot.
- Did we check whether actions continued after terraforming completed?: `yes`
- Which resources were stranded at pass or game end?: Pre-pass resources were effectively exhausted: 4 M€ and 2 plants had no legal positive conversion. The final model's 65 M€ was post-action/production state and not an available missed conversion window.
- Best missed `MC -> VP` conversion: None in the final action sequence. Business Network turned the last viable 14 M€ into the 1-VP Asteroid Mining Consortium; the larger miss was earlier strategic allocation.
- Best missed board placement: No clear late placement error. The material board miss was failing to establish a second city anchor in the midgame.
- Endgame execution verdict: Strong locally, insufficient strategically. Gen 13-14 liquidation raised Codex to 111, but it could not repair the ceiling gap created earlier.

## 12) Next-Game Checklist

- [x] Strategy call logged by Gen 3.
- [ ] Macro call is specific enough to exclude strategic drift.
- [x] Milestone contest plan explicit by Gen 4.
- [ ] Award funding lock confidence checked; Scientist ended tied rather than uniquely held.
- [ ] Card VP race estimate written by Gen 6.
- [ ] Gen 8 score forecast revised after opponent engine update.
- [ ] Endgame conversion plan written at start of final generation; the detailed script began during Gen 13.
- [x] After Mars is terraformed, live prompt checked before passing.
