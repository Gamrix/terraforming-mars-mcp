# MCP Bugs Found During Game 10 (2026-09-25)

## 1. Payment key casing mismatch (`megaCredits` vs `megacredits`)
- The updated tm-oss-server `isPayment` requires **every** key in `SPENDABLE_RESOURCES`, and uses lowercase `megacredits`.
- Before the MCP restart: `pay_for_project_card` and `submit_multi_actions` with `{"megaCredits": N}` failed with
  `HTTP 400 ... payment is not a valid type`. Workaround was `submit_raw_entity` with all 13 keys spelled out.
- After the restart: `pay_for_project_card` rejects `megaCredits` (pydantic `extra_forbidden`) and accepts `megacredits`,
  but the tool schema the client sees still lists `megaCredits` (the schema may be cached client-side).
- The `projectCard` examples in `agent-prompts/*/AGENTS.md` and the `submit_multi_actions` docstring still use `megaCredits`.

## 2. `or` options addressed by name: docs and schema out of date
- `choose_or_option` now requires `option_name`, but the advertised schema has only `option_index` (required) and `sub_response`.
- Nested `or` responses using `"index"` now fail with `'or' actions are addressed by 'name', not 'index'`.
  The AGENTS.md examples (milestone claim `{"type":"or","index":0,...}` and the multi-action pass example with `index: 5`) are now wrong.
- `waiting_for.options` no longer includes `index`, but `option_index` is still a required argument (redundant).

## 3. Ambiguous templated option titles can't be resolved (blocking) — FIXED
- Fix: `title_to_text` now renders `${n}` data into titles (players as their color). `find_or_option_index_by_name` matches either the rendered title or the placeholder-stripped template, and the ambiguity error lists the rendered titles.
- Asteroid's plant-removal prompt had two options titled `Remove ${0} plants from ${1}` (one for the opponent, one for self with
  warning `removeOwnPlants`). `_normalize_title` strips the placeholders, so both became `remove plants from` and
  `find_or_option_index_by_name` raised `Cannot uniquely resolve or-option`.
- Any prompt that differs only by title template data (player, amount) hits this: select-player-style `or` menus, steal effects, etc.
- Workaround used: `submit_raw_entity({"type":"option"})`, which got wrapped into the first `option`-typed branch (index 0).
  This only works by luck of ordering.
- Suggested fix: render the title with its `data` before matching (e.g. "Remove 3 plants from John"), expose warnings,
  and/or allow an index fallback when names collide.

## 4. Spurious error after a successful card play
- `pay_for_project_card("Sponsors")` (right after the MCP restart) played the card, but the response contained
  `"error": "HTTP 400 POST /player/input: Not waiting for anything"`. It looks like a second submit or refresh
  happened after the turn passed to the opponent.

## 5. `GameLogEntryModel.type` rejects value 2 (blocking at game end) — FIXED
- Fix: `LogMessageTypeLiteral` widened to `Literal[0, 1, 2]` to match the server's `LogMessageType` (DEFAULT, NEW_GENERATION, NOTICE).
- In the final generation (Gen 11, after terraforming finished), `pass_turn`, `choose_or_option` (final greenery placement)
  and `wait_for_turn` all failed with
  `1 validation error for GameLogEntryModel type: Input should be 0 or 1 [input_value=2]`.
- The server now sends log entries with `type: 2` (probably a new log message type used in end-of-game or production
  logs). The pydantic model uses `Literal[0, 1]`.
- The actions still went through on the server, but the MCP couldn't return state. I had to curl `/api/player`
  directly (outside the sandbox) to get the final score.
- Fix: widen the literal (or use `int`) and check the server's `LogMessageType` enum for all values.

## 6. Minor
- The `get_mars_board_state` reminder points to `agent-prompts/no_guide/tharsis-board-shape.md` whatever the agent's prompt folder is.
- To verify: Mohole Area placed on ocean space 63 (+2 titanium bonus) didn't seem to give the placement bonus.
  Check whether that matches the rules or is a bug.
