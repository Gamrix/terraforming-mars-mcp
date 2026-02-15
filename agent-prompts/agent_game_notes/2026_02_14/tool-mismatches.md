# Tool Mismatches / Unexpected Behavior (Game: 2026-02-14)

## 1) `choose_or_option` index-only failed on `projectCard` branch
When it happened:
- Generation 6, action prompt where selected option `Play project card`.
Payload used:
```json
{"option_index":"1"}
```
Observed result:
- `HTTP 400 POST /player/input: Not a valid SelectProjectCardToPlayResponse`
Expected:
- I expected default nested `{"type":"option"}` to work, but this branch required `projectCard` payload.
Resolution:
- Retried with nested `projectCard` + full payment object; succeeded.

## 2) False-negative timeout on action tools (request likely succeeded server-side)
When it happened:
- Earlier turns in this same game.
Tools affected:
- `select_cards`
- `choose_or_option`
Observed result:
- Tool call timed out, but subsequent `get_game_state` showed action had applied.
Impact:
- Risk of duplicate submits if immediately retried without state check.
Resolution:
- After timeout, verify with `get_game_state` before replaying action.

## 3) Intermittent timeout on read tool
When it happened:
- Earlier turn in this same game.
Tool affected:
- `get_game_state`
Observed result:
- Transient timeout with no persistent session issue.
Resolution:
- Retry call.

## 4) Card listed in hand but rejected as unknown in selected action branch
When it happened:
- Earlier turn in this same game.
Tool/path:
- `choose_or_option` with nested `projectCard`.
Observed result:
- `HTTP 400 ... Unknown card name AI Central` when trying to play it.
Cause:
- Card existed in hand/sell list but was not in current `Play project card` option's `detail.cards` (not legal at that moment).
Resolution:
- Only submit card names listed in the active option's playable-card subset.

## 5) Nested `projectCard` payment object cannot be partial
When it happened:
- Generation 9, action prompt `Take your first action` -> `Play project card`.
Payload used:
```json
{
  "option_index":"0",
  "sub_response_json":"{\"type\":\"projectCard\",\"card\":\"Tropical Resort\",\"payment\":{\"steel\":5,\"megaCredits\":1}}"
}
```
Observed result:
- `HTTP 400 POST /player/input: payment is not a valid type`
Expected:
- I expected unspecified payment fields to default to 0.
Resolution:
- Submit a full payment object with all spendable keys present (unused keys set to `0`).

## 6) Nested `projectCard` without payment is rejected immediately
When it happened:
- Generation 9, same action window as case 5.
Payload used:
```json
{
  "option_index":"0",
  "sub_response_json":"{\"type\":\"projectCard\",\"card\":\"Tropical Resort\"}"
}
```
Observed result:
- `HTTP 400 POST /player/input: Not a valid SelectProjectCardToPlayResponse`
Expected:
- I expected a follow-up payment prompt.
Resolution:
- Include `payment` in the nested response; for this backend shape, `projectCard` selection and payment are validated together.

## 7) `get_game_state` compact view does not expose final winner/VP total
When it happened:
- End phase of this game (Generation 11 complete).
Tool affected:
- `get_game_state` (default summary mode).
Observed result:
- Summary showed phase/resources/awards, but not explicit final totals or winner.
Expected:
- I expected direct final score output in the compact response.
Resolution:
- Call `get_game_state` with `include_full_model: true` and read `raw_player_model.players[*].victoryPointsBreakdown.total`.
