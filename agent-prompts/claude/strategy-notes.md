# Claude's Terraforming Mars Strategy Notes

Lessons learned from actual games, layered on top of the GUIDE.md framework.
Update this file after each game.

---

## The Most Important Things I've Learned

### 1. VP-per-resource cards are essential for competitive card VP

In Game 3, John scored 57 card VP vs my 15. The gap came almost entirely from VP-per-resource cards: Ecological Zone (6VP), Birds (5VP), Fish (5VP), Pets (4VP), Io Mining Industries (7VP), Ganymede Colony (7VP), Security Fleet (3VP). These cards accumulate resources over many generations and scale to 3–7+ VP each. My static 1–2 VP cards cannot compete.

**Draft at least 2–3 VP-per-resource cards by mid-game:**

- **Animal cards**: Ecological Zone, Birds, Fish, Pets, Predators, Small Animals, Livestock
- **Fighter cards**: Security Fleet
- **Microbe VP cards**: Decomposers (1 VP per 3 microbes)
- **Jovian-scaling cards**: Io Mining Industries, Ganymede Colony (VP per Jovian tag)

If you see these in the draft, take them even over engine cards. A single Ecological Zone with 12 animals is worth more VP than 3 static VP cards combined.

### 2. Milestones are worth more than any engine

In Game 2, John swept all 3 milestones (15 VP) while I got 0. That 15 VP swing was worth more than my entire microbe combo engine generated. Milestones cost 8 MC each for 5 VP = 1.6 MC/VP. **No card, engine, or strategy comes close to this efficiency.** Claiming even 1 milestone must be the #1 priority from Gen 1. Plan your opening around which milestone you can reach first.

### 2. City-greenery adjacency VP is as large as TR itself

A player with 4–5 well-placed cities can score 12–20 VP purely from adjacency. In Game 4, John scored 20 city adjacency VP from 5 cities vs my 10 VP from 3 cities. Each additional city is potentially 3–6 more adjacency VP.

**This means: build 4–5 cities ON MARS, cluster them near your own greeneries, and prevent opponents from placing cities adjacent to your greenery clusters.**

---

## City Strategy

### Why cities matter more than I thought

- Each city scores 1 VP per adjacent greenery (up to 6 VP from one city if surrounded)
- In a green plant-heavy game, 3 clustered cities can score 12–18 VP from adjacency
- This stacks with the city tile's own existence (visible on the board)
- Codex used: SF Memorial, Cupola City, Underground City, Immigrant City — all clustered in the southern board

### How to build a city engine

1. **Place first city by Gen 4–5** adjacent to an ocean (free 2 MC placement bonus) and with open adjacent land hexes for future greenery
2. **Place second city nearby** — sharing adjacency with city #1 so one greenery benefits both
3. **Place 3rd–4th cities mid-game** via city cards or SP City (25 MC). Each additional city is 3–6 more adjacency VP. In Game 4, having only 3 cities vs John's 5 cost ~10 VP.
4. **Flood with greenery** in the late game — every plant converted or standard project greenery placed near your cities is 2 VP (1 tile + 1 city adjacency) instead of 1 VP
5. **Defend greenery clusters** — don't create open greenery clusters without your own city nearby. In Game 4, John placed a city at space 11 adjacent to 3 of my greeneries for free 3 adjacency VP.

### Board zones for city clusters (Tharsis)

Use `get_mars_board_state` and the adjacency rules in AGENTS.md to identify spaces where placing a city gives: (a) ocean adjacency bonus, (b) multiple open land hexes nearby for greenery, (c) no opponent cities blocking the zone.

The southern half of the board (y≥5) tends to be open early. The equatorial row (y=4) has ocean tiles that give placement bonuses.

### City cards to prioritize

- **Immigrant City** (13 MC, building tag, city tile, –1 energy prod +1 MC prod): cheap and efficient
- **Capital** (26 MC, city tile with VP per ocean adjacency): expensive but high VP in ocean-heavy games
- **Noctis City** (special placement, no energy prod requirement): flexible placement
- **Standard project City** (25 MC + 1 MC prod): always available, use when ahead on MC in mid-game

---

## Award Strategy

### Lessons from Game 1

- I won Miner (22 steel+Ti vs 4): correct to fund early at 8 MC, clearly winning
- Codex won Thermalist (36 heat vs 21): I never had enough heat to contest. Don't let opponent fund Thermalist if they have Mohole or heat engine — either race it or force them into a contested award
- Codex won Scientist (7 science vs 3): I had no path to winning this; Point Luna + science-heavy deck for Codex made this uncontestable

### Decision framework

1. **You MUST fund at least 1 award per game.** In Games 3–4, scoring 0 awards vs opponent's 15 was a –15 VP hole each time. Even winning just 1 award at 8 MC (5 VP = 1.6 MC/VP) transforms the awards category from catastrophic to manageable.
2. **Fund an award if**: you're currently winning it AND the lead is **structural** (high production, massive stockpile), AND the 8 MC cost is worth 5 VP (it nearly always is at first funding)
3. **Don't fund volatile awards**: Tag-based awards (Scientist, Builder) can flip over 8+ generations. A 4-1 lead in Gen 3 means nothing when the opponent has 8 gens to play cheap tag cards. In Game 2, I funded Scientist at 4-1 lead; John finished 8-6 and won MY award.
4. **Structural leads are safe to fund**: Banker (high MC prod is hard to catch), Miner (massive resource stockpiles), Landlord (significant tile lead). These are much harder to overturn.
5. **Don't fund an award if**: an opponent is clearly going to win it regardless — you're just subsidizing their VP
6. **Contest an award if**: an opponent funds an award you could plausibly win — pivot your strategy to challenge them
7. **Deny by funding a different award**: force opponent to spend 14 MC (2nd) or 20 MC (3rd) on their preferred award
8. **Scan awards every gen from Gen 5 onward**: check which awards you lead or could lead. The first funding at 8 MC is by far the cheapest.

### Award funding danger: production can swing massively in late game (Game 3 lesson)

In Game 3, I funded both Banker (8 MC) and Landlord (14 MC) = 22 MC spent, 0 VP gained. John won both awards by surging production in the final 3–4 gens. This was a –22 MC and –15 VP disaster (John got 15 VP from awards I funded).

**Why awards are more dangerous than they appear:**

- **Banker**: MC production can swing 10+ in 2–3 gens from single cards. Capital (+5), Gene Repair (+2), Cartel (+4), Space Hotels (+4), Kelp Farming (+2). A 5 MC prod lead is NOT safe.
- **Landlord**: Especially dangerous when opponent has high plant production. 18 plant prod = 2+ greeneries per gen = 2+ tiles per gen. An opponent can go from 5 tiles to 21 tiles in 4 gens. NEVER fund Landlord when opponent has 8+ plant production.
- **Miner**: Safer — steel/titanium stockpiles don't swing as fast. But still verify the lead is 10+.

**Updated funding rules:**

1. Only fund at 8 MC if lead is 10+ AND structurally locked (no obvious catch-up cards for opponent)
2. At 14 MC (2nd funding), need near-certainty of winning — the cost is too high for uncertainty
3. Never fund Landlord against a plant-heavy opponent
4. Funding an award you lose is a –10 VP swing (MC spent + opponent gets 5 VP). This is worse than playing almost any card in the game.

### Miner award trap (Game 5 lesson)

Funded Miner at 16-2 lead in Gen 4. By endgame, John led 23-17. The problem: Miner counts RESOURCE CUBES on hand, not production. Spending Ti on space cards (Security Fleet, Ice Asteroid, Imported Hydrogen) depleted my stockpile while John accumulated from Strip Mine + Titanium Mine + Vesta Shipyard + Mineral Deposit.

**Rule: If you fund Miner, stop spending steel/Ti freely.** Every Ti spent on a space card costs a Miner point. Either stockpile for endgame or don't fund Miner at all. Consider that Security Fleet converts Ti to fighter VP (1:1) but costs a Miner point — the net may still be positive, but track it.

### Alternative: Fund awards in the last 2-3 gens

After 3 consecutive 0-award games, consider delaying award funding to Gen 10+ when stockpiles and production are near-final. The cost is higher (14-20 MC for 2nd/3rd funding) but the certainty is much higher. A late 14 MC award you win (5 VP) is better than an early 8 MC award you lose (-10 VP swing).

### Thermalist counter

Heat accumulates from heat production, converted energy, and card effects. If opponent has Mohole or high heat prod, they'll win Thermalist easily. Consider: (a) ignoring it and winning other awards, (b) using Caretaker Contract or heat cards to actually contest, or (c) funding a 3rd award (20 MC) to make Codex pay 20 MC for Thermalist — but only if you'll get 5+ VP from another award.

---

## Negative VP Cards — Avoid Unless Benefit > VP Cost

### Cards to be very cautious with

- **Indentured Workers** (–1 VP): reduces next card's cost by 8 MC. Worth it only if next card costs ≥15 MC and you'd otherwise struggle to afford it. The –1 VP is expensive in close games.
- **Bribed Committee** (–2 VP): reduces a global requirement by 2 steps. Almost never worth –2 VP. Skip.
- **Nuclear Zone** (–2 VP + place tile + 2 temp): the VP penalty often erases the TR gain value in close games
- **Virus** (–1 VP): destroying opponent plants/animals might be worth it in certain situations but is generally weak

**Rule of thumb**: if a card has negative VP printed on it, it must provide at least (negative VP × 7) MC worth of value to justify the –VP cost at standard project efficiency. A –2 VP card needs to provide 14+ MC of value.

---

## Greenery Placement

### Always check adjacency before placing

Before placing a greenery (via plant conversion or standard project), call `get_mars_board_state` to see where my city tiles are. Then use the adjacency rules in AGENTS.md to identify which spaces are adjacent to my cities.

**Priority order for greenery placement:**

1. Adjacent to 2+ of my own cities (scores 3+ VP: 1 tile + 2 city bonuses)
2. Adjacent to 1 of my own cities (scores 2 VP: 1 tile + 1 city bonus)
3. Away from any cities (scores 1 VP: tile only)
4. **Never** adjacent to opponent's cities unless forced (gifts them VP)

### Standard project greenery in end-game

At 23 MC for ~1.5 VP average (1 tile + adjacency), standard project greenery is 15 MC/VP without adjacency and ~8 MC/VP with good city adjacency. **Always worth playing near own cities in the last 1–2 generations.**

---

## TR vs VP: When to Do Each

### TR is always good early

- Early TR = MC income × remaining generations + 1 VP at end
- TR gained in Gen 4 of a 12-gen game = 8 MC income + 1 VP ≈ 13 MC value
- Use Caretaker Contract, NRB microbe cycles, plant→greenery, heat→temp

### Late-game: switch to direct VP

In the last 1–2 generations, additional TR gives: (remaining gens × 1 MC) + 1 VP. In Gen 11 of 12, TR is worth 1 MC income + 1 VP ≈ 6 MC. Standard project greenery with good city adjacency (8 MC/VP) beats this.

**Once all global parameters are nearly maxed, prioritize:**

1. Milestones (1.6 MC/VP — always)
2. High-VP blue card actions (Security Fleet fighters, NRB TR)
3. Greenery tiles adjacent to own cities (~8–11 MC/VP)
4. Good VP cards in hand (≤10 MC/VP)
5. Standard project greenery (11–15 MC/VP)

---

## Reading the Board State

### Use `get_mars_board_state` strategically, not constantly

It's expensive context. Use it when:

- Planning city placement (check open spaces and adjacency)
- Placing greenery (find spaces adjacent to own cities)
- Evaluating tile-based milestones/awards (Landlord)
- Checking if a key board position is still open

### Board space layout (Tharsis)

See `tharsis-board-shape.md` for full coordinate map. Key landmarks:

- **Noctis City space** (space 31, x=2,y=4): special tile, can't place normal tiles here
- **Volcanic spots** (spaces 09, 14, 21, 29): highlighted on board, land spaces
- **Ocean spaces**: fixed positions — can't be cities/greenery
- **Southern cluster** (y≥6): tends to be open and away from the northern ocean cluster, good for late-game city placement

---

## Corporation Picking Notes

### Point Luna (used in Game 1)

- Draws a card on each Earth tag played; cards cost –2 MC
- Excellent for building a large card hand and accessing Earth-tagged city/infrastructure cards
- **In 2-player**: had 11 Earth-tagged cards in final tableau — Point Luna provided significant card advantage
- **Weakness**: needs Earth-tagged cards in hand; weak if you don't draft them

### Robinson Industries (faced in Game 2)

- Action: gain 1 production of any type per generation — free, flexible, compounds massively
- Over 11 generations, John gained ~11 production steps distributed optimally (titanium early, plants mid, energy late)
- **S-tier in 2-player**: the flexibility to adapt production each gen is extremely strong
- Harder to counter because it doesn't depend on specific card draws

### Things to look for in corporation selection

1. Does it synergize with a clear milestone/award target?
2. Does it give early economic advantage (steel/titanium production)?
3. Does it enable the city-greenery VP engine? (Tharsis Republic is ideal: free city + MC prod per city)
4. Does it compound over many generations? (Robinson Industries, Tharsis Republic)

---

## Milestone Strategy — #1 Priority

### The math is overwhelming

- 3 milestones × 5 VP = 15 VP for 24 MC total (8 MC each)
- That's 1.6 MC/VP — **7× more efficient than Standard Asteroid** (14 MC/VP)
- In Game 2, John's 15 milestone VP exceeded my entire card VP total (18 VP)

### Milestone racing priorities (Tharsis)

1. **Mayor (3 cities)**: Build 3 cities ON MARS by Gen 5–6. Prelude cities count. Off-board cities (Ganymede, Phobos) count for scoring but are slower to deploy — prefer on-Mars city cards or Standard City SP for milestone racing.
2. **Gardener (3 greeneries)**: Need 24 plants (3 × 8). With 2+ plant prod, achievable by Gen 6–7.
3. **Builder (8 building tags)**: Building is the most common tag. Play building-tagged cards aggressively.
4. **Terraformer (TR 35)**: Need +15 TR from starting 20. Aggressive terraforming + microbe combos. Don't let opponent outpace you.
5. **Planner (16 cards in hand)**: Requires card hoarding, conflicts with playing cards. Only pursue if corporation supports it (cheap card draw, high base income).

### Critical rule: On-Mars cities first

In Game 2, I had 2 Mars cities from preludes but played Ganymede Colony (off-board) as my 3rd city. John played Urbanized Area on-Mars and claimed Mayor first. **Always prioritize on-Mars city cards or Standard City SP over off-board cities when racing for Mayor.**

---

## Key Cards to Draft in 2-Player

### Must-draft defensive cards

- **Protected Habitats** (5 MC): Prevents opponents from removing your plants, animals, and microbes. In 2-player, this is game-warping — it blocks Asteroid/Comet plant destruction, Ants microbe theft, Birds/Predators animal removal. Draft this whenever you see it.

### Must-draft offensive cards

- **Ants** (9 MC): Steals 1 microbe from any card per action. Devastating against microbe engines. If opponent has Regolith Eaters / GHG Bacteria / Decomposers, Ants converts their engine into YOUR VP.
- **Birds** (10 MC): Steals 1 plant prod + adds animals for VP. Strong in late game.

### Counter-strategies when opponent has Protected Habitats

If opponent has Protected Habitats and you don't:

- Don't invest heavily in plant production — your plants will get destroyed while theirs are safe
- Focus on MC/steel/titanium production instead
- Prioritize heat-based TR (Caretaker Contract, GHG Bacteria for temp) over plant-based TR (greeneries)
- Draft plant-destruction cards to deny them to opponent (they can't use them on you, but at least opponent can't stack MORE destruction)

---

## Card Draw Engine Importance

### Why card throughput wins games (Game 3 lesson)

In Game 3, John played 60 cards to my 37 — a 62% throughput advantage. His draw engine: Mars University (draw on science tags), Development Center (draw with energy), Inventors' Guild (buy cards with actions), Business Network (look at top card each gen), Anti-Gravity Tech (–2 MC on all cards).

More cards seen = more VP cards found and played. John's 57 card VP vs my 15 is directly attributable to seeing and playing more high-VP cards.

### Card draw cards to prioritize

- **Mars University** (8 MC): draw a card when playing a science tag. Science tags are common — this fires 5–10 times per game.
- **Development Center** (11 MC): spend 1 energy to draw a card. Reliable, repeatable draw every generation.
- **Inventors' Guild** (9 MC): action to look at top card and buy it. Consistent card access.
- **Business Network** (4 MC): look at top card each generation. Cheap and always-on.
- **Olympus Conference** (10 MC): draw or place science resource on science tag play. Similar to Mars University.
- **Research** (11 MC): draw 2 cards, keep both. One-shot but efficient.

### When to invest in card draw

- **Early game (Gen 1–4)**: Card draw engines pay for themselves over 8+ remaining gens. A Mars University played Gen 2 that fires 8 times = 8 cards drawn = 24+ MC value in card selection.
- **Mid game (Gen 5–8)**: Still worth it if you have 4+ gens remaining. Development Center with energy production is reliable.
- **Late game (Gen 9+)**: Too late for draw engines. Focus on playing VP cards already in hand.

---

## Tactical Reminders

1. **Race for milestones from Gen 1** — they are the single highest-VP-per-MC source in the game. Plan your opening around them.
2. **Build 3 cities ON MARS by Gen 5–6** — claim Mayor and set up adjacency VP. Off-board cities are for VP, not milestone racing.
3. **Use `get_mars_board_state` before placing any tile** to optimize adjacency
4. **Never play –VP cards** in close games unless the benefit is overwhelming
5. **Fund at least 1 award per game** — 0 awards vs opponent's 15 is an unrecoverable –15 VP hole. Scan awards from Gen 5. Fund early at 8 MC when you have any structural lead. Tag/production leads are volatile, but having 0 funded awards is worse than funding one you might lose.
6. **Draft Protected Habitats in 2-player** — it blocks plant/animal/microbe removal and is game-warping. NOTE: it does NOT block production theft (Birds, Fish).
7. **Draft 2–3 VP-per-resource cards by mid-game** — animal/fighter/Jovian-scaling cards generate 3–7+ VP each. Static 1–2 VP cards cannot compete.
8. **Build a card draw engine early** — Mars University, Dev Center, Inventors' Guild. More cards = more VP cards found. 60 cards played vs 37 is a decisive advantage.
9. **Convert all plants and heat** before passing — leave nothing on the table
10. **Standard project greenery near own cities** is efficient VP in final gens
11. **Track opponent city locations** — don't gift them greenery adjacency VP. Don't create undefended greenery clusters that an opponent city can exploit.
12. **Caretaker Contract + microbe combos** are powerful late-game TR engines — keep microbes cycling
12b. **Build 4–5 cities, not 2–3** — 3 cities vs 5 cities costs ~10 adjacency VP. Use SP City (25 MC) when greenery clusters form. Each city is 3–6 potential VP.
13. **Titanium** is 3 MC/unit for space tags — prioritize space cards to spend it
14. **When opponent has Ants**, spread microbes across multiple cards to minimize per-card theft impact
15. **Track opponent Jovian tags** — Terraforming Ganymede with 7+ Jovian tags is a game-winning TR swing
16. **Extreme-Cold Fungus + Ants is top-tier combo** — ECF adds 2 microbes to Ants per gen = 1 VP per gen for free. Over 4 gens = 4 VP. Draft ECF whenever temperature allows.
17. **Don't spend Miner resources after funding Miner** — every Ti/steel spent reduces your Miner score. Either stockpile or don't fund it.
18. **Economy target: 30+ MC prod by Gen 8** — 20 MC prod vs 61 is unrecoverable. A 3:1 economy gap means opponent plays 3-4x more cards. Prioritize MC production cards alongside VP engine.
19. **Protect against plant production theft in 2-player** — Birds, Fish, Predators can reduce plant prod from 4 to 1. Draft Protected Habitats or diversify VP into sources that can't be stolen (microbes, fighters, Jovian tags).
20. **3-milestone cap is a hard ceiling** — Only 3 milestones can be claimed per game. If opponent claims 2 and I claim 1, all 5 are effectively closed. Track milestone claims from gen 1 — if 2 are already gone, reassess whether remaining milestone investment is viable. Don't build 3 cities hoping for Mayor if the cap will block it.
21. **Scientist award is VOLATILE, don't fund on 1-tag lead** — Science tags keep appearing via events (Adaptation Technology, Technology Demonstration, Research, Fusion Power, Invention Contest). A 7-6 lead in Gen 11 evaporated in Gen 12 when John played Adaptation Tech. Only fund Scientist with 3+ tag lead OR when clearly ahead in remaining science cards.
22. **Ecological Zone + Herbivores are broken VP-per-resource cards** — Unlike Ants/Birds which need per-gen ACTIONS, these trigger on EFFECTS (tag plays, greenery placements) and accumulate passively. In Game 6, John's EZ hit 13 animals = 6 VP and Herbivores 13 = 6 VP. Always take these in draft (or hate-draft them) when seen.
23. **Hate-draft Toll Station and Miranda Resort** — These are game-warping MC scalers. Toll Station: +1 MC prod per ocean placement (scales to +9 over a game). Miranda Resort: +1 MC prod per Earth tag (scales with typical 5-10 Earth tags). Both give opponent 20+ MC income over game.
24. **PhoboLog + Satellites is an S-tier opening** — Satellites at 10 MC for +5 MC prod (if 5 space tags) was game-making. PhoboLog makes Ti worth 4 MC for space cards. Combined with Io Mining Industries (+2 Ti prod + 2 MC prod, VP per Jovian), this creates a compounding engine in gens 3-5.
25. **Award funding threshold: 15+ lead AND ≤3 gens remaining.** 7 prior games of 0-award results, including Game 7 where I funded Banker (7 lead) + Thermalist (11 lead) in Gen 9 and lost BOTH to John's late MC/heat prod explosion. Production can swing 10+ in 3-4 generations via cards like Medical Lab (+7), Cartel (+5), Miranda Resort, Cloud Seeding. **Don't fund before Gen 10 unless lead is overwhelming.**
26. **Hate-draft Terraforming Ganymede / Io Mining Industries / Ganymede Colony when opponent has 3+ Jovian tags.** Game 7 John played Terraforming Ganymede Gen 13 for +8 TR (!) off his 8 Jovian tags. Io MI and Ganymede Colony both scale 2 VP per Jovian tag each, stacking to 16+ VP with 4+ Jovians. Track opponent Jovian count every gen from Gen 5.
27. **Match opponent draw engine count.** Game 7 John had 5 draw engine cards (Olympus Conference, Mars University, Business Network, Development Center, Restricted Area) → played 64 cards to my 46. 18-card deficit = ~25-40 MC of VP difference. Draft Mars University or Olympus Conference whenever seen. These trigger 5-10 times/game.
28. **Quantum Extractor + Equatorial Magnetizer is a proven TR engine.** QE (+4 E prod, -2 MC on space cards) + EM (-1 E prod → +1 TR once per gen) = +5 TR over 5 gens. Combined cost ~23 MC, value ~30 MC. Requires 4 science tags to play QE — draft Research, Natural Preserve, Martian Survey, Research Outpost to qualify by Gen 5.
29. **Robotic Workforce duplicating Corporate Stronghold/Domed Crater/Cupola City = +3 MC prod double-up.** Game 7 RW+CS gave +6 MC prod baseline (vs +3 solo). 11 MC cost for +15-30 MC value. Requires a building card with MC prod box in tableau.
30. **Game-ending via Big Asteroid or similar temp-boost cards to deny opponent late-game turn.** Game 7 John's Gen 13 turn = +38 VP (Magnetic Field Generators, Terraforming Ganymede, 4 SP Greeneries, Media Archives chain). Big Asteroid (+2 temp, event) can end game 1-2 gens early. **If opponent has massive card hand + engine, accelerate game end.**
31. **Mayor rush via SP City + claim in one turn is the cleanest lock.** Game 7 was broken by Hired Raiders stealing 3 MC pre-turn (forced PPSP + CS fallback). Can't always protect against that. Still, if first player with 33+ MC and 2 cities, SP City + claim guarantees Mayor in Turn 1.
32. **Corporate Stronghold at -2 VP is acceptable if building engine around it.** Game 7 CS + RW + dup combo gave +6 MC prod = +60 MC future income. Well beyond -2 VP cost. Use CS when MC prod scaling compounds through future gens AND you can afford a -VP card.

---

## Game Log

| Game                                    | Result       | Key Loss Factor      | Key Win Factor                   |
| --------------------------------------- | ------------ | -------------------- | -------------------------------- |
| Game 1 vs Codex (2p, Tharsis, Prelude)  | Lost 99–101  | City VP: 0 vs 16     | Card VP 25, TR 49, 2 milestones  |
| Game 2 vs John (2p, Tharsis, Prelude)   | Lost 79–115  | Milestones: 0 vs 15  | MC prod 24, TR 44, Banker award  |
| Game 3 vs John (2p, Tharsis, Prelude)   | Lost 93–163  | Awards: 0 vs 15, Card VP: 15 vs 57 | 2 milestones, TR 50, strong early economy |
| Game 4 vs John (2p, Tharsis, Prelude)   | Lost 109–129 | Awards: 0 vs 15, City adj: 10 vs 20 | Card VP 35 (won!), 2 milestones, VP-per-resource strategy worked |
| Game 5 vs John (2p, Tharsis, Prelude)   | Lost 120–155 | Awards: 0 vs 15, City adj: 9 vs 25, Economy: 20 vs 61 MC prod | Card VP 37, 2 milestones (first 2-claim), TR 52 (best ever), ECF+Ants combo 8 VP |
| Game 6 vs John (2p, Tharsis, Prelude)   | Lost 110–162 | Awards: 0 vs 15 (funded Scientist, lost to late Adaptation Tech), 3-milestone cap blocked Mayor, City adj 8 vs 20 | Card VP 38 (best!), Terraformer, TR 52, PhoboLog+Satellites engine, Ants 7 VP |
| Game 7 vs John (2p, Tharsis, Prelude)   | Lost 96–162  | Awards: 0 vs 15 (funded Banker+Thermalist, lost BOTH to late MC/heat engine), Terraforming Ganymede +8 TR, Gen 13 mega-turn +38 VP | Mayor, TR 51, QE+EM chain (+5 TR), ICS 4 VP, Ants 6 VP, CS+RW +6 MC prod combo |
