## Terraforming Mars MCP Agent Basics

You are a game playing expert and you want to win at Terraforming Mars.
Make sure to continue playing until the current game is over.

## Game Guide

A game guide written by a deep researching AI Agent is available at `GUIDE.md`.
It has critical information on how the game of Terraforming Mars works and
core strategies for playing well. Read through it before playing a game.

## Tharsis Board

- Board square information is in `tharsis_board_shape.md`.
- The board coordinate system is a unique system.
- Adjacent coordinate rule: candidates are left/right `(x-1,y),(x+1,y)` plus four diagonals:
  - for `y<4` use `(x-1,y-1),(x,y-1),(x-1,y+1),(x,y+1)`,
  - for `y=4` use `(x-1,y-1),(x,y-1),(x,y+1),(x+1,y+1)`,
  - for `y>4` use `(x,y-1),(x+1,y-1),(x,y+1),(x+1,y+1)`.

## Core Tools

- `configure_session`: set server URL and player id.
- `get_game_state`: compact agent view of game status and legal current action context.
- `get_opponents_played_cards`: all cards currently in each opponent's tableau.
- `get_my_played_cards`: all cards currently in your tableau.
- `get_my_hand_cards`: all cards currently in your hand.
- `get_mars_board_state`: detailed Mars board state (occupied spaces by default).
- `wait_for_turn`: manually wait until your turn (fixed 2-hour timeout, fixed poll interval).
- `submit_raw_entity`: submit any raw `InputResponse` JSON object.

## How Actions Work

- The server always exposes one current prompt at `get_game_state().waiting_for`.
- `waiting_for.input_type` tells you which tool to call.
- After every write/action tool call, the MCP server now auto-waits for your next turn when your action ends your turn.
- Auto-wait uses a fixed timeout of 2 hours and a fixed poll interval of 2 seconds.
- When opponents act between your turns, responses include `opponent_actions_between_turns` (rendered from new game log entries).
- For compound prompts:
- `or`: choose one branch and provide a nested response for that branch.
- `and`: provide one response for each branch.
- You can always bypass helpers and send a raw response with `submit_raw_entity`.
- Every write tool returns state; post-turn state is rebuilt after waiting when opponent actions were detected between turns.

## Action Reference

| MCP tool | Response type | What it does | Typical prompt |
|---|---|---|---|
| `choose_or_option` | `or` | Selects one option index and submits nested response. | Main action menu / mixed choice prompt |
| `submit_and_options` | `and` | Submits responses for all required sub-prompts. | Multi-part prompt |
| `confirm_option` | `option` | Click/confirm style action with no extra data. | Pass, convert resources, trigger optional action |
| `select_amount` | `amount` | Chooses a numeric amount. | Spend/remove/select X |
| `select_cards` | `card` | Picks one or more card names. | Research cards, standard project choice, blue-card action selection, sell patents |
| `select_player` | `player` | Chooses a player color. | Target player effects |
| `select_delegate_target` | `delegate` | Chooses delegate target (`color` or `NEUTRAL`). | Turmoil delegate placement |
| `select_space` | `space` | Chooses a board hex by `spaceId`. | Tile placement after cards/SPs |
| `select_party` | `party` | Chooses a Turmoil party by name. | Send delegate to party |
| `select_colony` | `colony` | Chooses a colony name. | Colony-related effects |
| `pay_for_action` | `payment` | Pays costs for a generic payment prompt. | Non-card payment step |
| `pay_for_project_card` | `projectCard` | Plays a specific project card with payment object. | “Play project card” branch |
| `select_initial_cards` | `initialCards` | Submits corp/prelude/(optional CEO)/project selections in server option order. | Game setup |
| `select_production_to_lose` | `productionToLose` | Chooses which production units to reduce. | Production-loss effects |
| `shift_ares_global_parameters` | `aresGlobalParameters` | Sends Ares hazard threshold deltas. | Ares hazard adjustment prompt |
| `select_global_event` | `globalEvent` | Chooses one global event. | Turmoil event selection |
| `select_policy` | `policy` | Chooses a policy id. | Turmoil policy prompt |
| `select_resource` | `resource` | Chooses one resource key. | Single resource-type choice |
| `select_resources` | `resources` | Sends resource-unit allocation map. | Multi-resource distribution |
| `select_claimed_underground_tokens` | `claimedUndergroundToken` | Chooses underground token indexes. | Underworld token prompt |

## Important Action Details

- `projectCard`:
- Requires `card` plus full `payment` object.
- The payment object includes all spendable fields, even when most are zero.
- Example: `{"type":"projectCard","card":"Imported Nitrogen","payment":{"megaCredits":23,...}}`

- `space`:
- Requires a legal `spaceId` from `waiting_for.spaces`.
- Used after effects like placing oceans/greenery/cities/special tiles.
- Example: `{"type":"space","spaceId":"04"}`

- `card`:
- Respect `waiting_for.card_selection.min` and `max`.
- If `min` is 0, sending an empty list is legal only when the specific prompt allows skipping.

- `or`:
- Nested response must match the selected branch’s expected type.
- If branch 0 is `projectCard`, sending nested `{"type":"option"}` will fail validation.

- Milestones and awards:
- Milestone claim and award funding are selected as branches of an `or` prompt.
- Find the matching option title in `waiting_for.options`, then call `choose_or_option` with that index and nested `{"type":"option"}`.
- If the server then returns `input_type: payment`, finish with `pay_for_action(...)`.

- `initialCards`:
- The helper reads the server’s current setup option order and maps your corp/prelude/CEO/project picks into `responses`.
- This avoids hard-coding option positions.

## Game State for Agents

`get_game_state` returns:
- current generation/phase/global parameters,
- your resources and production,
- opponent summaries,
- board occupancy summary only during end-of-generation phases (`production`, `solar`, `intergeneration`, `end`) unless `include_board_state=true`,
- normalized `waiting_for` details (cards/options/spaces/etc.),
- card-rich prompt details for selectable cards (tags, ongoing effects/actions, play requirements, cost, and on-play effect text),
- `opponent_card_events` with newly observed opponent-played cards and their relevant card details,
- suggested tool names for the current input type.

### `include_full_model`

`get_game_state(include_full_model=true)` includes `raw_player_model`, which is the full unmodified `/api/player` payload for your player id. It includes:
- `game`: full `GameModel` (global parameters, phases, milestones/awards, colonies/turmoil/pathfinders/moon data, and full `spaces` board array),
- `players`: public model for each player (resources, production, tableau/played cards, etc.),
- `thisPlayer`: your full public player model,
- `waitingFor`: the raw current input prompt model (if any),
- plus player-view fields such as hand and draft/dealt card groups.
