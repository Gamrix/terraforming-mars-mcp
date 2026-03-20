# `choose_or_option` Input Format Log (Game: 2026-02-14)

Purpose:
- Track every distinct payload shape I used with `choose_or_option` in this game.
- Record whether each format succeeded.
- Record how the payload was derived.

## Format A: direct index only
Payload example:
```json
{"option_index":"1"}
```
Result:
- Mixed.
- Success when selected branch expected plain `option` confirmation.
- Failed when selected branch expected a typed nested response (for example `projectCard`).
- Concrete failure seen Gen 6: `HTTP 400 ... Not a valid SelectProjectCardToPlayResponse`.
How I chose it:
- Used when `waiting_for.input_type` was `or` and I expected default nested `{"type":"option"}` to be acceptable.
- Derived from `server.py` normalization: missing `sub_response_json` defaults nested response to `{"type":"option"}`.

## Format B: direct index + empty nested response
Payload example:
```json
{"option_index":"0","sub_response_json":""}
```
Result:
- Success in branches that accept `option` nested response.
How I chose it:
- Used as explicit equivalent of default `option` nested response.
- Derived from `server.py` `_normalize_or_sub_response` behavior (`""` -> `{"type":"option"}`).

## Format C: direct index + nested `projectCard` response
Payload example:
```json
{
  "option_index":"1",
  "sub_response_json":"{\"type\":\"projectCard\",\"card\":\"Geothermal Power\",\"payment\":{\"megaCredits\":9,\"steel\":0,\"titanium\":0,\"heat\":0,\"plants\":0,\"microbes\":0,\"floaters\":0,\"lunaArchivesScience\":0,\"spireScience\":0,\"seeds\":0,\"auroraiData\":0,\"graphene\":0,\"kuiperAsteroids\":0}}"
}
```
Result:
- Success.
How I chose it:
- `waiting_for.options[index].input_type` was `projectCard`, so nested response had to be a `projectCard` entity.
- Full payment object was included because partial payment payloads fail validation for this flow.
- Field names matched server helper `_encode_payment` output in `server.py`.

## Format I: direct index + nested `projectCard` with partial payment object
Payload example:
```json
{
  "option_index":"0",
  "sub_response_json":"{\"type\":\"projectCard\",\"card\":\"Tropical Resort\",\"payment\":{\"steel\":5,\"megaCredits\":1}}"
}
```
Result:
- Failed.
- Error: `HTTP 400 ... payment is not a valid type`.
How I chose it:
- Initial attempt used only resources actually spent.
- Rejected because backend `isPayment` requires every spendable key to exist as a number.
- Fixed by switching to Format C with full 13-field payment object.

## Format J: direct index + nested `projectCard` without `payment`
Payload example:
```json
{
  "option_index":"0",
  "sub_response_json":"{\"type\":\"projectCard\",\"card\":\"Tropical Resort\"}"
}
```
Result:
- Failed.
- Error: `HTTP 400 ... Not a valid SelectProjectCardToPlayResponse`.
How I chose it:
- Tried as an intermediate fallback to see if payment would be prompted in a separate step.
- Rejected because `SelectProjectCardToPlayResponse` requires exact keys `type`, `card`, and `payment`.

## Format K: direct index + nested `card` response (multi-card list for sell patents)
Payload example:
```json
{
  "option_index":"5",
  "sub_response_json":"{\"type\":\"card\",\"cards\":[\"Nitrophilic Moss\",\"Black Polar Dust\",\"Power Grid\",\"Aquifer Pumping\",\"Large Convoy\",\"Worms\",\"Electro Catapult\",\"Permafrost Extraction\",\"Lightning Harvest\"]}"
}
```
Result:
- Success.
How I chose it:
- The selected `or` branch was `Sell patents` with `input_type: card` and `min/max` greater than 1.
- Card names were chosen only from that branch's `detail.cards` list.

## Format L: direct index + nested explicit `option` response (pass)
Payload example:
```json
{
  "option_index":"4",
  "sub_response_json":"{\"type\":\"option\"}"
}
```
Result:
- Success.
How I chose it:
- Selected when the `or` branch was `Pass for this generation` with `input_type: option`.
- Used explicit option payload rather than relying on default/empty normalization.

## Format D: direct index + nested `card` response (blue-card action)
Payload example:
```json
{
  "option_index":"0",
  "sub_response_json":"{\"type\":\"card\",\"cards\":[\"AI Central\"]}"
}
```
Result:
- Success.
How I chose it:
- `waiting_for.options[index].input_type` was `card` with single-card action selection.
- Card name selected from the exact `waiting_for.options[index].detail.cards` list.

## Format E: direct index + nested `or` response (nested decision)
Payload example:
```json
{
  "option_index":"0",
  "sub_response_json":"{\"type\":\"or\",\"index\":0,\"response\":{\"type\":\"option\"}}"
}
```
Result:
- Success (used for claiming `Builder` milestone in Gen 6).
How I chose it:
- Outer `or` option pointed to another inner `or` prompt (for example milestone/award list), so nested response itself had to be `type: "or"` with selected inner index.
- Inner index chosen from nested `waiting_for.options[outer].detail.options`.

## Format F: legacy `request` payload with nested response object
Payload example:
```json
{
  "request":"{\"index\":0,\"response\":{\"type\":\"projectCard\",\"card\":\"...\",\"payment\":{...}}}"
}
```
Result:
- Success in prior turns.
How I chose it:
- Used to validate backward-compatible path in `choose_or_option` (`request` accepts `index`/`response`).
- Derived from tool docstring and parsing code in `server.py`.

## Format G: legacy `request` payload with stringified nested response
Payload example:
```json
{
  "request":"{\"option_index\":\"1\",\"sub_response_json\":\"{\\\"type\\\":\\\"projectCard\\\",...}\"}"
}
```
Result:
- Success in prior turns.
How I chose it:
- Used to validate alternate legacy parsing path (`option_index` and `sub_response_json`) handled by `choose_or_option`.

## Format H: direct index + nested `space` response (tile placement)
Payload example:
```json
{
  "option_index":"0",
  "sub_response_json":"{\"type\":\"space\",\"spaceId\":\"55\"}"
}
```
Result:
- Success (used for greenery conversion placement in Gen 7 and Gen 8).
How I chose it:
- `waiting_for.options[index].input_type` was `space`, so nested response had to provide `spaceId`.
- Selected `spaceId` directly from `waiting_for.options[index].detail.spaces`.

## Payload Option Selection Method (used consistently)
1. Read `waiting_for.input_type`; if not `or`, do not use `choose_or_option`.
2. Pick outer option index from `waiting_for.options[*].index` and `title`.
3. Inspect selected option `input_type`:
- `option` -> nested default `{"type":"option"}` is valid.
- `card` -> nested `{"type":"card","cards":[...]} `.
- `projectCard` -> nested `{"type":"projectCard","card":"...","payment":{full object}}`.
- `or` -> nested `{"type":"or","index":...,"response":...}`.
- `space` -> nested `{"type":"space","spaceId":"..."}`.
4. Only select cards shown in that option's `detail.cards` to avoid unknown-card errors.
5. For nested `projectCard`, include all spendable payment keys with numeric values:
- `megaCredits`, `steel`, `titanium`, `heat`, `plants`, `microbes`, `floaters`, `lunaArchivesScience`, `spireScience`, `seeds`, `auroraiData`, `graphene`, `kuiperAsteroids`.
