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
- `waiting_for.input_type` tells you which tool to call.
- After every write/action tool call, the MCP server auto-waits for your next turn when your action ends your turn.
- When opponents act between your turns, responses include `opponent_actions_between_turns` (rendered from new game log entries); post-turn state is rebuilt after waiting.
- For compound prompts:
- `or`: choose one branch and provide a nested response for that branch.
- `and`: provide one response for each branch.
- Treat action-tool responses as the primary state source after each move (`choose_or_option`, `select_cards`, `select_space`, `pay_for_project_card`, etc.). Call `get_game_state` only for explicit inspection, planning context, or a fresh full snapshot — not as the default follow-up after every action.

### Batching Multiple Actions

Use `submit_multi_actions` to send multiple actions in one call. Pass a list of raw `InputResponse` objects (as the `actions` argument) in the order the server will prompt for them. The server submits each one sequentially, using the next element to answer whatever `waitingFor` the previous action produced.
Use this when you know the sequence of actions ahead of time, and it can't be influenced by your actions having random results. (e.g., play a card → select space → second action). The response includes `actions_executed` showing how many of the provided actions were actually executed.

#### Example

play a card needing space selection, then pass:

```json
[
  {"type": "or", "index": 0, "response": {"type": "projectCard", "card": "Noctis City", "payment": {"megaCredits": 20}}},
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
| `submit_and_options` | `and` | Submits responses for all required sub-prompts. | Multi-part prompt |
| `confirm_option` | `option` | Click/confirm style action with no extra data. | Pass, convert resources, trigger optional action |
| `select_amount` | `amount` | Chooses a numeric amount. | Spend/remove/select X |
| `select_cards` | `card` | Picks one or more card names. | Research cards, standard project choice, blue-card action selection, sell patents |
| `select_player` | `player` | Chooses a player color. | Target player effects |
| `select_space` | `space` | Chooses a board hex by `spaceId`. | Tile placement after cards/SPs |
| `select_party` | `party` | Chooses a Turmoil party by name. | Send delegate to party |
| `select_colony` | `colony` | Chooses a colony name. | Colony-related effects |
| `pay_for_action` | `payment` | Pays costs for a generic payment prompt. | Non-card payment step |
| `pay_for_project_card` | `projectCard` | Plays a specific project card with payment object. | “Play project card” branch |
| `select_initial_cards` | `initialCards` | Submits corp/prelude/(optional CEO)/project selections in server option order. | Game setup |
| `select_production_to_lose` | `productionToLose` | Chooses which production units to reduce. | Production-loss effects |
| `select_resources` | `resource` / `resources` | Uses one units payload for both single-resource choice and multi-resource allocation prompts. | Resource-type choice / multi-resource distribution |
| `submit_multi_actions` | *(sequence)* | Submits multiple actions in one call. | Any `or` prompt |

## Important Action Details

- `projectCard`:
- Requires `card` plus a `payment` object. Only include the resources you are actually spending; omitted fields default to 0.
- Example: `{"type":"projectCard","card":"Imported Nitrogen","payment":{"megaCredits":23}}`

- `space`:
- Requires a legal `spaceId` from `waiting_for.spaces`.
- Used after effects like placing oceans/greenery/cities/special tiles.
- Example: `{"type":"space","spaceId":"04"}`

- `card`:
- Respect `waiting_for.card_selection.min` and `max`.
- If `min` is 0, sending an empty list is legal only when the specific prompt allows skipping.

- `or`:
- Nested response must match the selected branch's expected type (e.g. a `projectCard` branch requires a `projectCard` payload, not `{"type":"option"}`).
- Raw `OrOptionsResponse` shape is strict: `{"type":"or","index":<number>,"response":<InputResponse>}`. Keys must be exactly `type`, `index`, `response` (extra keys fail validation).
- If the selected branch is itself another `or` (e.g. milestone/award sub-menu), the nested payload must also be an `or` response, not `option`.

- Milestones and awards:
- Milestone claim and award funding are selected as branches of an `or` prompt. Find the matching option title in `waiting_for.options`, then call `choose_or_option` with that index and nested `{"type":"option"}`.
- If the server then returns `input_type: payment`, finish with `pay_for_action(...)`.

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

- Raw entity that `select_initial_cards` constructs:
```json
{
  "type": "initialCards",
  "responses": [
    { "type": "card", "cards": ["Thorgate"] },
    { "type": "card", "cards": ["Martian Industries", "Loan"] },
    { "type": "card", "cards": ["Noctis City", "Mining Area"] }
  ]
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

`get_game_state` returns:
- current generation/phase/global parameters,
- your resources and production,
- opponent summaries,
- board occupancy summary only during end-of-generation phases (`production`, `solar`, `intergeneration`, `end`) unless `include_board_state=true`,
- normalized `waiting_for` details (cards/options/spaces/etc.),
- card-rich prompt details for selectable cards (tags, ongoing effects/actions, play requirements, cost, and on-play effect text),
- `opponent_new_cards` with newly observed opponent-played cards and their relevant card details,
- suggested tool names for the current input type.

### `include_full_model`

`get_game_state(include_full_model=true)` includes `raw_player_model`, which is the full unmodified `/api/player` payload for your player id. It includes:
- `game`: full `GameModel` (global parameters, phases, milestones/awards, colonies/turmoil/pathfinders/moon data, and full `spaces` board array),
- `players`: public model for each player (resources, production, tableau/played cards, etc.),
- `thisPlayer`: your full public player model,
- `waitingFor`: the raw current input prompt model (if any),
- plus player-view fields such as hand and draft/dealt card groups.
