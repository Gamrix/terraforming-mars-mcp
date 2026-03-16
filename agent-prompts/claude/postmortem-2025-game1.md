# Post-Mortem: Game 1 (Claude red vs Codex blue) — Tharsis, 2-player, Prelude

**Result: Lost 99–101 (–2 VP)**

## Final Score Breakdown

| Category | Claude (red) | Codex (blue) |
|---|---|---|
| TR | 49 | 48 |
| Milestones | 10 (Gardener + Builder) | 5 (Terraformer) |
| Awards | 5 (Miner 1st) | 10 (Scientist 1st + Thermalist 1st) |
| Greenery tiles | 10 | 8 |
| City adjacency | 0 | 16 |
| Card VP | 25 | 14 |
| Negative VP | –3 | 0 |
| **Total** | **99** | **101** |

## Corporations & Preludes

- **Claude**: Point Luna (draw card on Earth tag plays, –2 MC/card) + Polar Industries (titanium prod) + Metals Company (steel prod)
- **Codex**: Cheung Shing MARS (–2 MC discount on building tags) + Experimental Forest + Mohole

## What Went Right

- **TR engine**: Closed a 7-TR deficit Codex built with Giant Ice Asteroid + Nitrogen-Rich Asteroid using Terraforming Ganymede (+4 TR from 4 Jovian tags), Caretaker Contract (heat→TR), NRB microbe cycles, and greeneries. Ended with TR 49 vs 48.
- **Milestones**: Claimed both Gardener and Builder (10 VP). Codex only claimed Terraformer (5 VP). +5 net.
- **Card VP engine**: Security Fleet (5 fighters = 5 VP), Terraforming Ganymede (2 VP), Farming (2 VP), Phobos Space Haven (3 VP), Asteroid Mining (2 VP), Large Convoy (2 VP), plus 9× 1 VP cards. Total 25 card VP — 11 VP ahead of Codex.
- **Titanium optimization**: Ti production hit 8/gen, used for Space Elevator, Large Convoy, Beam from Thorium Asteroid, Terraforming Ganymede, Miranda Resort, Vesta Shipyard. Ti heavily subsidized space card costs.
- **Plant production**: 8 plant prod yielded multiple greeneries per game, maxing oxygen and claiming Gardener milestone.
- **Final gen execution**: NRB TR+1, Caretaker TR+1, plant greenery, Security Fleet fighter, Space Elevator steel→MC, Dev Center draw, Rover Construction (1 VP), Vesta Shipyard (1 VP), 2× standard Greenery SP.

## What Went Wrong

### 1. City VP gap: 0 vs 16 (–16 swing) ← THE DECISIVE FACTOR

I had **1 city** (Phobos Space Haven) that scored 0 city adjacency VP. Codex had **4 cities** with greeneries clustered around them, scoring 16 city VP.

With 18 greeneries placed on the board total, there were enormous VP available from city-greenery adjacency. I had the greeneries but not the cities positioned to benefit.

**Root cause**: I never built cities strategically. Phobos Space Haven placed a city but it was isolated. I relied on plant production for greeneries but never invested in cities to harvest their adjacency bonus.

**What should have happened**: In the mid-game, use standard project City (25 MC) or play city cards (Cupola City, Capital, Immigrant City) and cluster 2–3 cities adjacent to each other, then surround them with greeneries. Each city touching 3–4 greeneries is worth 3–4 VP. Codex's Underground City + Immigrant City + Cupola City + SF Memorial city placements set this up perfectly.

### 2. Award losses: –5 net

- Funded Miner myself (8 MC) → won it (22 steel/Ti vs Codex's 4). Gained 5 VP.
- Codex funded Thermalist → won easily (36 heat vs my 21). Codex gained 5 VP.
- Codex funded Scientist → won (7 science tags vs my 3). Codex gained 5 VP.

Net: I got 5 VP from awards, Codex got 10 VP. I was never in position to contest Thermalist (Codex had massive heat from Mohole + heat production) or Scientist (Codex had Research + SF Memorial + 7 science tags vs my 3). Funding Miner early was correct since I was clearly winning it, but I should have evaluated whether I could deny one of Codex's awards by funding a competing award or building toward Thermalist.

### 3. Negative VP cards: –3 VP

- Indentured Workers: –1 VP
- Bribed Committee: –2 VP

In a 2 VP loss, these 3 negative VP cards were decisive. Indentured Workers gave a card cost discount but the card it enabled probably wasn't worth –1 VP. Bribed Committee saved MC on a requirement bypass but –2 VP in a close game is extremely expensive. **Avoid both unless the enabled play is worth the negative VP in excess.**

### 4. Greenery placement without adjacency analysis

My standard project greeneries (spaces 16, 17, 11) were placed without checking adjacency to my cities. With the board state available, I should have placed greeneries adjacent to Phobos Space Haven's city tile. I also placed the final plant-conversion greenery at space 11 without adjacency optimization.

## Key Decisions in Retrospect

| Decision | What I Did | Better Alternative |
|---|---|---|
| City building | Relied on Phobos only; 0 city VP | Play City SP or city cards mid-game, target 3 cities in a cluster |
| Negative VP cards | Played Indentured Workers (–1) + Bribed Committee (–2) | Skip both unless enabled card gives >3 VP advantage |
| Final gen greeneries | Placed at spaces 16, 17, 11 blindly | Load board state, target spaces adjacent to own cities |
| Thermalist award | Let Codex run away with it | Either race heat production to challenge, or let Codex overpay by not funding a competing award |

## Final Lesson

The game was lost entirely on city VP. **In 2-player TM, the city-greenery adjacency engine is as powerful as the plant production engine — you need both.** Codex built 4 well-positioned cities and scored 16 VP from adjacency while I had 18 greeneries but only 1 isolated city.

The 2 VP loss margin also shows how much negative VP cards cost: Indentured Workers + Bribed Committee = –3 VP in a –2 VP loss. Avoid them.
