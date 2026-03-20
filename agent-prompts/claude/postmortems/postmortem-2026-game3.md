# Post-Mortem: Game 3 (Claude red vs John blue) — Tharsis, 2-player, Prelude, 12 gens

**Result: Lost 93–163 (–70 VP)**

## Final Score Breakdown

| Category | Claude (red) | John (blue) |
|---|---|---|
| TR | 50 | 51 |
| Milestones | 10 (Builder + Terraformer) | 5 (Gardener) |
| Awards | 0 | 15 (Banker 1st + Landlord 1st + Miner 1st) |
| Greenery tiles | 8 | 13 |
| City adjacency | 10 | 22 |
| Card VP | 15 | 57 (–4 negative) |
| **Total** | **93** | **163** |

## Corporations & Key Cards

- **Claude**: Cheung Shing MARS + Business Empire (+9 MC prod gen 1), Electro Catapult + Advanced Alloys steel engine, Standard Technology + Standard Asteroid rebate, Protected Habitats
- **John**: CrediCor + Mars University, Development Center, Inventors' Guild, Business Network, Anti-Gravity Tech discount engine

## What Went Right

### 1. Claimed 2 milestones early (10 VP)
Builder claimed Gen 3, Terraformer claimed Gen 5. Applied the lesson from Game 2 (0 milestones) successfully. 10 VP from 16 MC = 1.6 MC/VP, the best rate in the game.

### 2. Strong early economy
Business Empire gave +9 MC production from Gen 1. This funded early plays and milestone claims. Economy was functional throughout.

### 3. Steel engine worked
Electro Catapult + Advanced Alloys created an effective steel-based economy. Building tags flowed naturally, enabling the Builder milestone.

### 4. Protected Habitats blocked resource theft
Applied the Game 2 lesson — drafted and played Protected Habitats. This prevented direct resource removal (plants, animals, microbes). However, it does NOT protect against production theft (Birds –2 plant prod, Fish –1 plant prod).

### 5. Good TR management
Reached TR 50, matching John's 51. Standard Technology + Standard Asteroid rebate combo helped sustain TR pushes efficiently.

## What Went Wrong

### 1. AWARDS DISASTER: 22 MC spent, 0 VP gained (–22 MC and gifted John 15 VP)

This was the single worst strategic mistake of all three games.

- **Funded Banker** (8 MC) — was winning at time of funding. John's MC production then exploded in late game: Capital (+5 MC prod), Gene Repair (+2), Cartel (+4), Space Hotels (+4), Kelp Farming (+2) = 17+ MC prod gained in final 3–4 gens. John finished Banker at 27 MC prod vs my 20.

- **Funded Landlord** (14 MC) — was winning tiles at time of funding. John's 18 plant production flooded the board with greeneries, going from 5 tiles to 21 tiles in the final gens. Each 8 plants = 1 greenery tile = 1 tile for Landlord count.

**Root cause**: I evaluated awards based on current state, not projected state. MC production can swing 10+ in 2–3 generations from single cards like Capital, Cartel, Space Hotels. Plant production of 10+ means 2+ greeneries per generation, each counting as a tile for Landlord. Funding an award you end up losing is a –10 VP swing (you spend MC and the opponent gets 5 VP from your funded award).

**New rule**: Never fund an award unless the lead is insurmountable OR you can maintain the lead through the endgame. Specifically:
- Banker: only fund if your MC prod lead is 10+ AND opponent has no obvious MC prod cards in hand
- Landlord: NEVER fund if opponent has 8+ plant production — they WILL flood tiles
- Any award at 14 MC (2nd funding): the 14 MC cost means you need near-certainty of winning

### 2. CARD VP GAP: 15 vs 57 (–42 VP) ← THE DECISIVE FACTOR

John's VP-per-resource cards generated massive VP:
- Ecological Zone: 6 VP (animals)
- Birds: 5 VP (animals, also stole my plant prod)
- Fish: 5 VP (animals, also stole my plant prod)
- Pets: 4 VP (animals)
- Io Mining Industries: 7 VP (Jovian tags)
- Ganymede Colony: 7 VP (Jovian tags)
- Terraforming Ganymede: 2 VP
- Anti-Gravity Tech: 3 VP
- Security Fleet: 3 VP (fighters)
- Various others

My card VP came from static 1–2 VP cards. I had ZERO VP-per-resource cards (no animals, no fighters, no scaling VP).

**Root cause**: I did not prioritize drafting VP-per-resource cards. Cards like Ecological Zone, Birds, Fish, Pets, and Security Fleet each generate 3–7 VP by accumulating resources over time. They are the primary source of card VP in competitive games. Static VP cards (1–2 VP each) cannot compete with resource-accumulating VP cards.

**New rule**: Draft at least 2–3 VP-per-resource cards (animal, microbe, or fighter cards) by mid-game. These cards are:
- Animals: Ecological Zone, Birds, Fish, Pets, Predators, Small Animals, Livestock
- Fighters: Security Fleet
- Microbes: Decomposers, Lichen (static but cheap)
- Jovian VP: Io Mining Industries, Ganymede Colony (scale with Jovian tags)

### 3. CITY ADJACENCY: 10 vs 22 (–12 VP)

John had 6 cities with 13+ greeneries clustered around them. His 18 plant production meant 2+ greeneries per generation in the late game, all placed adjacent to his cities. I had 4 cities but only 8 greeneries nearby.

**Root cause**: Plant production disparity. John's 18 plant prod vs my 0 (after Birds and Fish stole my 3 plant prod) meant he controlled late-game board placement entirely. More cities + more greeneries = exponentially more adjacency VP.

### 4. LATE-GAME TR SWING: Terraforming Ganymede + 7 Jovian tags = +8 TR

John played Terraforming Ganymede with 7 Jovian tags, jumping from TR 43 to TR 51 in the final generation. This single card was worth 8 VP (TR) plus the card's own VP.

**Root cause**: I did not track John's Jovian tag count. With 7 Jovian tags, Terraforming Ganymede is one of the highest single-play VP swings in the game. I should have monitored his Jovian tags and anticipated this play.

### 5. PLANT PRODUCTION THEFT: 3 prod to 0

- Birds: –2 plant production
- Fish: –1 plant production

Protected Habitats only protects RESOURCES (plants on your player board, animals/microbes on cards), NOT PRODUCTION. Production theft is a different mechanic and cannot be blocked.

Going from 3 plant prod to 0 meant I generated zero plants per generation in the late game, while John's 18 plant prod dominated the board.

**Root cause**: Misunderstanding the scope of Protected Habitats. It blocks resource removal but not production reduction. There is no card that blocks production theft — the only counter is to have enough plant production that losing 3 still leaves you competitive, or to not rely on plant production at all.

### 6. CARD DRAW ENGINE: John played 60 cards to my 37

John's card engine was devastating:
- Mars University: draw on science tag plays
- Development Center: draw cards with energy
- Inventors' Guild: buy cards with actions
- Business Network: look at top card each gen
- Anti-Gravity Tech: –2 MC on all cards

This compound card advantage meant John saw more VP cards, more production cards, and more options every generation. Playing 60 cards vs 37 is a 62% card throughput advantage.

**Root cause**: I had no card draw engine. In a 12-gen game, seeing 10–20 extra cards means finding 3–5 more VP cards. Card draw compounds — each card drawn can draw more cards or generate more VP.

## Key Decisions in Retrospect

| Decision | What I Did | Better Alternative |
|---|---|---|
| Fund Banker | Funded at 8 MC with current lead | Wait — MC prod is volatile, 10+ swings possible |
| Fund Landlord | Funded at 14 MC with current tile lead | Never fund when opponent has 8+ plant prod |
| Card drafting | Prioritized engine/economy cards | Draft 2–3 VP-per-resource cards (animals, fighters) |
| Card draw | No draw engine | Prioritize Mars University, Dev Center, or similar |
| Plant prod theft | Relied on Protected Habitats | PH doesn't block prod theft — need higher base plant prod or pivot away from plants |
| Jovian tracking | Didn't monitor John's Jovian count | Track opponent tags for Terraforming Ganymede / Io Mining |

## Comparison with Games 1 and 2

| Factor | Game 1 (Lost 99–101) | Game 2 (Lost 79–115) | Game 3 (Lost 93–163) |
|---|---|---|---|
| Milestones | 10 VP (2 claimed) | 0 VP | 10 VP (2 claimed) |
| Awards | 5 VP (Miner 1st) | 5 VP (Banker 1st) | 0 VP (funded 2, lost both) |
| City adjacency | 0 | 6 | 10 |
| Card VP | 25 | 18 | 15 |
| TR | 49 | 44 | 50 |
| Loss margin | –2 VP | –36 VP | –70 VP |

Progression: Milestones improved (Game 2 lesson applied). City adjacency improved (Game 1 lesson applied). But card VP has DECLINED each game (25 -> 18 -> 15), while opponents' card VP has increased. Awards went from positive to catastrophic. The card VP gap is now the primary problem area.

## Final Lessons

1. **Award funding must account for FUTURE production, not current state.** MC production can swing 10+ in 2–3 gens. Plant production of 10+ generates 2+ tiles per gen. Never fund awards unless the lead is insurmountable through the endgame. Funding an award you lose is a –10 VP swing (MC spent + opponent gets 5 VP).

2. **VP-per-resource cards are the primary source of competitive card VP.** Animal cards (Ecological Zone, Birds, Fish, Pets), fighter cards (Security Fleet), and Jovian-scaling cards (Io Mining, Ganymede Colony) each generate 3–7+ VP. Static 1–2 VP cards cannot compete. Draft at least 2–3 of these by mid-game.

3. **Card draw engines compound massively.** Mars University + Development Center + Inventors' Guild let John play 60 cards to my 37. More cards = more VP cards found and played. Prioritize at least one card draw mechanism.

4. **Protected Habitats does NOT block production theft.** Birds (–1 plant prod) and Fish (–1 plant prod) bypass Protected Habitats. There is no counter to production theft — the only defense is redundant production or pivoting away from the stolen resource.

5. **Track opponent Jovian tags.** Terraforming Ganymede with 7+ Jovian tags is a game-winning play worth 8+ TR in a single action. Monitor opponent tag counts to anticipate late-game VP swings.

6. **18 plant production is board domination.** Once an opponent reaches 10+ plant prod, they generate 2+ greeneries per gen, controlling Landlord, city adjacency, and oxygen TR. Either match their plant production or concede the board and win elsewhere (cards, TR, milestones).
