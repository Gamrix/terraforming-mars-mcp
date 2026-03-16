# Claude's Terraforming Mars Strategy Notes

Lessons learned from actual games, layered on top of the GUIDE.md framework.
Update this file after each game.

---

## The Most Important Thing I've Learned

**City-greenery adjacency VP is as large as TR itself.** A player with 4 well-placed cities can score 12–20 VP purely from adjacency (1 VP per adjacent greenery per city). In the game I lost, I had 18 greeneries on the board but only 1 isolated city — scoring 0 city VP. Codex had 4 cities and scored 16. The –16 swing was the entire margin.

**This means: build 2–3 cities early, cluster them, then flood adjacent hexes with greenery.**

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
3. **Flood with greenery** in the late game — every plant converted or standard project greenery placed near your cities is 2 VP (1 tile + 1 city adjacency) instead of 1 VP

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

1. **Fund an award if**: you're currently winning it AND you can maintain the lead, AND the 8 MC cost is worth 5 VP (it nearly always is at first funding)
2. **Don't fund an award if**: an opponent is clearly going to win it regardless — you're just subsidizing their VP
3. **Contest an award if**: an opponent funds an award you could plausibly win — pivot your strategy to challenge them
4. **Deny by funding a different award**: if Codex is building toward Thermalist, fund Miner or Banker to force Codex to spend 14 MC on the second award instead of 8 MC

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

### Things to look for in corporation selection
1. Does it synergize with a clear award target? (Thermalist → Helion, Scientist → Interplanetary Cinematics/Research)
2. Does it give early economic advantage (steel/titanium production)?
3. Does it enable the city-greenery VP engine? (Tharsis Republic is ideal: free city + MC prod per city)

---

## Tactical Reminders

1. **Use `get_mars_board_state` before placing any tile** to optimize adjacency
2. **Never play –VP cards** in close games unless the benefit is overwhelming
3. **Build 2–3 cities** by Gen 7–8 in good positions, then surround with greeneries
4. **Claim milestones the moment eligible** — don't wait
5. **Fund awards only when winning them** or as denial play
6. **Convert all plants and heat** before passing — leave nothing on the table
7. **Standard project greenery near own cities** is efficient VP in final gens
8. **Track opponent city locations** — don't gift them greenery adjacency VP
9. **Caretaker Contract + NRB microbes** are powerful late-game TR engines — keep microbes cycling
10. **Titanium** is 3 MC/unit for space tags — prioritize space cards to spend it

---

## Game Log

| Game | Result | Key Loss Factor | Key Win Factor |
|---|---|---|---|
| Game 1 vs Codex (2p, Tharsis, Prelude) | Lost 99–101 | City VP: 0 vs 16 | Card VP 25, TR 49, 2 milestones |
