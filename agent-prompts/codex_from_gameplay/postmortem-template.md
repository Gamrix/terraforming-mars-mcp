# Terraforming Mars Postmortem
## Game: `<url>`
## Date: `<YYYY-MM-DD>`

## 1) Outcome Snapshot

- Final result: **<Opponent> <opponent_score> - <self_score> <Self>**
- Ended in **Generation <N>**
- Board: `<tharsis|hellas|elysium|other>`
- Initial strategy call (Gen 2-3): `<hard close|hybrid leaning close|outscale>`
- Did we pivot? `<yes/no>`
- Pivot generation: `<N or n/a>`
- Was the macro call actually specific enough to constrain play? `<yes/no>`

## 2) Score Decomposition

| Category | Self | Opponent | Delta (Opp - Self) |
|---|---:|---:|---:|
| TR |  |  |  |
| Milestones |  |  |  |
| Awards |  |  |  |
| Greenery |  |  |  |
| City |  |  |  |
| Card VP |  |  |  |
| **Total** |  |  |  |

## 2A) Forecast Accuracy

Record the best in-game forecast you had by Gen 6 to 8.

| Category | Self Forecast | Self Actual | Opp Forecast | Opp Actual |
|---|---:|---:|---:|---:|
| TR |  |  |  |  |
| Awards |  |  |  |  |
| Greenery |  |  |  |  |
| City |  |  |  |  |
| Card VP |  |  |  |  |

- What did the forecast miss?
- Did we think we were ahead because of TR while actually behind on VP ceiling?

## 3) Timeline by Generation

- Gen 1:
- Gen 2:
- Gen 3:
- Gen 4:
- Gen 5:
- Gen 6:
- Gen 7:
- Gen 8:
- Gen 9:
- Gen 10:
- Gen 11:
- Gen 12:

## 4) Strategy Review

### Self
- Core plan:
- Why this macro plan was chosen:
- What worked:
- What failed:
- Did we drift into an under-defined hybrid line?:

### Opponent
- Core plan:
- How they converted into VP:
- What we failed to deny:
- Which explicit engine alarms should have fired:

## 5) Critical Turning Points

| Gen | Decision | Why it mattered | VP impact estimate |
|---:|---|---|---:|
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

## 6) Counterfactuals

| Alternative line | Realism | Estimated swing |
|---|---|---:|
|  | low/med/high |  |
|  | low/med/high |  |
|  | low/med/high |  |

## 7) Mistake Taxonomy Tags

Use tags from `agent-prompts/codex_from_gameplay/decision-taxonomy.md`.

- `tag_1`
- `tag_2`
- `tag_3`

## 8) Tool Mismatches

| Tool | Expected | Actual | Root cause | Mitigation |
|---|---|---|---|---|
|  |  |  |  |  |

## 9) Rule Updates (Must Be Actionable)

1. If `<condition>`, then `<action>`.
2. If `<condition>`, then `<action>`.
3. If `<condition>`, then `<action>`.

## 10) Active Hypotheses Check

List 1 to 3 hypotheses that were being tested in this game.

| Hypothesis | Result in this game | Status |
|---|---|---|
|  | strengthened / weakened / unresolved |  |
|  | strengthened / weakened / unresolved |  |
|  | strengthened / weakened / unresolved |  |

## 11) Endgame Conversion Review

- Did we write a liquidation plan by Gen 10+?:
- Did we check whether actions continued after terraforming completed?:
- Which resources were stranded at pass or game end?:
- Best missed `MC -> VP` conversion:
- Best missed board placement:

## 12) Next-Game Checklist

- [ ] Strategy call logged by Gen 3.
- [ ] Macro call is specific enough to exclude strategic drift.
- [ ] Milestone contest plan explicit by Gen 4.
- [ ] Award funding lock confidence checked.
- [ ] Card VP race estimate written by Gen 6.
- [ ] Gen 8 score forecast revised after opponent engine update.
- [ ] Endgame conversion plan written at start of final generation.
- [ ] After Mars is terraformed, live prompt checked before passing.
