# Terraforming Mars Postmortem
## Game: `http://localhost:8080/player?id=p1d77654ac98a`
## Date: 2026-02-15

## 1) Outcome Snapshot

- Final result: **John (Blue) 104 - Codex (Red) 72**
- Ended in **Generation 10**
- Global completion order:
1. Oceans maxed first.
2. Temperature maxed second.
3. Oxygen finished last.

This was a fast game, but not fast enough to suppress Blue's late VP engine.

## 2) Score Decomposition

### Codex (72)
- TR: 55
- Milestones: 5
- Awards: 5
- Greenery: 8
- City: 0
- Card VP: -1

### John (104)
- TR: 31
- Milestones: 10
- Awards: 10
- Greenery: 11
- City: 13
- Card VP: 29

### Delta Drivers (John minus Codex)
- TR: **-24** (Codex advantage)
- Milestones: **+5**
- Awards: **+5**
- Greenery: **+3**
- City: **+13**
- Card VP: **+30**
- Net: **+32** for John

Interpretation:
- We massively won terraform tempo.
- John massively won VP conversion categories.
- The biggest deciding lane was **Card VP + City VP**.

## 3) Terraform Tempo Timeline

From `globalsPerGeneration`:

- Gen 1: Temp -24, O2 0, Oceans 2
- Gen 2: Temp -22, O2 0, Oceans 2
- Gen 3: Temp -14, O2 0, Oceans 3
- Gen 4: Temp -14, O2 1, Oceans 4
- Gen 5: Temp -14, O2 4, Oceans 5
- Gen 6: Temp -8, O2 5, Oceans 5
- Gen 7: Temp -8, O2 6, Oceans 6
- Gen 8: Temp 0, O2 8, Oceans 9
- Gen 9: Temp 8, O2 11, Oceans 9
- Gen 10: Temp 8, O2 14, Oceans 9 (end)

What this means:
- Rush worked on temperature and oceans.
- Oxygen became the true closing bottleneck.
- Blue's plant engine still had enough time to cash oxygen/greenery VP.

## 4) What John Did Better

1. Built overlapping VP lanes early.
- Animals + science + plant package scaled together.
- Blue did not rely on TR to win.

2. Converted economy into scoring, not just production.
- Late actions stayed point-focused.
- Card VP stack reached 29, which is very high in a 2p Gen 10 end.

3. Won contested public points.
- Claimed `Gardener` and `Builder`.
- Funded and won `Scientist`.
- Won `Thermalist` even though we funded it.

4. Built city presence that paid immediately.
- 13 city VP from adjacency.
- We had 0 city VP.

## 5) What We Did Well

1. Strong rush shell and early map control.
- Preludes and early events gave fast TR acceleration.
- We controlled oceans and temperature pace.

2. Secured `Terraformer` milestone and `Miner` award win.
- `Miner` was a correctly funded lock.
- Steel economy and Mining Guild synergy worked.

3. Correct macro read that long game favored Blue.
- Rush decision itself was reasonable.

## 6) Where Our Plan Broke

### A) Rush was not paired with VP floor

We drove TR but underbuilt score floor categories:
- No city VP.
- Weak card VP.
- Only one milestone.

Rush in 2p still needs a minimum endgame floor if the opponent can score 25+ from cards.

### B) Award funding discipline failed once

We funded `Thermalist` and lost it.

Consequences:
- We spent 20 MC.
- Blue gained 5 VP from an award we opened.
- We gained 0 from that award.

This was a high-leverage swing against us.

### C) Endgame conversion window was underused

Late game, we had one action windows where:
- We could still run standard projects.
- We had enough MC for city/greenery choices.

We passed instead of forcing extra board VP.

### D) Resource mix stranded value

We ended with very large leftover steel.

Steel is not VP by itself.
Without late building cards or conversion outlets, this became dead value.

### E) Final hand liquidation cost points

We sold `Bribed Committee` in endgame.

`Bribed Committee` is +2 TR on play.
In a finished-terraformed endgame, that is pure score and should usually be played if affordable.

## 7) Counterfactuals (How Much Could Be Recovered?)

These are rough realistic swings:

1. Do not fund losing `Thermalist`: about **+5 swing**.
2. Play `Bribed Committee` instead of selling: about **+2**.
3. Build one high-adjacency city in final action cycle: about **+4 to +6**.

Best realistic recovery from late tactical fixes: about **+11 to +13**.

Even with perfect late tactics, we still trail by around 19-21.

Conclusion:
- Loss was not one blunder.
- Loss was a structural scoring gap established by midgame.

## 8) Rush Decision Review (Was Rush Wrong?)

Short answer: **Rush choice was right, execution was incomplete.**

Why rush was right:
- Blue had superior engine ceiling.
- If game extends to Gen 11-12, Blue likely gains even more card/animal/city VP.

Why execution was incomplete:
- Rush line did not include a hard anti-engine layer.
- We did not sufficiently deny Blue's late VP conversion lanes.
- We did not transition from pure terraforming to mixed closure + VP floor early enough.

## 9) Practical Heuristics for Next Match

1. Use an award lock rule:
- Do not fund unless projected win probability is high and stable.
- Treat funding as a contract, not tempo.

2. Add a rush transition trigger:
- At first maxed global (often oceans or temp), switch from pure TR to:
1. one secure VP lane (city or card VP),
2. one denial lane (award/milestone pressure),
3. one closure lane (remaining global).

3. Protect endgame action value:
- Never sell a cheap direct-VP/TR card in final generation unless it cannot be played.

4. Convert MC before final pass if actions remain:
- In endgame action phase, unused MC is almost always lower value than board VP.

5. Watch oxygen race explicitly:
- In plant-heavy opponent games, oxygen is usually the final gate.
- Build closure plans around oxygen math, not temperature math.

## 10) Concrete Playbook Update

For Mining Guild rush vs science/plant engine:

1. Early game:
- Prioritize temp/ocean tempo as before.
- Keep at least one path to city adjacency.

2. Mid game:
- Fund only awards with durable lock (`Miner` often yes).
- Avoid marginal awards that opponent can flip (`Thermalist` often volatile).

3. Late game:
- If terraforming is 1-2 steps from end, switch every action to immediate VP.
- Prefer city or guaranteed TR cards over speculative production.

## 11) Final Diagnosis

John won because Blue converted economic engine into scoring categories that survive rush pressure:
- high card VP,
- strong city adjacency,
- milestone/award capture.

We won pace, but Blue won value realization.

In this game state, tempo alone was not enough.
