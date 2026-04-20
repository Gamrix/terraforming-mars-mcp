# Post-Mortem: Game 7 (Claude red vs John blue) — Tharsis, 2-player, Prelude, 13 gens

**Result: Lost 96–162 (–66 VP)** — worst margin since Game 3.

## Final Score Breakdown

| Category | Claude (red) | John (blue) |
|---|---|---|
| TR | 51 | 55 |
| Milestones | 5 (Mayor) | 10 (Builder + Gardener) |
| Awards | **0** | **15** (Banker + Thermalist + Miner, all 1st) |
| Greenery tiles | 6 | 12 |
| City adjacency | 9 | 19 |
| Card VP | 25 | 51 |
| Negative VP | -2 (Corporate Stronghold) | -1 (Indentured Workers) |
| **Total** | **96** | **162** |

## Corporations & Key Cards

- **Claude (Teractor)**: Ants (6 VP from 12 microbes), Interstellar Colony Ship (4 VP), Small Animals (3 VP), Space Elevator (2 VP), Callisto Penal Mines (2 VP), Mohole Area (+4 heat prod), Insects (+2 plant prod), Imported Nitrogen, Deimos Down (-8 John plants), Fusion Power, Big Asteroid (game-ending), Virus denial, Equatorial Magnetizer (+5 TR over 5 chain actions), Quantum Extractor, Robotic Workforce (dup Corporate Stronghold for +3 MC prod). 5 cities on Mars.
- **John (Tharsis Republic)**: Olympus Conference + Mars University + Business Network + Development Center + AI Central = massive draw engine (~60 cards played). VP-per-resource: Ecological Zone (9 animals = 4 VP), Herbivores (6 animals = 3 VP), Livestock (3 animals = 3 VP), Pets. Jovian stack: Io Mining Industries (8 VP), Ganymede Colony (8 VP), **Terraforming Ganymede (+8 TR!)**. Economy: Medical Lab (+7 MC prod), Miranda Resort, Cartel, Toll Station. 6 cities.

## What Went Right

### 1. Claimed Mayor milestone via Gen 4 rush (5 VP)
John stole 3 MC via Hired Raiders on Gen 4 Turn 0, breaking my original SP City + claim plan. Pivoted to Power Plant SP + Corporate Stronghold + claim sequence across 2 turns. John placed 2 cities Gen 1 and was tied 2-2 on cities; he passed Gen 4 without racing Mayor — crucial gift. First time I've locked Mayor vs John.

### 2. Best TR ever (51, exceeds Game 5/6's 52 peak only slightly but...)
Equatorial Magnetizer chain gave +5 TR across generations. DWH temperature step, heat converts (used 8 heat → TR multiple times), greenery oxygen TRs, Big Asteroid +2 TR (game-ending), Deimos Down +3 TR, Imported Nitrogen +1 TR. Broad TR-scattering approach worked.

### 3. Interstellar Colony Ship unlock chain
Played Martian Survey Gen 5 to hit 5 science tags, then ICS Gen 6 for 4 VP (paid with Teractor -3, RO -1, QE -2 discounts + 1 Ti = 15 MC cash). ICS at 4.5 MC/VP is excellent.

### 4. Corporate Stronghold + Robotic Workforce combo
CS gave +3 MC prod for its -2 VP penalty. RW duplicated CS's production box for another +3 MC prod. Total +6 MC prod from this pairing. Ended with 25 MC prod baseline — though John reached 43 anyway.

### 5. VP-per-resource cards produced real points
Ants (12 microbes = 6 VP), Small Animals (6 = 3 VP), Fish (1 animal = 1 VP). 10 VP from action-based accumulation. **Still vastly less than John's Ecological Zone + Herbivores + Livestock + Pets which accumulate on effect triggers (plant/animal tag plays, greenery placements).**

## What Went Wrong

### 1. AWARDS CATASTROPHE: 0 VP vs 15 VP (–15 VP swing)
**Funded Banker at 8 MC Gen 9 when leading 17 vs 9.** Final: 25 vs 43 MC prod. John overtook via Medical Lab (+7 MC prod), Miranda Resort, Cartel, Cloud Seeding, Shuttles.

**Funded Thermalist at 14 MC Gen 9 when leading 21 vs 10.** Final: 14 vs 28 heat. John added Mohole-equivalent heat prod via Aerobraked Ammonia Asteroid, Imported GHG, Caretaker Contract, Windmills → heat prod 10. Meanwhile I converted heat for TR (-8 each time) and burned heat on LHT.

**John funded Miner at 20 MC Gen 12 when he had 16 vs my 0.** He won trivially.

**Net: –22 MC spent by me + 15 VP to John = ~-22 MC –15 VP = catastrophic.**

**Root cause: I funded awards assuming "structural 10+ lead" was enough.** But:
- MC prod can swing 10+ in 2-3 generations via cards like Medical Lab (+7), Cartel (+5), Miranda Resort (+scaling Earth), Cloud Seeding (-1 to me).
- Heat prod can swing similarly: Aerobraked Ammonia, Carbonate Processing, Imported GHG, Caretaker Contract all add multiple heat prod.
- Gen 9 (my funding gen) is NOT late game in 13-gen game — 4 more gens for John to flip.

### 2. JOHN'S CARD VP DWARFED MINE: 25 vs 51 (–26 VP swing)
John's top card VP sources:
- Io Mining Industries: 8 VP (4 Jovian tags × 2 VP).
- Ganymede Colony: 8 VP (4 Jovian tags × 2 VP).
- Ecological Zone: 4 VP (9 animals / 2).
- Herbivores: 3 VP (6 animals / 2).
- Livestock: 3 VP (3 animals).
- Anti-Gravity Technology: 3 VP.
- Gene Repair: 2 VP.
- Methane From Titan, Asteroid Mining, Terraforming Ganymede: 2 VP each.

**John played 6 Jovian cards (vs my 1) and stacked them late for 16 VP from Jovian scaling alone.** Io Mining and Ganymede Colony both scale on Jovian tag count — John drafted toward this aggressively.

### 3. TERRAFORMING GANYMEDE GAME-WARPING LATE PLAY (+8 TR swing to John)
John played Terraforming Ganymede Gen 13. +1 TR per Jovian tag he has. He had 8 Jovian tags → +8 TR in one action. Moved TR from me+7 ahead to me-4 behind in one play.

**Lesson: Track opponent Jovian tag count every generation. If opponent has 4+ Jovians, hate-draft Terraforming Ganymede when seen. Also hate-draft Io Mining Industries and Ganymede Colony which stack with it.**

### 4. CITY ADJACENCY: 9 vs 19 (–10 VP)
My 5 cities had 9 adjacent greeneries total. John's 6 cities had 19 adjacent greeneries.

Placements:
- Research Outpost at 39: restricted "next to no other tile" = only 2 adjacent greeneries at game end.
- Domed Crater at 42: surrounded by greeneries 41, 49, 50. 3 adj.
- Corporate Stronghold at 21: adjacent to greeneries 22, 30 = 2 adj.
- Cupola City at 51: 1 adj greenery (50).
- SP City at 24: 1 adj greenery (25 John's — doesn't count for me wait, actually does give MY city +1 VP regardless of owner of greenery).

Actually SP City 24 was adj to John's greenery 25 (Gen 3). So +1 VP adj to my SP City? Yes — the rule is "1 VP per adjacent greenery regardless of who owns it".

John placed greeneries in 3 late-game turns on spaces 03, 08, 10, 15 (all in north near his cities 17, 18). His Gen 13 action flurry added 4 greeneries in one turn.

**Lesson: John's plant prod 14 at end-game let him convert 4+ greeneries in final turn. I should have been placing MORE cities earlier near future greenery zones AND/OR denying his plant prod.**

### 5. 60+ cards played by John via mega draw engine
Count: John played 64 cards in his tableau (I counted from final state). I played 46.

John's draw engine:
- Olympus Conference (draw on science tag)
- Mars University (draw on science tag, discard+draw)
- Business Network (check+buy top card per turn)
- Development Center (spend 1 E for draw)
- Restricted Area (spend 2 MC for draw)

Each of these fires 1-2 times per gen. John's science tag plays trigger Olympus and Mars U multiple times per gen. Net: ~2-3 extra cards drawn per gen = 20-30 extra cards over game.

**I had Business Network only, no Mars U or Olympus.** Draw disparity directly fed his VP card count.

### 6. John's Gen 13 mega-turn (+38 VP)
Gen 13 VP progression: me 88→96 (+8). John 124→162 (+38!).

John's Gen 13 plays: Magnetic Field Generators (+2 plant prod), 4 Greeneries via SP Greenery (+4 MC x 3 from Media Archives + +4 MC per greenery from his effects + 4 animals to Herbivores), Terraforming Ganymede (+8 TR!), Asteroid Mining Consortium, Pets, Gene Repair, Shuttles, Eos Chasma, Caretaker Contract, and probably more.

He had 100+ MC available and chained cards via Earth Catapult (-2 MC) + Earth Office + multiple triggered effects. Each greenery triggered +1 animal on Herbivores, Media Archives gave +16 MC retroactively on event plays, etc.

**The late-game compounding of engine cards is catastrophic when opponent has 6+ draw engine sources. Need to either match it OR end the game earlier to deny the late turn.**

## Comparison with Games 1–7

| Factor | G1 (–2) | G2 (–36) | G3 (–70) | G4 (–20) | G5 (–35) | G6 (–52) | G7 (–66) |
|---|---|---|---|---|---|---|---|
| Milestones | 10 | 0 | 10 | 10 | 10 | 5 | 5 |
| Awards | 5 | 5 | 0 | 0 | 0 | 0 | 0 |
| City adjacency | 0 | 6 | 10 | 10 | 9 | 8 | 9 |
| Card VP | 25 | 18 | 15 | 35 | 37 | 38 | 25 |
| TR | 49 | 44 | 50 | 44 | 52 | 52 | 51 |
| Loss margin | –2 | –36 | –70 | –20 | –35 | –52 | –66 |

**Trends:**
- **Awards: 6 consecutive 0-award games despite funding (G7 funded 2 and lost both).** This is the persistent structural loss driver.
- **Card VP dropped back to 25 this game.** Worse than Games 4-6 (35-38). Lost because I spent cards on TR race (Equatorial Magnetizer, Comet, Imported Nitrogen) rather than VP-per-resource engines.
- **Milestone wins now consistent (Mayor this game, Mayor G4, Terraformer G6). That's +5 VP from milestones but John stacks 10 VP.**
- **TR remains strong (49-52 range).**

## Key Lessons

1. **FUND AWARDS AT MOST WHEN LEAD IS 15+ WITH 3 OR FEWER GENERATIONS REMAINING.** My Gen 9 Banker/Thermalist fundings with 7-10 gap and 4 generations remaining were both reversed. Rule: **don't fund before Gen 10 unless lead is 15+.**

2. **Track opponent's Jovian tags every generation starting Gen 5.** If opponent has 3+ Jovians, hate-draft Terraforming Ganymede, Io Mining Industries, Ganymede Colony, Asteroid Mining when seen. These cards have VP:cost ratios of 2-4 MC/VP when Jovian-stacked.

3. **Draw engine parity is critical.** I had Business Network + MS 2-card draws + Tech Demo 2-card draws. John had 5 draw engine cards firing per gen. **Draft Mars University or Olympus Conference or Development Center whenever seen.** Each fires 5-10 times = 5-10 extra cards = 10-20 MC value.

4. **John's Gen 13 played +38 VP via Media Archives + Earth Catapult + chain plays.** When opponent has event-triggering cards (Media Archives, Olympus Conference, Optimal Aerobraking), their late-game explodes. **Consider ending the game 1 gen earlier via Big Asteroid or aggressive heat conversion, even at cost of my own setup cards.**

5. **Corporate Stronghold's -2 VP + Robotic Workforce combo gave +6 MC prod baseline.** Net ~+40 MC value for 4 MC draft + 19 MC play = +17 MC net. WORKED. Consider repeating with other -VP cards if the MC prod compounds.

6. **SP City placement bonus from adjacent ocean (+2 MC × ocean count) is huge.** SP City at 24 earned +4 MC from 2 adj oceans + 1 plant bonus. Plan city placements for placement bonuses.

7. **Quantum Extractor + Equatorial Magnetizer is a viable S-tier TR combo.** QE gave +4 E prod + -2 MC on space cards. EM converted E prod to TR over 5 generations = +5 TR for 23 MC. Net +30 MC value. **Excellent if 4+ science tags in hand.**

## Strategic Pivot for Game 8

Three persistent structural problems across 6+ games:
- **Awards: 0 VP in 6 straight games despite funding.** New rule: **don't fund before Gen 10** and **only fund if lead is 15+**. In short game, skip awards entirely (like Game 1).
- **City adjacency: 8-10 VP stuck.** Need 5+ cities with adjacent greeneries placed specifically for them. Prioritize SP City mid-game.
- **Opposing VP-per-resource engines + late-game card chains.** Hate-draft or take Ecological Zone, Herbivores, Pets, Io Mining Industries, Ganymede Colony, Terraforming Ganymede. These stack to 15+ VP for opponent.

**New priority for Game 8: DRAFT MORE DRAW ENGINE CARDS EARLY.** Mars University, Olympus Conference, Development Center. Match John's card throughput. My 46 cards vs his 64 = 18 card deficit = ~25 MC of VP difference right there.
