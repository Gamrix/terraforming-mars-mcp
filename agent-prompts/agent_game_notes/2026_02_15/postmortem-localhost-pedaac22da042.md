# Terraforming Mars Postmortem
## Game: `http://localhost:8080/player?id=pedaac22da042`
## Date: 2026-02-15

## 1) Outcome Snapshot

- Final result: **John 112 - 81 Codex**
- Ended in **Generation 11**
- Board: `tharsis`
- Initial strategy call (Gen 2-3): `hybrid`
- Did we pivot? `yes`
- Pivot generation: `11`

## 2) Score Decomposition

| Category | Self | Opponent | Delta (Opp - Self) |
|---|---:|---:|---:|
| TR | 39 | 56 | +17 |
| Milestones | 5 | 10 | +5 |
| Awards | 5 | 10 | +5 |
| Greenery | 2 | 6 | +4 |
| City | 4 | 9 | +5 |
| Card VP | 26 | 21 | -5 |
| **Total** | **81** | **112** | **+31** |

## 3) Timeline by Generation

- Gen 1: Thorgate setup into early building economy and map presence.
- Gen 2: Continued economy ramp; committed to a mixed science/building line.
- Gen 3: Added more production and board footprint; game pace still open.
- Gen 4: Midgame value cards online; did not secure early milestone pressure beyond Mayor line.
- Gen 5: Opponent economy started scaling faster on MC/city trajectory.
- Gen 6: Continued engine layering, but no durable denial line against Builder/Planner race.
- Gen 7: Economy stayed healthy; scoreboard remained close.
- Gen 8: Entered late midgame with strong science tag count but weak public-race position.
- Gen 9: Played into high-VP cards (`Research`, `Solar Wind Power`) and funded awards; opponent still ahead in Banker potential.
- Gen 10: Terraforming nearly complete; oceans closed, but opponent retained stronger city/award setup.
- Gen 11: Played `Anti-Gravity Technology`, `Pets`, `Advanced Ecosystems`, and a standard project city; Mars finished and opponent converted final generation into decisive public VP.
- Gen 12: n/a.

## 4) Strategy Review

### Self
- Core plan: hybrid science/building engine with selective terraforming and endgame card VP.
- What worked: strong card VP floor (26), high science count, and one secured award (`Scientist`) plus `Mayor`.
- What failed: public scoring races (milestones, awards, city, greenery) were under-defended; late resources stranded after game end.

### Opponent
- Core plan: Mining Guild economic engine into city/public scoring.
- How they converted into VP: large TR lead (56), two milestones, two award wins, and broad map control.
- What we failed to deny: `Builder`/`Planner`, `Banker`, and late Landlord swing.

## 5) Critical Turning Points

| Gen | Decision | Why it mattered | VP impact estimate |
|---:|---|---|---:|
| 9 | Funded awards while not locked on Banker/Landlord trajectories | Opened/maintained high-value public VP lanes for opponent | 8 |
| 11 | `Open City` failed to submit due payload/card-name mismatch | Lost a high-efficiency endgame city/card action line | 4 |
| 11 | Opponent final conversion after Mars completion | Opponent gained decisive public-point separation in final cycle | 10 |

## 6) Counterfactuals

| Alternative line | Realism | Estimated swing |
|---|---|---:|
| Avoid funding non-locked award lines (especially Banker context) | high | 5 |
| Resolve `Open City` earlier or pre-plan fallback card with same role | med | 4 |
| Contest Builder/Planner lane earlier (or force tempo closure sooner) | low | 8 |

## 7) Mistake Taxonomy Tags

Use tags from `agent-prompts/codex_from_gameplay/decision-taxonomy.md`.

- `award_funding_mislock`
- `milestone_contest_miss`
- `endgame_conversion_miss`
- `resource_stranding`
- `opponent_engine_underrated`
- `tool_payload_shape_mismatch`

## 8) Tool Mismatches

| Tool | Expected | Actual | Root cause | Mitigation |
|---|---|---|---|---|
| `choose_or_option` | `or` -> `projectCard` accepts first nested payload | 400 invalid `SelectProjectCardToPlayResponse` | Sent `cards` shape instead of strict `card` + full `payment` object | Always use strict payload: `{\"type\":\"projectCard\",\"card\":\"...\",\"payment\":{all spendable keys}}` |
| `choose_or_option` | Play `Open City` listed in selectable cards | 400 `Unknown card name Open City` | Server-side mismatch on this card submit path despite card being present in prompt | Treat as known mismatch, log it, and pivot immediately to legal fallback action |

## 9) Rule Updates (Must Be Actionable)

1. If funding an award without a durable lead projection, then do not fund and spend actions on direct VP or denial instead.
2. If two opponent milestones are live by Gen 6 and uncontested, then prioritize contest/deny actions before additional engine cards.
3. If a project-card submit fails in endgame, then run one retry with strict payload and immediately switch to fallback VP line on second failure.

## 10) Next-Game Checklist

- [ ] Strategy call logged by Gen 3.
- [ ] Milestone contest plan explicit by Gen 4.
- [ ] Award funding lock confidence checked.
- [ ] Card VP race estimate written by Gen 6.
- [ ] Endgame conversion plan written at start of final generation.
