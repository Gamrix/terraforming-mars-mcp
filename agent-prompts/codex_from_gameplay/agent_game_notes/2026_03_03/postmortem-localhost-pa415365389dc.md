# Terraforming Mars Postmortem
## Game: `http://localhost:8080/player?id=pa415365389dc`
## Date: `2026-03-03`

## 1) Outcome Snapshot

- Final result: **John 142 - 88 Codex**
- Ended in **Generation 12**
- Board: `tharsis`
- Initial strategy call (Gen 2-3): `hybrid`
- Did we pivot? `yes`
- Pivot generation: `10`

## 2) Score Decomposition

| Category | Self | Opponent | Delta (Opp - Self) |
|---|---:|---:|---:|
| TR | 48 | 44 | -4 |
| Milestones | 15 | 0 | -15 |
| Awards | 0 | 15 | +15 |
| Greenery | 6 | 18 | +12 |
| City | 4 | 14 | +10 |
| Card VP | 15 | 51 | +36 |
| **Total** | 88 | 142 | +54 |

## 3) Timeline by Generation

- Gen 1: Valley Trust setup, Great Aquifer + Supply Drop + Nitrogen Shipment, early economy established.
- Gen 2: Deimos Down + Noctis line created early TR lead and board foothold.
- Gen 3: Olympus/Inventors value line continued; opponent science-earth setup continued.
- Gen 4: Cupola City + Subterranean Reservoir improved board and MC production.
- Gen 5: Claimed Mayor and funded Banker; board expanded but opponent plant core formed.
- Gen 6: Comet + Industrial Microbes line; continued parameter pressure.
- Gen 7: Protected Valley, claimed Terraformer and Builder; very strong milestone game.
- Gen 8: Callisto Penal Mines + Cartel improved economy, but opponent discount/science stack accelerated.
- Gen 9: Plantation + Mining Expedition + Grass improved TR/oxygen, but opponent VP engine kept scaling.
- Gen 10: Forced oxygen and ocean progress (Towing A Comet, greenery, Magnetic Field Dome).
- Gen 11: Aquifer Pumping + Tundra + Herbivores + Rad-Suits + Eos Chasma, but opponent converted huge plant/card VP.
- Gen 12: Permafrost Extraction closed oceans; multiple asteroid SPs closed temperature, game ended immediately after final conversions.

## 4) Strategy Review

### Self
- Core plan: Hybrid TR/board pressure with strong milestone capture and late close.
- What worked: Excellent milestone conversion (3/3), strong TR lane, timely endgame closure trigger.
- What failed: Could not keep pace in card VP and board greenery/city conversion, and failed to secure any award points despite early Banker funding.

### Opponent
- Core plan: Science/earth discount stack into card draw plus large plant conversion engine.
- How they converted into VP: Massive card VP (51), dominant greenery/city endgame placement, and two funded awards won.
- What we failed to deny: Discount-stack maturation and late mass plant conversion windows.

## 5) Critical Turning Points

| Gen | Decision | Why it mattered | VP impact estimate |
|---:|---|---|---:|
| 8 | Opponent discount/card-draw engine matured (Earth Catapult -> Anti-Gravity -> AI Central trajectory) | Locked in superior late card VP conversion | 15 |
| 10 | Scientist funded by opponent, Landlord later funded and won | Public-point race swung despite our milestone lead | 10 |
| 11-12 | We closed globals aggressively, but after opponent had already banked large card/board VP | Closure helped limit damage, but came after VP ceiling gap was established | 8 |

## 6) Counterfactuals

| Alternative line | Realism | Estimated swing |
|---|---|---:|
| Contest/deny Scientist and Landlord funding windows instead of preserving MC for flexible play | med | 8 |
| Earlier anti-engine denial focus (prioritize repeated plant suppression and faster closure from Gen 8) | med | 10 |
| Convert more MC into board VP one generation earlier (before opponent final greenery bursts) | high | 6 |

## 7) Mistake Taxonomy Tags

- `insufficient_card_vp_scaling`
- `opponent_engine_underrated`
- `award_funding_mislock`
- `endgame_conversion_miss`
- `tool_timeout`
- `resource_stranding`

## 8) Tool Mismatches

| Tool | Expected | Actual | Root cause | Mitigation |
|---|---|---|---|---|
| `choose_or_option` | Pass action should return quickly with next-turn state | Timed out on pass twice while action still executed server-side | Server/tool timeout during post-action wait | Always call `get_game_state` before retrying after timeout; treat timeout as potentially successful |

## 9) Rule Updates (Must Be Actionable)

1. If opponent card-VP projection exceeds 40 by Gen 9, then prioritize closure and denial over additional economy cards.
2. If funding an award does not project at least second place with high confidence, then do not fund it.
3. If oceans and oxygen are near cap by Gen 10, then reserve MC for guaranteed temperature/TR closure actions.

## 10) Next-Game Checklist

- [x] Strategy call logged by Gen 3.
- [x] Milestone contest plan explicit by Gen 4.
- [ ] Award funding lock confidence checked.
- [ ] Card VP race estimate written by Gen 6.
- [x] Endgame conversion plan written at start of final generation.
