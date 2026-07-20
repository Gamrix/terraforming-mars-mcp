# Terraforming Mars Postmortem
## Game: `http://localhost:8080/player?id=p828080340352`
## Date: `2026-07-19`

## 1) Outcome Snapshot

- Final result: **John 119 - 90 Codex**
- Ended in **Generation 11**
- Board: `tharsis`
- Corporations: `Valley Trust` (Codex) vs. `Ecoline` (John)
- Initial strategy call (Gen 2-3): `outscale`, revised to `hard close` during Gen 3
- Did we pivot?: `yes`
- Pivot generation: `3`
- Was the macro call actually specific enough to constrain play?: `partly`

The pivot itself was timely. `Earth Catapult`, `Business Network`, `Space Station`, and `Research Outpost` correctly triggered a hard-close response in Gen 3. The problem was that "hard close" named a posture but did not prove a finish date. By Gen 6 the category forecast already made Codex an underdog, and by Gen 8 the fastest credible finish still appeared to be Gen 11. Against John's discount, draw, accumulator, and emerging Jovian multipliers, a Gen 11 finish required a much larger locked VP floor than Codex had.

## 2) Score Decomposition

| Category | Self | Opponent | Delta (Opp - Self) |
|---|---:|---:|---:|
| TR | 50 | 45 | -5 |
| Milestones | 10 | 5 | -5 |
| Awards | 5 | 10 | +5 |
| Greenery | 9 | 6 | -3 |
| City | 6 | 9 | +3 |
| Card VP | 10 | 44 | +34 |
| **Total** | **90** | **119** | **+29** |

Codex won TR, milestones, and greenery by 13 combined points. John erased that entire public-point edge with awards and city, then won the game through a 34-point card-VP advantage. `Ants` scored 8; `Ganymede Colony` and `Water Import From Europa` scored 6 each; the remaining animal, microbe, science, and fixed-VP cards supplied the rest.

## 2A) Forecast Accuracy

The following ranges were explicitly recorded in Gen 6.

| Category | Self Forecast | Self Actual | Opp Forecast | Opp Actual |
|---|---:|---:|---:|---:|
| TR | 45-50 | 50 | 42-48 | 45 |
| Awards | 5-10 | 5 | 5-10 | 10 |
| Greenery | 8-10 | 9 | 7-10 | 6 |
| City | 7-10 | 6 | 6-10 | 9 |
| Card VP | 15-22 | 10 | 30-40 | 44 |

- What did the forecast miss? The direction was correct, but it overcounted Codex's held and contingent card VP by 5-12, understated John's upper card-VP tail by at least 4, and treated Banker as a likely self award without modeling John's tag-based production burst.
- Did we think we were ahead because of TR while actually behind on VP ceiling? `No`. The game correctly identified the VP-ceiling problem. The failure was turning that diagnosis into a winning schedule and adequate scoring floor.
- Gen 8 revision: hard close was reaffirmed, with temperature identified as the first bottleneck and oxygen as the next. The revision still did not state the earliest feasible finish or the minimum locked VP required if the finish remained Gen 11.

## 3) Timeline by Generation

- Gen 1: Valley Trust opened with `Allied Bank`, `Supply Drop`, and `Eccentric Sponsor` into `Space Elevator`. `Industrial Microbes`, `Designed Microorganisms`, and `Imported Hydrogen` established a flexible production and ocean shell.
- Gen 2: `Corporate Stronghold` at 35, greenery 27, and `Restricted Area` at 55 created the first city/greenery anchor. `Gene Repair`, `Wave Power`, and other options entered hand.
- Gen 3: The initial outscale lean was revoked after John's discount/card-flow engine became visible. Codex played `Plantation`, `Hired Raiders`, and `Vesta Shipyard`; John completed the alarm stack with `Research Outpost`.
- Gen 4: `Viral Enhancers`, greenery 26, `Gardener`, and `Aquifer Pumping` strengthened the plant/ocean closure line.
- Gen 5: `Mineral Deposit`, `Comet`, an Aquifer ocean, `Wave Power`, and `Robotic Workforce` accelerated globals and production. `Water Splitting Plant` entered the tableau, but lacked energy support.
- Gen 6: The category forecast correctly identified a hard-close requirement. Codex denied `AI Central` and `Shuttles`, played `Nitrite Reducing Bacteria`, funded Banker, and used `Hackers` to attack John's MC production. Banker looked favorable on the current scoreboard but was not stress-tested against John's visible Earth/building tags and card velocity.
- Gen 7: `Big Asteroid`, another ocean, and the `Terraformer` milestone pushed the public-point lead. `Olympus Conference` added only modest card value.
- Gen 8: Hard close was reaffirmed. `Methane From Titan` and `Mohole Area` built plant/heat capacity; John added `Deimos Down`, `Domed Crater`, `Pets`, and more accumulator infrastructure.
- Gen 9: `Kelp Farming`, greenery 37, `Geothermal Power`, and `Fusion Power` prepared reliable oxygen conversion. John drove temperature to 0 C and oceans to eight. Codex sold most of the hand to preserve a final-ocean plan, but the liquidation model mixed locked points with speculative held-card VP.
- Gen 10: `Large Convoy` completed oceans, `Ecological Zone` created a scoring tile, and greeneries plus `Water Splitting Plant` advanced oxygen. Codex funded and ultimately won Landlord. John funded Scientist, moved Banker into a tie, and expanded science/card velocity with `Mars University`, `Research`, and `Mass Converter`.
- Gen 11: Two heat conversions completed temperature. `Immigrant City`, `Magnetic Field Generators`, and two plant conversions completed oxygen while adding efficient TR and board VP. Codex correctly continued after terraforming, played and activated `Security Fleet`, exhausted useful actions, and placed a final greenery. John converted the last action phase into `Ganymede Colony`, `Water Import From Europa`, `Advanced Ecosystems`, `Decomposers`, `Livestock`, and accumulator actions, then won Banker 30-12.

## 4) Strategy Review

### Self

- Core plan: Build an early city/greenery and ocean shell, then hard-close before John's discount engine could convert its hand into card VP.
- Why this macro plan was chosen: The opening had strong terraforming cards and public-point access, while John's Gen 3 discounts made a long engine race clearly unfavorable.
- What worked: The Gen 3 pivot was early; the Gen 6 forecast was written; AI Central and Shuttles were denied; two milestones were secured; the board produced 15 combined greenery/city VP; Landlord was won 14-13; all globals were finished in Gen 11; post-terraform liquidation was correctly executed; and no useful pre-pass resources were stranded.
- What failed: The hard-close call lacked an earliest-finish schedule. Codex's forecast counted unplayed cards as if their VP were funded and executable. Banker was funded from a current lead rather than a burst-tested final projection. The plan therefore entered Gen 11 with only 10 net card VP against an opponent whose hidden Jovian and accumulator ceiling was far above the forecast midpoint.
- Did we drift into an under-defined hybrid line?: `No` after Gen 3. Most later engine cards supported closure. The deeper problem was that a genuine hard-close line was still too slow to win without a larger VP floor.

### Opponent

- Core plan: Ecoline board pressure backed by Earth/science discounts, Business Network and Mars University card velocity, titanium/Jovian scaling, and animal/microbe accumulators.
- How they converted into VP: 44 card VP, 10 awards, and 9 city VP. The final-generation Jovian pair alone scored 12; `Ants` scored 8; late ecosystem and animal cards converted cheap tags and actions into another scoring layer.
- What we failed to deny: The value of Gen 11 itself, the Banker production burst, and vulnerable Nitrite resources that Ants repeatedly stole. The draft denied two premium engine cards, but direct denial could not stop cards found through repeated draw/cycling.
- Which explicit engine alarms should have fired: The Gen 3 discount alarm did fire. A second, different alarm should have fired by Gen 9-10: four or more effective Jovian tags plus heavy card velocity means unseen Jovian multipliers can represent 10-20 hidden VP in the final generation. Banker also required a production-burst alarm once John had large Earth/building tag counts.

## 5) Critical Turning Points

| Gen | Decision | Why it mattered | VP impact estimate |
|---:|---|---|---:|
| 6 | Fund Banker from a large current lead without a two-card burst test | John later used Medical Lab, Space Hotels, Miranda Resort, and Insulation to reach 30 MC production and take the award Codex funded | 5 |
| 6-8 | Treat hard close as a stance without proving the earliest finish generation | The forecast showed Codex behind, but the plan did not ask whether a likely Gen 11 finish was itself losing or what locked VP floor was required | 8 |
| 9 | Count held, conditional card VP inside the expected 15-22 point card lane | The final tableau delivered only 10 net card VP, so the projected scoring floor was never real | 7 |
| 10-11 | Allow a final generation against John's draw, discount, accumulator, and Jovian shell | John converted Gen 11 into roughly 20 late card VP, including 12 from the two Jovian multipliers | 18 |

## 6) Counterfactuals

| Alternative line | Realism | Estimated swing |
|---|---|---:|
| Do not fund Banker unless the lead survives a two-card production burst based on John's visible Earth/building tags; preserve the award slot for Landlord alone | high | +5 |
| At Gen 6, split the card forecast into locked versus contingent VP and require a 15-point locked card/city floor before assuming a Gen 11 close can win | high | +7 |
| By Gen 8, script every remaining global step and prioritize one additional oxygen step early enough to make a Gen 10 finish credible | low | +15 |
| Once John has four effective Jovian tags and strong card velocity, add a 10-20 VP hidden-multiplier reserve to his ceiling and draft/play immediate VP accordingly | med | +10 |

These swings overlap. The clearest correction is not that one tactical move threw the game; it is that the forecast correctly identified danger but used contingent self VP and an untested award to conclude the remaining gap was manageable.

## 7) Mistake Taxonomy Tags

- `rush_without_closure`
- `insufficient_card_vp_scaling`
- `forecasting_failure`
- `award_funding_mislock`
- `vp_ceiling_miscalculated`

## 8) Tool Mismatches

| Tool | Expected | Actual | Root cause | Mitigation |
|---|---|---|---|---|
| Mutating MCP calls that wait through the opponent turn | Return promptly after the mutation committed | Several calls remained open while John acted | The helper couples a successful mutation to opponent-turn polling | Continue sending progress updates and inspect live state before any retry; this caused no VP loss |
| Imported GHG payment | Pay with the intended cash/titanium mix | The first payment was rejected because only 2 M€ remained, not 4 | Operator balance arithmetic, not a tool defect | Read the full player model before mixed-resource payment when compact state omits balances |

No tooling issue changed a strategic decision or final score.

## 9) Rule Updates (Must Be Actionable)

1. If the macro call is `hard close`, then write the earliest feasible finish generation and assign a source to every remaining global step; if the earliest finish is Gen 11+ against a live John engine, add a locked VP/denial plan because closure alone is not a win condition.
2. If forecasting card VP, then separate `locked` VP already played or fully funded from `contingent` VP in hand; use only locked plus budgeted VP when deciding whether the current line is ahead.
3. If funding Banker against a draw/discount engine, then stress-test the lead against the opponent's best plausible two-card production burst from visible Earth/building tags; do not fund if that burst flips the award and no response is reserved.
4. If the opponent has four or more effective Jovian tags plus strong draw or space discounts, then add 10-20 hidden VP to the one-extra-generation forecast for unseen Jovian multipliers.
5. If the opponent has an unused stealing accumulator such as Ants, then do not add a vulnerable resource unless it can be converted before the opponent's next action or the immediate benefit exceeds the VP fed to the accumulator.
6. If buying a card in Gen 10+, then include its exact play action and payment in the liquidation script; otherwise do not pay the 3 M€ research cost.

## 10) Active Hypotheses Check

| Hypothesis | Result in this game | Status |
|---|---|---|
| Hard-close commitment by Gen 8 performs better than hybrid drift against John's science engine | The game pivoted in Gen 3 and finished in Gen 11, but hard close alone did not overcome a 34-point card-VP deficit | weakened; revise to require a finish date and VP floor |
| Early city anchors can offset or prevent a card-VP deficit | Two cities produced 6 VP and the board package stayed competitive, but it could not offset John's card ceiling | strengthened, with a clear upper bound |
| Continuing actions after terraforming completion materially changes outcomes | Codex correctly added Security Fleet VP and a final greenery after completion rather than passing early | strengthened |

## 11) Endgame Conversion Review

- Did we write a liquidation plan by Gen 10+?: `yes`, though it was refined action by action rather than fully scripted before the first Gen 10 action.
- Did we check whether actions continued after terraforming completed?: `yes`
- Which resources were stranded at pass or game end?: No useful pre-pass conversion was missed. The final model's 78 M€ and production resources were post-production state after the action phase had ended.
- Best missed `MC -> VP` conversion: No clear final-action conversion. The material cash error was paying 3 M€ for Solar Power in Gen 10 and later selling it for 1 M€ without playing it.
- Best missed board placement: None material. Greenery 30 correctly doubled Immigrant City value, greenery 39 captured the two-plant refund, and final greenery 40 avoided feeding an opposing city.
- Endgame execution verdict: Strong. The loss was primarily evaluation and planning: contingent VP overcount, award durability misread, and insufficient scoring floor for the earliest credible close.

## 12) Next-Game Checklist

- [x] Strategy call logged by Gen 3.
- [x] Macro call was specific enough to stop hybrid drift.
- [x] Milestone contest plan explicit by Gen 4.
- [ ] Award funding lock confidence stress-tested against plausible burst cards.
- [x] Card VP race estimate written by Gen 6.
- [x] Gen 8 score forecast revised after opponent engine update.
- [ ] Earliest finish generation and source for every remaining global step written with the hard-close call.
- [ ] Forecast separated locked VP from contingent VP.
- [x] Endgame conversion plan written by Gen 10+.
- [x] After Mars was terraformed, live prompt checked before passing.
