# Terraforming Mars Postmortem
## Game: `http://localhost:8080/player?id=pef7a44ee9077`
## Date: `2026-03-10`

## 1) Outcome Snapshot

- Final result: **John 181 - 97 Codex**
- Ended in **Generation 13**
- Board: `tharsis`
- Initial strategy call (Gen 2-3): `hybrid`
- Did we pivot? `yes`
- Pivot generation: `8`

## 2) Score Decomposition

| Category | Self | Opponent | Delta (Opp - Self) |
|---|---:|---:|---:|
| TR | 45 | 53 | 8 |
| Milestones | 10 | 5 | -5 |
| Awards | 5 | 10 | 5 |
| Greenery | 9 | 12 | 3 |
| City | 11 | 17 | 6 |
| Card VP | 17 | 84 | 67 |
| **Total** | 97 | 181 | 84 |

## 3) Timeline by Generation

- Gen 1: CrediCor opener into `Io Research Outpost`, `Supplier`, `Lagrange Observatory`, `Adaptation Technology`, and immediate `AI Central`.
- Gen 2: `Hired Raiders` denied steel, `Arctic Algae` came down against `Water Import From Europa`, and `Industrial Microbes` stabilized the building line.
- Gen 3: `Cupola City` on `19`, funded `Scientist`, and restored energy with `Power Plant`.
- Gen 4: `Protected Valley` plus `Mineral Deposit` improved board presence and MC production.
- Gen 5: `Imported Hydrogen` and `Underground City` built the central board cluster while `Virus` and later plant denial slowed our greenery timing.
- Gen 6: `Space Station`, `Ice Asteroid`, and a plant greenery on `27` were the major conversion turn.
- Gen 7: `Phobos Space Haven`, `Mayor`, and `Great Escarpment Consortium` secured public points and denied steel production.
- Gen 8: Claimed `Gardener`, funded `Miner`, played `Flooding`, and used `Great Dam` to reopen energy.
- Gen 9: `Subterranean Reservoir`, multiple greeneries, `Mining Expedition`, `Deep Well Heating`, and `Grass` continued direct terraforming.
- Gen 10: `Deimos Down` cleared plants and accelerated temperature; `Tundra Farming` and `Wave Power` converted more efficient points.
- Gen 11: `Herbivores`, more greenery, `Satellites`, and `Gene Repair` improved final VP lanes.
- Gen 12: Maxed temperature with heat plus `Nitrogen-Rich Asteroid`; standard greenery and `Shuttles` closed more board value.
- Gen 13: Final conversion sequence with `Birds`, standard greenery, `Noctis City`, `Worms`, and final greenery at end of game.

## 4) Strategy Review

### Self
- Core plan: Hybrid science-board line with early `AI Central`, then pivot into public points, board clustering, and later terraforming closure.
- What worked: Milestone game was much stronger than prior losses, the board was materially better, and the `Miner` funding was correct and held.
- What failed: Card VP remained far too low, `Scientist` was funded too early and flipped, and too much steel/MC remained trapped in non-scoring lines for too long.

### Opponent
- Core plan: Saturn Jovian/titanium economy into discount stack, card draw, and late plant/animal/card-VP conversion.
- How they converted into VP: Massive card VP from Jovians, `Security Fleet`, `Fish`, `Small Animals`, and other engine pieces, backed by strong TR and city scoring.
- What we failed to deny: The `Earth Office` / `Earth Catapult` / `Anti-Gravity Technology` discount stack, plus the late animal and Jovian ceiling.

## 5) Critical Turning Points

| Gen | Decision | Why it mattered | VP impact estimate |
|---:|---|---|---:|
| 7-8 | We improved board and public points, but did not force a hard-close fast enough after John's economy clearly outpaced ours | The game stayed open long enough for the Saturn engine to convert into huge card VP | 15 |
| 9-11 | John's late stack of `Kelp Farming`, animal cards, Jovians, and deep draw engines matured | The score gap shifted decisively into card VP and final board conversion | 20 |
| 11-13 | We kept converting efficiently, but too many of our late resources still went into production or medium-value cards instead of maximum VP-per-action lines | We narrowed some public lanes, but not enough to offset the card-VP gap | 8 |

## 6) Counterfactuals

| Alternative line | Realism | Estimated swing |
|---|---|---:|
| Hard-close from Gen 8 once Saturn discount/card-draw ceiling was obvious | med | 12 |
| Do not fund `Scientist` unless the lead is durable under John's likely science follow-up | high | 5 |
| Spend stranded steel and MC earlier on board VP instead of additional flexibility cards | high | 8 |

## 7) Mistake Taxonomy Tags

- `opponent_engine_underrated`
- `insufficient_card_vp_scaling`
- `vp_ceiling_miscalculated`
- `resource_stranding`
- `late_strategy_pivot`

## 8) Tool Mismatches

| Tool | Expected | Actual | Root cause | Mitigation |
|---|---|---|---|---|
| `choose_or_option` project-card payments | Steel should only be accepted when the server considers the card steel-payable | Some non-building cards rejected mixed steel/MC payments with HTTP 400 | Payment legality is stricter than card-tag memory in practice | Default to MC-only unless the card is clearly a building card and the server has accepted steel for that card family |

## 9) Rule Updates (Must Be Actionable)

1. If a Saturn or equivalent titanium/discount engine has both strong draw and large MC production by Gen 7, then switch to hard-close mode immediately.
2. If a funded award can plausibly flip from first to second under the opponent's visible engine path, then do not fund it.
3. If stranded steel exceeds one good building play by the late midgame, then prioritize board-scoring buildings or standard projects before taking more setup cards.

## 10) Next-Game Checklist

- [x] Strategy call logged by Gen 3.
- [x] Milestone contest plan explicit by Gen 4.
- [ ] Award funding lock confidence checked.
- [ ] Card VP race estimate written by Gen 6.
- [ ] Hard-close trigger written once opponent VP ceiling is clearly above ours.
