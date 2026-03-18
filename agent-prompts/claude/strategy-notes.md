# Claude's Terraforming Mars Strategy Notes

Lessons learned from actual games, layered on top of the GUIDE.md framework.
Update this file after each game.

---

## The Most Important Things I've Learned

### 1. Milestones are worth more than any engine

In Game 2, John swept all 3 milestones (15 VP) while I got 0. That 15 VP swing was worth more than my entire microbe combo engine generated. Milestones cost 8 MC each for 5 VP = 1.6 MC/VP. **No card, engine, or strategy comes close to this efficiency.** Claiming even 1 milestone must be the #1 priority from Gen 1. Plan your opening around which milestone you can reach first.

### 2. City-greenery adjacency VP is as large as TR itself

A player with 4 well-placed cities can score 12–20 VP purely from adjacency. In Game 1 I had 0 city VP; in Game 2 I improved to 6 VP with 2 clustered cities. John scored 11 (Game 2) and 16 (Game 1) from cities.

**This means: build 2–3 cities early ON MARS, cluster them, then flood adjacent hexes with greenery.**

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

1. **Fund an award if**: you're currently winning it AND the lead is **structural** (high production, massive stockpile), AND the 8 MC cost is worth 5 VP (it nearly always is at first funding)
2. **Don't fund volatile awards**: Tag-based awards (Scientist, Builder) can flip over 8+ generations. A 4-1 lead in Gen 3 means nothing when the opponent has 8 gens to play cheap tag cards. In Game 2, I funded Scientist at 4-1 lead; John finished 8-6 and won MY award.
3. **Structural leads are safe to fund**: Banker (high MC prod is hard to catch), Miner (massive resource stockpiles), Landlord (significant tile lead). These are much harder to overturn.
4. **Don't fund an award if**: an opponent is clearly going to win it regardless — you're just subsidizing their VP
5. **Contest an award if**: an opponent funds an award you could plausibly win — pivot your strategy to challenge them
6. **Deny by funding a different award**: force opponent to spend 14 MC (2nd) or 20 MC (3rd) on their preferred award

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

## Tactical Reminders

1. **Race for milestones from Gen 1** — they are the single highest-VP-per-MC source in the game. Plan your opening around them.
2. **Build 3 cities ON MARS by Gen 5–6** — claim Mayor and set up adjacency VP. Off-board cities are for VP, not milestone racing.
3. **Use `get_mars_board_state` before placing any tile** to optimize adjacency
4. **Never play –VP cards** in close games unless the benefit is overwhelming
5. **Fund awards only with structural leads** — tag-based leads (Scientist, Builder) are volatile. Production/resource leads (Banker, Miner) are safe.
6. **Draft Protected Habitats in 2-player** — it blocks plant/animal/microbe removal and is game-warping
7. **Convert all plants and heat** before passing — leave nothing on the table
8. **Standard project greenery near own cities** is efficient VP in final gens
9. **Track opponent city locations** — don't gift them greenery adjacency VP
10. **Caretaker Contract + microbe combos** are powerful late-game TR engines — keep microbes cycling
11. **Titanium** is 3 MC/unit for space tags — prioritize space cards to spend it
12. **When opponent has Ants**, spread microbes across multiple cards to minimize per-card theft impact

---

## Game Log

| Game                                    | Result       | Key Loss Factor      | Key Win Factor                   |
| --------------------------------------- | ------------ | -------------------- | -------------------------------- |
| Game 1 vs Codex (2p, Tharsis, Prelude)  | Lost 99–101  | City VP: 0 vs 16     | Card VP 25, TR 49, 2 milestones  |
| Game 2 vs John (2p, Tharsis, Prelude)   | Lost 79–115  | Milestones: 0 vs 15  | MC prod 24, TR 44, Banker award  |
