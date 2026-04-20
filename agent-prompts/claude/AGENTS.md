## Terraforming Mars MCP Agent Basics

You are a game playing expert and you want to win at Terraforming Mars.
Make sure to continue playing until the current game is over.

## Game Guide

A game guide written by a deep researching AI Agent is available at `GUIDE.md`.
It has critical information on how the game of Terraforming Mars works and
core strategies for playing well. Read through it before playing a game.

## Tharsis Board

- Board square information is in `tharsis-board-shape.md`.
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
- `wait_for_turn`: manually wait until your turn when needed.
- `submit_raw_entity`: submit any raw `InputResponse` JSON object.

## How Actions Work

- The server always exposes one current prompt at `get_game_state().waiting_for`.
- `waiting_for.input_type` tells you which tools are currently valid.
- After every write/action tool call, the MCP server auto-waits for your next turn when your action ends your turn.
- Treat action-tool responses as the primary state source after each move (`choose_or_option`, `select_cards`, `select_space`, `pay_for_project_card`, etc.). Call `get_game_state` only for explicit inspection, planning context, or a fresh full snapshot — not as the default follow-up after every action.

### Submitting Multiple Actions

Use `submit_multi_actions` to send multiple actions in one call. Pass a list of raw `InputResponse` objects (as the `actions` argument) in the order the server will prompt for them.
The server submits them **one at a time, in the order given**. Each response is the answer to whatever `waitingFor` the previous submission produced.
Dependent actions are fine: each step uses the game state produced by the previous step, exactly as if you had called the tools sequentially yourself.
Always use this whenever you know the sequence of responses ahead of time, including multi-step flows like play a card → select space → follow-up action.
The response `actions_executed` is the count of actions that were actually executed.

#### Example

play a card needing space selection, then pass:

```json
[
  {"type": "projectCard", "card": "Noctis City", "payment": {"megaCredits": 20}},
  {"type": "space", "spaceId": "35"},
  {"type": "or", "index": 5, "response": {"type": "option"}}
]
```

#### Times to not use `submit_multi_actions`

- An action other than the last one causes some kind of card draw or viewing cards from outside of your hand.


## Action Reference

| MCP tool | Response type | What it does | Typical prompt |
|---|---|---|---|
| `choose_or_option` | `or` | Selects one option index and submits nested response. | Main action menu / mixed choice prompt |
| `submit_and_options` | `and` | Submits responses for all required sub-prompts. | Multi-part prompt (Rare) |
| `confirm_option` | `option` | Click/confirm style action with no extra data. | convert resources, trigger optional action |
| `select_amount` | `amount` | Chooses a numeric amount. | Spend/remove/select X |
| `select_cards` | `card` | Picks one or more card names. | Research cards, standard project choice, blue-card action selection, sell patents |
| `select_player` | `player` | Chooses a player color. | Target player effects |
| `select_space` | `space` | Chooses a board hex by `spaceId`. | Tile placement after cards/SPs |
| `select_party` | `party` | Chooses a Turmoil party by name. | Send delegate to party |
| `select_colony` | `colony` | Chooses a planet to place colony. | Colony-related effects |
| `pay_for_action` | `payment` | Pays costs for a generic payment prompt. | Non-card payment step |
| `pay_for_project_card` | `projectCard` | Plays a specific project card with payment object. | “Play project card” branch |
| `select_initial_cards` | `initialCards` | Submits corp/prelude/(optional CEO)/project selections in server option order. | Game setup |
| `select_production_to_lose` | `productionToLose` | Chooses which production units to reduce. | Production-loss effects |
| `select_resources` | `resource` / `resources` |  payload for both single-resource choice and multi-resource allocation prompts. | Resource-type distribution |
| `pass_turn` | *(shortcut)* | Submits the "Pass for this generation" / "End Turn" option in the current `or` prompt. | End-of-turn or end-of-generation `or` prompt |
| `submit_multi_actions` | *(sequence)* | Submits multiple actions in one call. | Any prompt |

## Important Action Details

- `projectCard`:
- Requires `card` plus a `payment` object. Only include the resources you are actually spending; omitted fields default to 0.
- Example: `{"type":"projectCard","card":"Imported Nitrogen","payment":{"megaCredits":23}}`

- `space`:
- Requires a legal `spaceId` from `waiting_for.spaces`.
- Used after effects like placing oceans/greenery/cities/special tiles.
- Example: `{"type":"space","spaceId":"04"}`

- `or`:
- Nested response must match the selected branch's expected type (e.g. a `projectCard` branch requires a `projectCard` payload, not `{"type":"option"}`).
- If the selected branch is itself another `or` (e.g. milestone/award sub-menu), the nested payload must also be an `or` response, not `option`.

- `initialCards`:
- The helper reads the server’s current setup option order and maps your corp/prelude/CEO/project picks into `responses`.
- This avoids hard-coding option positions.

## Payload Formats (Copy/Paste)

Use these exact shapes when you are unsure about setup or nested prompts.

- `select_initial_cards` tool payload:
- Pass an object with snake_case keys; list-typed fields must be arrays (not comma-separated strings).
- Minimal example:
```json
{
  "corporation_card": "Thorgate",
  "prelude_cards": ["Martian Industries", "Loan"],
  "project_cards": ["Noctis City", "Mining Area"],
  "ceo_cards": []
}
```

- `choose_or_option` with nested `space` response:
```json
{
  "option_index": 1,
  "sub_response": {"type": "space", "spaceId": "04"}
}
```

- `choose_or_option` with nested `projectCard` response:
```json
{
  "option_index": 0,
  "sub_response": {"type": "projectCard", "card": "Noctis City", "payment": {"megaCredits": 18}}
}
```

- `choose_or_option` for nested `or` (example: claim Mayor milestone — outer `or` branch contains a second `or` with milestone choices):
```json
{
  "option_index": 0,
  "sub_response": {"type": "or", "index": 0, "response": {"type": "option"}}
}
```

- `select_cards` with empty list (prompt with `amount_range.min=0` and `max=0`, e.g. Inventors' Guild "cannot afford any cards"):
```json
{
  "card_names": []
}
```

## Game State for Agents

### `get_game_state` returns:
- current generation/phase/global parameters,
- your resources and production,
- opponent summaries,
- board occupancy summary only during end-of-generation phases (`production`, `solar`, `intergeneration`, `end`) unless `include_board_state=true`,
- normalized `waiting_for` details (cards/options/spaces/etc.),
- card-rich prompt details for selectable cards (tags, ongoing effects/actions, play requirements, cost, and on-play effect text),
- `opponent_new_cards` with newly observed opponent-played cards and their relevant card details,
- suggested tool names for the current input type.

### `include_full_model`

`get_game_state(include_full_model=true)` includes all data available to the player-view API, including:

- `game`: full `GameModel` (global parameters, phases, milestones/awards, colonies/turmoil/pathfinders/moon data),
- `players`: public model for each player (resources, production, tableau/played cards, etc.),
- `thisPlayer`: your full private player model,
- `waitingFor`: the raw current input prompt model (if any),
- plus player-view fields such as hand and draft/dealt card groups.
