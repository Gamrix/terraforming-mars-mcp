# Post-Mortem: Game 2 (Claude red vs John blue) — Tharsis, 2-player, Prelude

**Result: Lost 79–115 (–36 VP)**

## Final Score Breakdown

| Category | Claude (red) | John (blue) |
|---|---|---|
| TR | 44 | 44 |
| Milestones | 0 | 15 (Mayor + Planner + Terraformer) |
| Awards | 5 (Banker 1st) | 10 (Scientist 1st + Landlord 1st) |
| Greenery tiles | 6 | 8 |
| City adjacency | 6 | 11 |
| Card VP | 18 | 27 |
| Negative VP | 0 | –1 |
| **Total** | **79** | **115** |

## Corporations & Preludes

- **Claude**: Teractor (60 MC, –3 MC on Earth tags) + Self-Sufficient Settlement (+2 MC prod, city) + Early Settlement (+1 plant prod, city)
- **John**: Robinson Industries (action: +1 prod of choice/gen) + Experimental Forest (greenery) + Mohole Excavation (+1 steel prod, +2 heat prod)

## What Went Right

### 1. City cluster from preludes
Placed 2 cities (spaces 40 and 42) on Gen 1 with shared adjacency at space 41. The cluster worked as intended — greenery at space 41 scored 3 VP (adjacent to both cities). Greeneries at 39, 46, 47, 48 all scored city adjacency VP. Total city adjacency: 6 VP (up from 0 in Game 1).

### 2. Microbe combo engine
Extreme-Cold Fungus + Regolith Eaters + GHG Producing Bacteria generated free TR most generations. ECF adds 2 microbes to RE or GHG, then remove 2 for +1 oxygen or +1 temperature. Generated approximately 8 TR over the game from combos alone.

### 3. MC production engine
Built MC production to 24 by endgame through Teractor Earth tag discount, Sponsors (+2), Miranda Resort (+3 from Earth tags), Acquired Company (+3), Satellites (+3 from space tags), Zeppelins (+5 from cities on Mars), Callisto Penal Mines (+3), Protected Valley (+2), Rad-Suits (+1). This was the game's strongest economy.

### 4. Won Banker award decisively
MC production 24 vs John's 12. Clear 1st place for 5 VP.

### 5. Avoided all negative VP cards
Correctly passed on Nuclear Zone, Corporate Stronghold, Hackers. Learned from Game 1's –3 VP from Indentured Workers + Bribed Committee.

### 6. TR parity
Matched John's TR at 44 despite his 3-milestone advantage. Microbe combos + Caretaker Contract + heat conversions + standard projects kept TR competitive.

## What Went Wrong

### 1. Milestone sweep: 0 vs 15 (–15 VP) ← THE DECISIVE FACTOR

John claimed ALL THREE milestones. I claimed zero. This 15 VP swing alone accounts for nearly half the loss margin.

- **Mayor** (3 cities): I had 2 Mars cities from preludes. Played Ganymede Colony (off-board city) as my 3rd city, but John played Urbanized Area at space 49 to claim Mayor first. **Root cause**: I should have played a standard project City (25 MC) or a city card ON MARS in Gen 5–6 instead of waiting for Ganymede Colony in Gen 6. Off-board cities don't help claim Mayor as quickly as on-Mars cities with adjacency benefits.

- **Terraformer** (TR 35): I reached TR 31 by Gen 8, needing 4 more. John hit 35 first. **Root cause**: I prioritized economy building (Satellites, Miranda Resort, Acquired Company) over raw TR generation. Should have used Standard Asteroid (14 MC) earlier to push TR faster.

- **Planner** (16 cards): John hoarded 14–16 cards throughout the game. I never exceeded 7 cards in hand. **Root cause**: Not a realistic target with my playstyle of deploying cards aggressively. John's Robinson Industries sustained his economy while holding cards.

### 2. Scientist award backfire: funded but lost (–5 VP net swing)

Funded Scientist in Gen 3 when leading 4-1 in science tags. By endgame, John had 8 science tags vs my 6. My 8 MC funded John's 5 VP.

**Root cause**: Science tags are cheap and numerous. A 4-1 lead in Gen 3 is NOT structurally safe — John had 8+ remaining generations to play science cards. John played: Standard Technology, Anti-Gravity Technology, Trans-Neptune Probe, Mass Converter, and others with science tags.

**Lesson**: Only fund awards where the lead is based on structural advantage (e.g., Banker with 20+ MC prod vs 4, Miner with massive ti/steel stockpile). Tag-based awards are volatile — opponents can cheaply accumulate tags over time.

### 3. Plant destruction with no counter

John destroyed my plants 4 separate times:
- Asteroid: –3 plants (Gen 4)
- Comet: –3 plants (Gen 5)
- Giant Ice Asteroid: –4 plants (Gen 7)
- Mining Expedition: –2 plants (Gen 8)

Total: 12 plants destroyed. That's 1.5 greeneries worth of plants, or ~4.5 VP in tile + adjacency value. Meanwhile, John had Protected Habitats making his own plants untouchable.

**Root cause**: I never drafted or played Protected Habitats or any plant protection. In 2-player, if the opponent has Protected Habitats, plant destruction is one-directional. I should have either: (a) drafted Protected Habitats myself when available, (b) avoided heavy plant investment knowing John had protection + attack cards, or (c) pivoted to heat/MC-based VP generation earlier.

### 4. John's Ants disrupted microbe combos every turn

Ants removes 1 microbe from any card per action. John used it every generation to steal from Regolith Eaters, GHG Producing Bacteria, or Decomposers. This:
- Reduced my TR generation by ~2–3 over the game (combos that couldn't fire)
- Stole from Decomposers' VP pile (6 microbes at end instead of 8+ = 2 VP instead of potentially 3 VP)
- Fed Ants to 10 microbes = 5 VP for John

**Root cause**: No counter available. Protected Habitats would have blocked Ants. Once Ants was in play, I should have overloaded microbes across multiple cards to minimize per-card impact.

### 5. Card VP deficit: 18 vs 27 (–9 VP)

John's key VP cards:
- Ants: 5 VP (fed from my microbes!)
- Birds: 5 VP (accumulated animals)
- Anti-Gravity Technology: 3 VP
- Ecological Zone: 3 VP (7 animals)
- Advanced Ecosystems: 3 VP
- Farming: 2 VP
- Colonizer Training Camp: 2 VP
- Lake Marineris: 2 VP

My key VP cards:
- Ganymede Colony: 3 VP (3 jovian tags)
- Callisto Penal Mines: 2 VP
- Pets: 2 VP (4 animals)
- Decomposers: 2 VP (6 microbes)
- Fish: 2 VP (2 animals)
- Others: 7× 1 VP cards

**Root cause**: John had stronger VP-per-card density. His animal engine (Birds + Ecological Zone + Ants) generated 13 VP from card resources. My microbe engine generated 4 VP from resources (Decomposers + Fish). I needed higher-VP cards or more resource accumulation.

### 6. Robinson Industries compounding

John's corporation gave +1 production of any type every generation for free. Over 11 generations, that's +11 production steps distributed optimally. John used it for titanium, plant, steel, and energy production as needed. This flexibility let him build economy while deploying cards aggressively.

## Key Decisions in Retrospect

| Decision | What I Did | Better Alternative |
|---|---|---|
| 3rd city | Ganymede Colony (off-board, Gen 6) | Standard City SP on Mars (Gen 4–5) to claim Mayor |
| Scientist award | Funded Gen 3 at 4-1 lead | Wait until lead is 6+ tags or structurally locked |
| Terraformer race | Focused on economy Gen 4–7 | Push TR harder with Standard Asteroids Gen 5–6 |
| Plant protection | No plant defense | Draft Protected Habitats when available |
| Microbe defense | Spread microbes reactively | Draft/play Protected Habitats to block Ants |
| Card drafting | Prioritized engine synergy | Should have drafted more direct VP cards mid-game |

## Comparison with Game 1

| Factor | Game 1 (Lost 99–101) | Game 2 (Lost 79–115) |
|---|---|---|
| City adjacency VP | 0 (1 isolated city) | 6 (2 clustered cities + greeneries) |
| Milestones claimed | 2 (Gardener + Builder = 10 VP) | 0 |
| Awards won | 1 (Miner = 5 VP) | 1 (Banker = 5 VP) |
| Negative VP | –3 (Indentured Workers + Bribed Committee) | 0 |
| TR differential | +1 (49 vs 48) | 0 (44 vs 44) |
| Loss margin | –2 VP | –36 VP |

Game 1's lesson (cities!) was applied — city VP improved from 0 to 6. But milestones collapsed from 10 to 0, and the opponent played a much stronger overall game.

## Final Lessons

1. **Milestones are worth more than any engine.** 15 VP from milestones requires only 24 MC (8×3). No engine in the game delivers that efficiency. Claiming even 1 milestone should be the #1 priority from Gen 1.

2. **Don't fund volatile awards.** Tag-based awards (Scientist, Builder) can flip over 8+ generations. Only fund awards where your advantage is structural: high production (Banker), massive resource stockpiles (Miner, Thermalist), or tile count (Landlord with significant lead).

3. **Protected Habitats is a must-draft in 2-player.** It blocks plant/animal/microbe removal — countering Ants, Asteroid plant destruction, Birds stealing, and Predators. In 2-player, one-directional resource destruction is game-warping.

4. **Robinson Industries is S-tier.** Free production every generation compounds enormously over 11 gens. Respect it as a top-tier corporation.

5. **Off-board cities don't help with Mayor.** They count as cities for scoring, but they miss the critical window for Mayor milestone claim. Always prioritize on-Mars cities first.
