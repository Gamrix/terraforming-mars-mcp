# Terraforming Mars Postmortem
## Game: `http://localhost:8080/player?id=p8c557b3d0c85`
## Date: `2026-03-05`

## 1) Outcome Snapshot

- Final result: **John 137 - 115 Codex**
- Ended in **Generation 12**
- Board: `tharsis`
- Initial strategy call (Gen 2-3): `hybrid`
- Did we pivot? `yes`
- Pivot generation: `9`

## 2) Score Decomposition

| Category | Self | Opponent | Delta (Opp - Self) |
|---|---:|---:|---:|
| TR | 55 | 45 | -10 |
| Milestones | 10 | 5 | -5 |
| Awards | 5 | 10 | +5 |
| Greenery | 24 | 7 | -17 |
| City | 14 | 21 | +7 |
| Card VP | 7 | 49 | +42 |
| **Total** | 115 | 137 | +22 |

## 3) Timeline by Generation

- Gen 1: Valley Trust opener with Nitrogen Shipment + Experimental Forest + Dome Farming + Arctic Algae; early plant/TR setup online.
- Gen 2: Ice Asteroid + Invention Contest + Dust Seals; ocean/plant triggers accelerated TR and board access.
- Gen 3: Imported Hydrogen + greenery conversion + Gardener claim setup pressure.
- Gen 4: Comet + plant denial + Rad-Suits; continued board pressure while opponent built economy stack.
- Gen 5: Algae + Mining Expedition + double greenery conversion; oxygen pressure increased.
- Gen 6: Terraformer claimed, Insects spike to high plant production, Great Dam + GHG Bacteria online.
- Gen 7: Noctis City and Landlord funding with board expansion; opponent funded Miner and strengthened economy.
- Gen 8: Protected Valley + greenery + aquifer SP; oxygen capped, closure pressure started.
- Gen 9: Nitrogen-Rich Asteroid + Deep Well Heating + multiple greeneries; strong TR push while opponent expanded VP engine.
- Gen 10: City + multiple greeneries + Rad-Chem Factory; board and TR conversion continued.
- Gen 11: Multiple Asteroid SPs pushed temperature from -2 to +6; closed timer lane and added final board VP.
- Gen 12: Plantation greenery + final Asteroid SP to +8 and end trigger; final city/greenery conversion line executed.

## 4) Strategy Review

### Self
- Core plan: Plant-heavy hybrid line with milestone control, then pivot to closure and board liquidation.
- What worked: Milestones (Terraformer + Gardener), strong TR lane, Landlord win, high greenery conversion.
- What failed: Insufficient card VP engine and weaker city network than opponent despite late city push.

### Opponent
- Core plan: Economy/science-space stack into animal/microbe/card-VP conversion.
- How they converted into VP: Massive card VP stack (49), high city adjacency network (21 city VP), and award wins (Banker + Miner).
- What we failed to deny: Long-run VP ceiling from stacked blue cards and late high-yield city/animal lines.

## 5) Critical Turning Points

| Gen | Decision | Why it mattered | VP impact estimate |
|---:|---|---|---:|
| 7 | Funded Landlord while opponent funded Miner | Landlord eventually held (+5), but Miner lock gave opponent reliable public VP | 5 |
| 9 | Hard closure pivot (Nitrogen-Rich Asteroid + Deep Well Heating + greeneries) | Correctly improved TR/board floor and limited further engine growth | 8 |
| 10-12 | Opponent converted established card engine into huge card/city VP | Card VP and city categories decided game despite our TR/greenery lead | 15 |

## 6) Counterfactuals

| Alternative line | Realism | Estimated swing |
|---|---|---:|
| Build one additional city anchor by Gen 8 (before oxygen cap) and route greenery to own city network sooner | med | 8 |
| Shift one Gen earlier from science utility cards to direct VP cards/standard city/greenery liquidation | high | 6 |
| Track opponent card-VP ceiling more aggressively and force temperature closure by Gen 10-11 at latest | med | 7 |

## 7) Mistake Taxonomy Tags

- `insufficient_card_vp_scaling`
- `opponent_engine_underrated`
- `vp_ceiling_miscalculated`
- `resource_stranding`
- `endgame_conversion_miss`

## 8) Tool Mismatches

| Tool | Expected | Actual | Root cause | Mitigation |
|---|---|---|---|---|
| n/a | n/a | No blocking mismatch observed this game | n/a | Keep timeout safety protocol (poll state before retries) |

## 9) Rule Updates (Must Be Actionable)

1. If opponent projected `card_vp >= 35` by Gen 8, then pivot immediately to forced closure plus city-denial instead of additional setup cards.
2. If entering Gen 10+ with `MC >= 40` and all but one global track complete, then pre-commit each generation to a 2-action liquidation plan (city/greenery/TR) before passing.
3. If opponent is likely to lock Banker or Miner by midgame, then either contest with a committed line in the same generation or fully ignore and convert actions to guaranteed board/card VP.

## 10) Next-Game Checklist

- [x] Strategy call logged by Gen 3.
- [x] Milestone contest plan explicit by Gen 4.
- [x] Award funding lock confidence checked.
- [ ] Card VP race estimate written by Gen 6.
- [x] Endgame conversion plan written at start of final generation.
