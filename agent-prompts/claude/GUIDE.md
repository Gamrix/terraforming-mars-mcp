# The definitive Terraforming Mars strategy guide

This guide has been prepared for you by the Claude Deep Research Agent

**Terraforming Mars rewards the player who converts MegaCredits into victory points most efficiently—and understanding that single principle transforms a beginner into a competitor.** This guide distills insights from competitive tournament players, the renowned BGG "Quantified Guide to TM Strategy," and hundreds of community strategy threads into a complete framework for winning. Whether you're playing your first game or preparing for tournament play, the concepts here build from foundational mechanics through advanced optimization, covering every strategic dimension of the game.

The core tension in Terraforming Mars is tempo versus engine: spend resources now to terraform (raising your Terraforming Rating and shortening the game) or invest in production that compounds over many generations. Every decision flows from this tension. **The best players don't commit to one approach—they read the table and adapt.**

---

## How the game actually works, generation by generation

Each game of Terraforming Mars consists of multiple generations (rounds), each with four phases. In the **Player Order Phase**, the first player marker passes clockwise and the generation counter advances. During the **Research Phase**, every player draws 4 cards and may buy any number at **3 MC each** (this phase is skipped in Generation 1, since players already selected starting cards). The **Action Phase** is where the game lives: players take turns clockwise, performing 1 or 2 actions per turn, until everyone passes. Finally, the **Production Phase** converts all energy to heat, then pays income (MC equal to your Terraforming Rating plus your MC production) and produces all other resources according to production tracks.

The game ends when all three global parameters are maxed: **temperature at +8°C** (19 steps from -30°C, each step = 2°C), **oxygen at 14%** (14 steps from 0%), and **all 9 ocean tiles placed**. This creates exactly **43 TR points** available from terraforming (19 + 14 + 9, plus a bonus temperature step at 8% oxygen). The game finishes at the end of that generation—after the production phase, players get one final chance to convert plants into greenery tiles.

Scoring combines your TR (which doubles as both ongoing income and final VP), greenery tiles (1 VP each), city tiles (1 VP per adjacent greenery regardless of who owns it), milestone points, award points, and VP printed on played cards. Tiebreaker goes to remaining MC, then unplayed cards in hand.

### The six resources and what they're really worth

Understanding resource equivalencies is fundamental to evaluating every card and action:

| Resource | Production Value | Conversion | Derived MC Value |
|----------|-----------------|------------|-----------------|
| **MegaCredits** | Universal currency | Pays for everything | 1 MC = 1 MC |
| **Steel** | Building tag payments | 1 steel = 2 MC (building cards only) | ~2 MC |
| **Titanium** | Space tag payments | 1 titanium = 3 MC (space cards only) | ~3 MC |
| **Plants** | 8 → greenery tile | +1 oxygen, +1 TR, +1 VP tile | ~2.9 MC per plant |
| **Energy** | Powers card effects | Leftover converts to heat | ~1.75 MC |
| **Heat** | 8 → temperature step | +1 TR | ~1.75 MC per heat |

These equivalencies derive from standard project costs. The Greenery standard project costs 23 MC for what 8 plants accomplish, making each plant worth roughly **2.9 MC**. The Asteroid standard project costs 14 MC for what 8 heat accomplish, making each heat worth roughly **1.75 MC**. Plants are dramatically more valuable than heat because greenery provides both TR *and* a permanent VP tile, while heat provides only TR.

---

## Corporations shape everything—choose wisely

Your corporation determines starting resources, ongoing abilities, and which cards become playable. In competitive play, corporation selection is arguably the single most impactful decision you'll make.

### Base game corporation tier list

**S-Tier (consistently dominant):**

**Tharsis Republic** starts with 40 MC, places a free city as its first action, and gains +1 MC production whenever *any* city is placed on Mars plus 3 MC when you place one yourself. The free city provides immediate board presence, the MC production snowballs across the entire game, and the corporation naturally pursues the Mayor milestone. In a 4-player game where 8-12 cities might be placed, that ability alone generates **8-12+ MC production** over the game. Near-universally ranked #1 among base game corporations.

**Ecoline** starts with 36 MC, 2 plant production, and 3 plants, and converts greenery at **7 plants instead of 8**—a persistent 12.5% discount on the game's strongest endgame action. This corporation makes plant production cards roughly 14% more efficient and naturally locks up the Gardener milestone. In 2-player games, Ecoline is borderline overpowered because fewer opponents means fewer asteroid attacks on your plants.

**A-Tier:** **Credicor** (57 MC starting, 4 MC rebate on expensive plays ≥20 MC) offers tremendous flexibility and forgiveness. The rebate triggers on standard projects too, making Aquifers and Cities meaningfully cheaper. Excellent for beginners.

**B-Tier:** **Interplanetary Cinematics** (30 MC + 20 steel, effectively ~70 MC for building cards), **Phobolog** (23 MC + 10 titanium at 4 MC each = 40 MC for space cards; space cards are disproportionately VP-rich), **Saturn Systems** (steady MC production from any player's Jovian tags), **Teractor** (60 MC + 3 MC discount on Earth cards).

**C-Tier:** **Helion** (heat-as-MC is flexible but inefficient), **Mining Guild** (placement-dependent, easily blocked), **Thorgate** (niche energy discount).

**D-Tier:** **Inventrix** (marginal flexibility, mediocre economy), **UNMI** (weakest base corp—the 3 MC → 1 TR action requires having already raised TR that generation, and it starts with no production or resources).

### Expansion corporations that warp the game

From expansions, several corporations are considered a tier above the base game's best. **Poseidon** (Colonies) has the highest competitive win rates—a free colony placement plus +1 MC production whenever any colony is placed creates compound economic growth. **Manutech** (Venus Next) effectively doubles every production increase by granting that resource when you gain production—some consider it overpowered. **Terralabs Research** (Turmoil) pays only **1 MC per card** instead of 3, creating staggering card advantage over a full game despite starting at just 14 MC and -1 TR. **Polyphemos** (Colonies) starts with 50 MC, 5 MC production, and 5 titanium but pays 5 MC per card—a raw economic powerhouse.

---

## Card drafting is where games are won and lost

With the draft variant (mandatory in competitive play), each generation you draw 4 cards, keep 1, pass 3 to your neighbor, receive 3, keep 1, pass 2, and so on until all 4 are distributed. You then decide which of your 4 drafted cards to actually *buy* at 3 MC each. This two-layer decision—what to draft and what to buy—is where skill separates from luck.

### The card evaluation framework

Every card should be assessed against a simple question: **how many VP does this generate per MC invested, and does that beat my alternatives?**

The baseline for VP efficiency comes from standard projects. The Asteroid (14 MC for 1 TR) sets the floor at **14 MC per VP**—if a card can't beat this ratio, it's probably not worth playing. The key benchmarks competitive players use:

- **≤7 MC/VP**: Excellent—always play (e.g., Breathing Filters, Colonizer Training Camp at 5.5 MC/VP)
- **7-10 MC/VP**: Good—play if it fits your engine
- **10-14 MC/VP**: Marginal—only with strong synergy or tag value
- **>14 MC/VP**: Below standard project efficiency—usually skip

Remember to include the **3 MC draft cost** in every calculation. A card with a printed cost of 10 MC that gives 2 VP actually costs 13 MC total (10 + 3 buy cost) = 6.5 MC/VP. Tags also carry hidden value: they trigger corporation abilities, count toward milestones like Builder (8 building tags), enable future cards with tag requirements, and synergize with scoring cards like Terraforming Ganymede.

### Production cards have a shelf life

For production-boosting cards, the math is straightforward: **total cost ÷ production increase = generations to break even**. A card costing 13 MC (10 + 3 draft) that provides +3 MC production breaks even in roughly 4.3 generations. If fewer than 5 generations remain, skip it. This "remaining generations" calculation is the single most important heuristic for card buying decisions. Each MC of production gained in Generation 1 of a 10-generation game yields 10 MC total. The same production gained in Generation 8 yields only 3 MC—an 70% reduction in value.

### When to buy versus pass

**Always buy:** Cards playable immediately that beat 10 MC/VP, critical engine pieces matching your corporation, cards needed to claim milestones. **Usually pass:** Cards with requirements you won't meet for 4+ generations, pure VP cards in the early game when your economy needs building, cards above 10 MC/VP without strong synergy. **The cardinal sin of card buying is hoarding.** Aim to hold **4-6 cards maximum** in hand. Each unplayed card represents 3 MC of frozen capital doing nothing.

---

## Building your economic engine across three phases

The game naturally divides into three strategic phases, and understanding when to transition between them separates strong players from average ones.

### Early game (Generations 1-3): build the machine

Every MC spent on production in the first three generations compounds across the remaining 7-10 generations. **Prioritize MC production, steel, and titanium above all else.** Competitive production benchmarks by the end of Generation 3 in an experienced 4-player game: **MC income of 25-30 per generation** (TR + MC production combined), steel production of 3-4, and at least modest plant or heat production. Players consistently hitting these targets score 80+ points.

Avoid the beginner trap of playing flashy VP cards or expensive science setups in these generations. A 15 MC VP card played in Generation 2 could have been a production card generating 30+ MC over the remaining game. As one veteran puts it: "Spending your starting capital on cards that only give victory points will make you lose."

### Mid game (Generations 4-7): leverage and position

Your engine should now be producing enough to fund both terraforming actions and board positioning. This is the critical window for **claiming milestones** (which are the most efficient VP source in the game), **funding awards** you're positioned to win, and establishing city-greenery clusters on the board. Play cards that both advance your economy and contribute VP—the best mid-game cards do double duty.

### Late game (final 2-3 generations): the VP pivot

When a production increase can no longer pay for itself before the game ends, **stop building engine and start buying points**. Convert plants to greenery, heat to temperature, and MC to standard projects. Play every VP card in your hand. Place greenery adjacent to your own cities for maximum adjacency scoring. This pivot point isn't fixed—it depends on counting remaining terraforming steps and estimating how many generations remain.

### Balancing the six production types

**MC production** is universally valuable and should be your first investment. **Steel** is the second priority—building-tagged cards are the most numerous in the deck, and each steel effectively doubles your spending on those cards. **Titanium** is higher per-unit value but narrower; invest heavily only if you have space cards to spend it on. **Plant production** is the best long-term VP engine since greenery yields both TR and tile VP, but plants are vulnerable to opponent attacks. **Energy production** is primarily a prerequisite for powerful blue cards; leftover energy converts to heat. **Heat production** is the most straightforward path to TR since temperature has 19 steps—the largest parameter pool.

---

## Terraforming Rating is income now and points forever

Each point of TR serves dual purpose: **+1 MC income every future generation** and **+1 VP at game end**. This dual nature means TR gained early is dramatically more valuable than TR gained late. The competitive community estimates **1 TR ≈ 10 MC in total value** when gained in the early-to-mid game, reflecting both the VP component and cumulative income.

The math is stark. TR gained in Generation 2 of a 10-generation game produces 8 additional MC of income over the remaining game, plus 1 VP at endgame (worth roughly 5 MC equivalent)—about 13 MC total value. TR gained in Generation 9 produces only 1 MC of future income plus 1 VP—about 6 MC total value. **Early TR is worth more than twice as much as late TR.**

### When to push TR aggressively

Push hard when you're in the first half of the game and have efficient terraforming cards, when you want to shorten the game against opponents building slow engines, when you're pursuing the Terraformer milestone (TR 35), or when your corporation naturally terraforms (Ecoline with plants, Helion with heat). Aggressive TR-pushing is also a legitimate competitive strategy called the "terraforming rush"—maximize direct terraforming actions, skip engine building, and end the game before opponents can deploy their accumulated cards.

### When to push TR passively

Ease off when the game is in its final stages (low income return), when you have a powerful VP card engine that needs more generations to mature, when other players are already pushing parameters toward completion (free-riding on their efforts to end the game), or when global parameters are nearly maxed with diminishing opportunities.

Temperature track bonuses at **-24°C and -20°C** (each granting +1 heat production to the player who reaches them) and the **ocean tile at 0°C** create race incentives. Similarly, reaching **8% oxygen** triggers a bonus temperature step. Competitive players actively race for these bonuses.

---

## Milestones and awards: the most efficient VP in the game

### Milestones are non-negotiable

At **5 VP for just 8 MC**, milestones cost roughly **1.6 MC per VP**—approximately seven times more efficient than standard project VP sources. Only 3 of the 5 can be claimed per game, and each is exclusive to one player. In competitive play, claiming a milestone is almost always correct when eligible.

The five base game milestones ranked by achievability: **Builder** (8 building tags—easiest since building is the most common tag), **Gardener** (3 greenery tiles—straightforward with plant production), **Mayor** (3 city tiles—requires significant investment), **Terraformer** (TR 35—demands 15 TR increases, achievable mid-to-late game), and **Planner** (16 cards in hand—widely considered the hardest and least worthwhile, since hoarding unplayed cards contradicts good strategy).

**Timing is critical.** Don't wait until you've met the requirement—by then an opponent may have claimed it first. Start positioning 1-2 generations before you'll qualify. If you see two opponents racing for Mayor, pivot to Builder or Gardener where competition is lighter. Getting even one milestone in a competitive game is significant; claiming two is a major advantage.

### Awards demand careful calculation

Awards use an escalating cost structure: **8 MC** for the first funded, **14 MC** for the second, **20 MC** for the third. Unlike milestones, anyone can win a funded award regardless of who paid for it—the funder gets no special consideration. First place earns 5 VP, second place earns 2 VP (except in 2-player games where no second place is awarded).

The five base game awards: **Landlord** (most tiles owned on the board), **Banker** (highest MC production), **Scientist** (most science tags in play), **Thermalist** (most heat cubes at game end), and **Miner** (most steel + titanium cubes at game end). Note that Thermalist and Miner count *resource cubes*, not production—players can stockpile these resources deliberately in the final generations.

Fund awards strategically: the first award at 8 MC is excellent efficiency if you're likely to win. The third at 20 MC is marginal and should only be funded with high confidence or as a denial play. **Defensive funding**—funding an award where multiple opponents compete—forces them to fight each other instead of focusing on you.

---

## Standard projects and conversions: your safety net

Standard projects are always available but intentionally overpriced by approximately **3 MC** compared to equivalent card actions. They exist as a floor—you can always terraform or build, even with a weak hand.

The **Asteroid** (14 MC, raise temperature) is the most MC-efficient standard terraforming action and sets the competitive baseline for VP evaluation. The **Aquifer** (18 MC, place ocean) is more expensive but includes placement bonuses that can reduce effective cost to 15-16 MC. The **Greenery** (23 MC, place greenery + raise oxygen) is expensive but yields approximately **2 VP** (1 tile VP + 1 TR from oxygen), making it roughly 11.5 MC/VP—competitive with many cards. The **City** (25 MC + 1 MC production) is most valuable early when adjacent greenery potential is high. The **Power Plant** (11 MC, +1 energy production) is the weakest standard project and should almost never be used. **Selling Patents** (discard cards for 1 MC each) is a desperation play since cards cost 3 MC to acquire.

The plant-to-greenery conversion (8 plants → greenery) and heat-to-temperature conversion (8 heat → temperature step) are free standard actions that don't cost MC. They represent the primary way production engines translate into points. **Never end the game with unconverted plants or heat**—after the final production phase, all players can still convert remaining plants to greenery in player order.

---

## Tile placement is a spatial puzzle with hidden depth

### Cities: plan for adjacency scoring

Cities score **1 VP per adjacent greenery at game end**, regardless of who owns the greenery. A city surrounded by 6 greenery tiles scores 6 VP. The optimal approach is to place cities where you can later surround them with your own greenery, capturing both the 1 VP per greenery tile and the adjacency VP on your city. **Placing cities adjacent to oceans** is high-value—you collect 2 MC per adjacent ocean as a placement bonus, and ocean hexes don't block future greenery placement.

A powerful pattern is the **triangle formation**: three cities positioned so they share adjacent hexes, allowing you to surround all three with greenery tiles that each benefit multiple cities. Three well-placed cities with full greenery rings can generate **15-18+ VP** from city scoring alone.

### Greenery: every tile is a strategic commitment

Greenery must be placed adjacent to a tile you already own (if possible), so your board presence constrains your options. Each greenery is worth **1 VP** to its owner plus **1 VP to any adjacent city** (any player's). This means placing greenery next to your own city generates 2 VP for you, but placing it next to an opponent's city gifts them 1 VP—a critical consideration.

In the late game, greenery is the primary VP engine. Plant production converts to greenery at no MC cost, and even the expensive 23 MC standard project greenery yields roughly 2 VP (TR + tile), making it competitive. **Place greenery to maximize your own city adjacency while avoiding boosting opponents' cities.**

### Blocking and board control

Since cities cannot be placed adjacent to other cities, each city you place creates an exclusion zone. Use this to cut off opponents from prime positions. Place tiles near ocean clusters to capture adjacency bonuses before opponents can. In 4-5 player games, board space becomes tight, and **border hexes gain strategic value**—placing a city one hex from the map edge lets you build greenery behind it where opponents can't reach.

---

## Reading tempo decides who controls the endgame

### Counting the clock

The game ends when 43 total terraforming steps are completed across all three parameters. At any point, you can count remaining steps: how many temperature increases, oxygen increases, and ocean tiles remain. Divide by the table's approximate terraforming rate per generation (typically 4-8 steps per generation in a 4-player game) to estimate remaining generations.

Average game length varies dramatically by player count:

| Player Count | Typical Generations | Strategic Implication |
|-------------|-------------------|----------------------|
| 2 players | 12-15 | Deep engine building; economy dominates |
| 3 players | 10-13 | Balanced engine/tempo tension |
| 4 players | 8-10 | Faster pace; mid-game pivot earlier |
| 5 players | 5-8 | Shortest games; immediate value dominates |

### Accelerating versus decelerating

**Accelerate** (push terraforming, end the game faster) when you're ahead on TR, when opponents are building slow engines, or when you have fewer unplayed VP cards than opponents. This is the core of the "rush strategy"—Ecoline can convert plant production directly into oxygen raises while simultaneously scoring greenery VP, ending games before engine-builders can deploy their accumulated cards.

**Decelerate** (avoid terraforming, build your engine) when your production outpaces opponents', when you have powerful blue cards generating per-generation value (Pets, Birds, AI Central), or when your hand contains high-VP cards you haven't yet played. The risk is that opponents can force game end by aggressively terraforming despite your preference.

The strongest players monitor this constantly. When you see an opponent stockpiling cards and building a massive engine, consider whether pushing the game to end one generation sooner strands them with unplayed cards worth dozens of points.

---

## Player count transforms the strategic landscape

**Two-player games** last longest (12-15 generations) and reward pure engine efficiency. Board space is abundant, so interaction is minimal. Income disparity is devastating—falling 10-20 MC production behind with no other opponents to balance the gap is often unrecoverable. Ecoline is borderline overpowered with only one opponent's attacks to worry about, and Protected Habitats (preventing resource removal) becomes one of the game's best cards. Card draw engines are extremely powerful since you see far more of the deck.

**Three-player games** are widely considered the most strategically balanced. All corporation tiers remain viable, tile placement becomes meaningfully interactive, and the tension between engine building and tempo is at its peak.

**Four-player games** compress to roughly 10 generations, making the mid-game pivot come earlier. Board space becomes crowded—place cities early to secure prime positions. Time-based VP generators (Pets, Birds, Security Fleet) become critical: the VP differential between players who buy animal cards and those who don't is often game-deciding. Milestones become fiercely competitive with four players racing for three slots.

**Five-player games** can end in as few as 5-8 generations. Engine building has minimal time to compound. Immediate-value cards and corporations dominate. Cards like Pets in an opening hand can score 8+ VP at practically no MC per VP. Board space is extremely tight, and defensive tile placement is essential.

**Drafting** dynamics shift too: in 2-player, you see every card your opponent passes, creating deep information symmetry. In 4-5 player games, hate-drafting becomes less targeted but milestones and awards become more contested.

---

## The twelve mistakes every beginner makes

**Buying VP cards too early.** Fixed VP cards are paid upfront but only score at game end. A 15 MC VP card in Generation 2 could have funded production generating 30+ MC over the remaining game. Economy first, points later.

**Undervaluing production.** New players chase exciting cards while neglecting boring MC production and steel. The player with +5 MC production by Generation 3 will have 35+ more MC to spend over the game than the player who skipped it.

**Holding too many cards.** Each card costs 3 MC to buy. Holding 8-10 cards "for later" means 24-30 MC of frozen capital. Keep 4-6 cards maximum—only cards you can play within 1-2 generations.

**Ignoring milestones.** At 1.6 MC/VP, milestones are seven times more efficient than standard projects. Missing the window because you waited to claim until "next turn" is one of the costliest mistakes in the game.

**Forgetting about awards.** Many beginners never fund awards. Even the second award at 14 MC is excellent value if you're likely to win first place.

**Not converting resources at game end.** Leftover plants and heat at game end are completely wasted. Convert everything. After the final production phase, you still get one last chance to convert plants to greenery—use it.

**Forgetting standard projects exist.** Standard projects are overpriced but always available. They're essential for grabbing temperature track bonuses, placing strategic tiles, and converting MC to VP in the late game.

**Misreading game length.** Playing as though 5 generations remain when only 2 do—or vice versa—leads to catastrophic misallocation. Count remaining terraforming steps every generation.

**Gifting VP through greenery placement.** Placing greenery adjacent to an opponent's city gives them free adjacency VP. Place adjacent to your own cities whenever possible.

**Overvaluing energy.** Energy production is a means to an end (powering blue cards or converting to heat), not an end in itself. The Power Plant standard project is almost never worth 11 MC.

**Not tracking opponents.** Everything except hand cards is public information. Track opponents' production, TR, tile placement, and likely milestone/award positions. Failing to monitor the table means missing critical blocking opportunities.

**Falling in love with a strategy.** The best Terraforming Mars players have no fixed style. They adapt to their corporation, their cards, their opponents, and the board state. **Flexibility is the most important skill after efficiency.**

---

## Advanced strategies for competitive play

### Rush versus engine: reading the meta-decision

The terraforming rush strategy minimizes engine building and maximizes direct terraforming. Use cheap event cards (asteroids, aquifers), plant production for oxygen, and heat production for temperature. End the game in 8-9 generations, stranding opponents with unplayed engines. Ecoline is the strongest rush corporation—plant production directly converts to both oxygen TR and greenery VP without needing cards.

The engine strategy builds massive production, card draw engines (AI Central, Mars University), and per-generation VP generators (Pets, Birds, Physics Complex). It accepts slower terraforming and profits from each additional generation. Credicor and Tharsis Republic excel here.

**The meta-decision**: rush when opponents are building slow engines. Build engine when opponents are rushing (piggyback on their terraforming while accumulating VP). The strongest players read the table mid-game and adjust—there is no universally correct approach.

### Tag synergy architectures

**Building + City** is the most reliable strategy since building is the most common tag type, steel is readily available, and it naturally pursues both the Builder milestone and Mayor milestone. Tharsis Republic and Interplanetary Cinematics are purpose-built for this.

**Space + Jovian** offers the highest VP density per card—33 of 43 space cards provide VP or TR. Saturn Systems converts every Jovian tag (from any player) into MC production. Terraforming Ganymede (1 VP per Jovian tag you own) is one of the game's best VP cards when you stack 5+ Jovian tags. Titanium at 3 MC each (4 MC for Phobolog) subsidizes the expensive card costs.

**Plant + Microbe combos** create powerful ongoing engines. Extreme-Cold Fungus combined with Regolith Eaters generates **1 TR per generation** from microbe accumulation—one of the strongest repeatable combos in the game. Arctic Algae (2 plants per ocean placed) can generate massive plant stockpiles in ocean-heavy games.

**Science** is a gatekeeper tag—having science tags unlocks powerful cards that require 2-3+ science prerequisites. Mars University (draw a card when playing science tags) creates a card-draw engine. The Scientist award specifically rewards science tag accumulation.

### Hate-drafting: the cost of denial

Taking a card to deny an opponent costs you 3 MC (the draft cost) with zero benefit to your own engine. This means hate-drafting is only justified when the denied card would generate **more than 3 MC worth of VP advantage** for your opponent. In practice, deny city-based cards against Tharsis Republic, plant cards against Ecoline, and Jovian cards against Saturn Systems. In 2-player games, hate-drafting is far more impactful since you know exactly who you're denying.

### Point density analysis for the endgame

In the final generation, every remaining MC should be converted to VP as efficiently as possible. The hierarchy of VP efficiency:

- **Milestones**: 1.6 MC/VP (claim if still available)
- **Greenery from plants**: Essentially free VP
- **Best VP cards**: 5-7 MC/VP
- **Awards (1st funded, if winning)**: 1.6 MC/VP
- **Good VP cards**: 7-10 MC/VP
- **Standard project greenery**: ~11.5 MC/VP
- **Standard project asteroid**: 14 MC/VP
- **Aquifer**: 15-18 MC/VP

Plan your final generation precisely: count your MC, list available VP actions ranked by efficiency, and spend from top to bottom. Don't leave MC unspent—even a standard project asteroid at 14 MC/VP is better than unused currency.

### Reading the score in real time

Tracking who's winning during play is notoriously difficult, but competitive players approximate: **sum TR + (cities × estimated adjacency greenery) + greenery count + milestones claimed × 5 + likely award wins × 5 + visible card VP**. In experienced groups, winning scores typically range from **80-120+ points**, with a rough breakdown of TR (35-45), cities and greenery (15-25), milestones and awards (10-15), and card VP (10-20).

---

## How each expansion reshapes the game

**Prelude** is the consensus must-have expansion. It adds 35 prelude cards—each player receives 4, keeps 2, and plays them before Generation 1. These provide production boosts, resources, and TR increases that compress the "boring" early economy-building phase. Games shorten by 2-3 generations. Corporation + prelude synergy becomes a crucial opening decision. Once you play with Prelude, the base game feels slow. Most competitive formats mandate it.

**Colonies** adds colony tiles representing distant moons and asteroids, with trade fleets and escalating resource tracks. It creates a meaningful secondary economy that integrates naturally with engine building—trading at colonies provides steady resource income, and building colonies on locations matching your strategy (titanium from Io, plants from Europa) amplifies your engine. **Poseidon** has the highest competitive win rate of any corporation across all expansions thanks to its free colony and snowballing MC production. Games end somewhat faster with more resources flowing.

**Turmoil** is the expert expansion, adding a political layer with 6 parties, delegates, global events visible 3 generations in advance, and a per-generation TR tax. It rewards forward planning and adds significant player interaction through political maneuvering. The complexity increase is substantial—many tournaments allow players to veto it. **Terralabs Research** (1 MC per card instead of 3) is game-warpingly powerful in skilled hands.

**Venus Next** adds a fourth terraforming track (Venus) that does *not* need to be maxed for the game to end—making it optional VP. It introduces 49 new cards and the World Government rule (one free parameter bump per generation for pacing). The main criticism is deck dilution—more cards means less chance of finding the specific cards your engine needs. **Manutech** (gaining resources equal to production increases) is considered one of the strongest corporations across all expansions. Venus is the lowest-priority expansion in competitive rankings.

---

## Conclusion: the principles that win games

Terraforming Mars rewards compound thinking—small efficiency advantages in early generations cascade into decisive leads by game end. The players who win consistently don't memorize card lists or follow rigid strategies. They internalize a handful of principles and apply them flexibly.

**Build economy before buying points.** Every MC of production gained early compounds across remaining generations. **Claim milestones the moment you can.** Nothing in the game matches 1.6 MC/VP efficiency. **Count remaining terraforming steps every generation** to know when to pivot from engine to scoring. **Evaluate every card against the 14 MC/VP standard project baseline**—anything worse than an Asteroid isn't worth playing. **Adapt to what the game gives you.** The strongest players have no style—only efficiency and flexibility.

The final insight: Terraforming Mars is not a solitaire optimization puzzle. It's a race with shared resources and contested board space. The player who best reads the table—knowing when to accelerate the game against engine-builders, when to grab contested milestones, when to hate-draft a critical card, and when to convert their remaining resources into the last few VP—will win far more often than the player with the theoretically optimal engine.
