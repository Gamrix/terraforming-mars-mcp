# Bug Log

## 2026-02-14

### `choose_or_option` project card branch requires explicit payment payload
- Context: During an `or` prompt (`Take your first action`), selecting option `Play project card` with nested `{"type":"projectCard","card":"Research Outpost"}` failed.
- Error: `HTTP 400 POST /player/input: Not a valid SelectProjectCardToPlayResponse`
- Repro:
  1. Wait for `input_type: "or"` where one option has `input_type: "projectCard"`.
  2. Call `choose_or_option` with `option_index` set to that option and `sub_response_json` containing only `type` and `card`.
  3. Observe 400 validation error.
- Workaround: Include a full `payment` object in `sub_response_json` (all numeric fields explicitly present).
- Notes: This is easy to hit because `pay_for_project_card` auto-normalizes payment, but `choose_or_option` does not.

### Final model marks multiplayer game as solo win
- Context: End-game `get_game_state(include_full_model=true)` payload in a 2-player game (`Codex` vs `John`).
- Error: `raw_player_model.game.isSoloModeWin` is `true` even though multiple players are present and standard multiplayer scoring is shown.
- Repro:
  1. Play a normal 2-player game to completion.
  2. Call `get_game_state` with `include_full_model=true`.
  3. Inspect `raw_player_model.game.isSoloModeWin`.
- Expected: `isSoloModeWin` should be `false` (or omitted) for multiplayer games.

### `Earth Catapult` cost reduction not applied during payment validation
- Context: `Earth Catapult` is in tableau with effect text `When you play a card, you pay 2 M€ less for it.`
- Error: Paying discounted cost is rejected as insufficient.
- Repro:
  1. Ensure `Earth Catapult` is played.
  2. Attempt to play a project card (for example `Soil Factory`, printed cost 7) via `choose_or_option`/`projectCard`.
  3. Submit payment reduced by 2 M€ (for example `megaCredits: 5`).
  4. Observe `HTTP 400 POST /player/input: Did not spend enough to pay for card`.
- Notes: Full printed cost is accepted. This suggests effective-cost modifiers are not being applied in validation for this flow.

### `Birds` appears playable but `projectCard` rejects with unknown card name
- Context: End-game action phase (`game.phase = "action"`, `terraforming.isTerraformed = true`) where `Play project card` UI/tool option listed `Birds` as available.
- Error: Submitting `Birds` through `choose_or_option` -> nested `projectCard` returned `HTTP 400 POST /player/input: Unknown card name Birds`.
- Repro:
  1. Reach action phase after terraforming is complete, with `Birds` in hand.
  2. Confirm `waiting_for.options[*].detail.cards` includes `Birds` under `Play project card`.
  3. Submit `choose_or_option` for that project-card option with nested `{"type":"projectCard","card":"Birds","payment":{...}}`.
  4. Observe unknown-card-name validation failure.
- Expected: If `Birds` is listed as playable, server should accept the card name and proceed to any follow-up prompts.
- Notes: In the same state, `Mineral Deposit` was accepted from that same `Play project card` branch.

## Suggestions

### Expose axial-neighbor-friendly board representation for agents
- Suggestion: Add an agent-friendly board view that uses an axial/cube hex model, or explicitly provides `neighbors` for each space in API responses.
- Why: Current row-shifted `(x,y)` coordinates are valid but easy for agents to misinterpret, causing distance/adjacency mistakes in city/greenery planning.
- Possible implementation options:
  1. Include canonical axial coordinates per space in `get_mars_board_state`.
  2. Include precomputed `adjacent_space_ids` per space.
  3. Offer a dedicated `get_board_graph` endpoint returning nodes + edges.
