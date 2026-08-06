# Godot front-end for gulk-lib

## Context

`gulk-lib` (`packages/gulk-lib`) is a pure, dependency-free Python engine for a 20-hand trick-taking/bidding card game ("Gulk"). It's driven purely via `apply_event(state: GameState, event: GameEvent) -> None`, a mutating reducer over `NewGame | Deal | Bid | PlayCard`. Today the only "player" is `scripts/random_game.py`, a fuzzer that picks random legal moves and is used to generate the integration test's golden trace. There is no human-playable interface. We want a Godot client so a person can actually play a hand of Gulk against computer opponents.

Decisions made with the user (via `AskUserQuestion`):
- **Game mode**: single human + AI-controlled bots, all in one local session (no networked multiplayer, no hidden-info redaction needed since it's one trusted local process).
- **Integration**: a local server wraps `gulk-lib` and talks to the Godot client (as opposed to a subprocess/stdio pipe, or porting the engine to GDScript, which would fork the tested rules logic).
- **Transport**: WebSocket, not plain TCP sockets. On the Godot side both `StreamPeerTCP` and `WebSocketPeer` are built in; on the Python side plain TCP sockets are stdlib (`socket`/`asyncio`) but WebSocket is not — it needs the third-party `websockets` package. Both options work identically on Mac and Windows, so platform support doesn't distinguish them. The real tradeoff: plain TCP costs zero new Python dependencies but requires hand-rolled message framing (buffering partial reads, delimiting messages) on both ends; WebSocket costs one new dependency but both Godot's `WebSocketPeer` and the `websockets` library handle framing for you, and it's the standard choice if this ever needs to run through a browser export or a real network boundary later. Chose WebSocket for the reduced hand-rolled-protocol risk, accepting the one extra dependency.
- **Wire format**: extend the previously-designed-but-unbuilt msgspec codec ([[gulk_lib_deferred_event_serialization]] memory) rather than hand-rolled JSON.
- **Legal moves**: currently only exist ad hoc in `scripts/random_game.py` (`legal_cards`), and `apply_event.py:68` has a standing TODO to enforce follow-suit. Move this into `gulk-lib` proper as the single source of truth, closing that TODO.

## Architecture

```
Godot client (GDScript)  <--WebSocket, JSON-->  gulk-server (Python, new package)  -->  gulk-lib (existing)
```

`gulk-server` owns one authoritative `GameState` per session, is the only thing that calls `apply_event`, and drives AI bots automatically between human turns.

## Implementation steps

### 1. `gulk-lib` additions

**`legal_actions.py`** (new module in `packages/gulk-lib/src/gulk_lib/`):
- `get_legal_bids(state: GameState) -> list[int]` — the set of legal bid values for the current bidder. For most bidders that's the full `0..cards_dealt` range; for the last bidder it's that range minus whichever single value would violate "screw the dealer" (bids must not sum to cards dealt). This replaces the range-plus-exclusion logic currently tangled up with random selection in `scripts/random_game.py:_random_bid`.
- `get_legal_cards(state: GameState, player: PlayerId) -> list[Card]` — follow-suit-filtered legal plays (port of the filtering half of `scripts/random_game.py:53-73`)
- `get_next_actor(state: GameState) -> PlayerId | None` — whose turn it is (bidder or trick player), or `None` when the hand/game is complete and needs to advance. Needed by both the bot loop and the Godot UI (to know when to show controls vs. wait).

**`apply_event.py`**: replace the bare-assert follow-suit gap at line 68 with a call into `get_legal_cards`, closing the existing TODO. Keep raising on illegal input (still an internal invariant violation if `gulk-server` validates first), but `gulk-server` must catch and translate to a wire error rather than crash.

**`codec.py`** (new module): extends the msgspec design already scoped in memory rather than starting fresh.
- Convert only `events.py` and `cards.py` to `msgspec.Struct` (tagged unions: `Card` via `tag_field="kind"`, `GameEvent` via `tag_field="type"`), exactly as previously designed. `game_state.py`, `game_config.py`, `player_id.py` do not need conversion — msgspec encodes/decodes plain dataclasses natively, so `GameState` can be serialized directly once `GameEvent`/`Card` are Structs.
- Resolve the previously-open wire-format wrinkle for `Rank` (int/str mix) and suit (Unicode symbol vs. `S/H/D/C` letter): since `enc_hook`/`dec_hook` don't fire for natively-recognized `int`/`str` types (confirmed in the earlier design), do the rank/suit rewrite as an explicit translation step over `msgspec.to_builtins()` output before final JSON encoding, and the inverse on decode — not via hooks.
- Expose `encode_event`, `decode_event`, `encode_state`, `decode_state`.
- New dependency (`msgspec`): add via `uv add msgspec --package gulk-lib`, not by hand-editing `pyproject.toml`.

### 2. Design the client-server protocol (separate planning pass)

The WebSocket message protocol (envelope shapes, message types, ordering/handshake, error format) is substantial enough to deserve its own design doc rather than being fixed here. Once step 1 lands, do a follow-up planning pass covering:
- Exact message types for both directions (starting a game, submitting a bid/card, broadcasting state after each applied event, reporting errors).
- What subset of `GameState` actually needs to go over the wire per update vs. only the delta.
- How `get_next_actor`/`get_legal_bids`/`get_legal_cards` results get attached to outgoing state so Godot knows what input to show.

### 3. New package: `gulk-server`

`packages/gulk-server/` (new `uv` workspace member), depends on `gulk-lib`.

- New dependency: `websockets`, added via `uv add websockets --package gulk-server`.
- **Session**: one in-memory `GameState` per server run (no persistence, no multi-game routing — out of scope per current use case). No seat-selection step needed — dealer/turn order is already handled by the engine's existing rotation; the human is simply assigned a fixed seat.
- **Bot strategy**: `bots.py` with a minimal interface `Bot = Callable[[GameState, PlayerId], GameEvent]`. v1 bot picks uniformly at random among `legal_actions` outputs (i.e., promote the existing `random_game.py` fuzzer strategy from a test tool to the actual v1 opponent). Kept as a swappable single-function interface so a smarter bot can replace it later without a redesign.
- **Game loop**: on each human action, validate via `get_legal_bids`/`get_legal_cards`, apply it, then repeatedly call `get_next_actor` + the bot strategy to auto-apply bot turns, broadcasting an update after **every single applied event** (human or bot) — not just at the next human decision point — so the Godot client can animate deals/bids/trick plays one at a time instead of jumping straight to the next decision. Exact broadcast shape is defined in step 2.
- Illegal actions from the client are rejected with a typed error message, never let `apply_event`'s `AssertionError` crash the session.

### 4. Godot client

New top-level `godot/` project (GDScript, no C#).

- **`GulkClient.gd`** (autoload singleton): owns the `WebSocketPeer`, sends/receives the protocol from step 2, decodes into Godot `Dictionary`s (not generated typed classes — matches the "no premature abstraction" preference; revisit only if the dictionary access gets unwieldy), emits signals such as `state_updated(state: Dictionary)` and `error_received(msg: String)`.
- **`NewGameScreen.tscn`**: pick player count and joker count; sends the "start game" message.
- **`GameScreen.tscn`**: renders scores, current hand structure (round number, trump), the human's hand as legal/illegal-highlighted cards (using the legal-bids/legal-cards data attached to the latest update), and the current trick in progress. Since there's no hidden-info redaction, bot hands are present in the payload but simply not rendered face-up.
- Card visuals: no art assets exist yet. v1 uses simple text/color-coded placeholders (rank+suit label on a rect) rather than blocking on artwork — explicitly deferred.

## Explicitly out of scope for this pass
- Networked/multi-machine multiplayer and per-player redacted views.
- Event-log persistence (the msgspec codec is reused here for the live wire boundary, not wired up to disk persistence).
- Smarter-than-random bot strategy.
- Card artwork.

## Step-by-step breakdown

Discrete, independently-completable steps, roughly in dependency order:

1. **`gulk-lib`: legal-move queries.** Add `get_legal_bids`, `get_legal_cards`, `get_next_actor` to a new `legal_actions.py`, plus unit tests.
2. **`gulk-lib`: enforce follow-suit.** Wire `get_legal_cards` into `apply_event.py`, closing the line-68 TODO; update `scripts/random_game.py` and the integration test's random-play loop to use the new module instead of their local copies.
3. **`gulk-lib`: msgspec codec.** Convert `events.py`/`cards.py` to tagged `msgspec.Struct`s, resolve the Rank/suit wire-format translation, expose `encode_event`/`decode_event`/`encode_state`/`decode_state`.
4. **Design the client-server protocol.** Separate planning pass (see above) producing the concrete message schema for `gulk-server`.
5. **Scaffold `gulk-server`.** New `uv` workspace package, WebSocket connection handling, session holding one `GameState`, wired to the protocol from step 4 — human actions only, no bots yet.
6. **Bot strategy + auto-play loop.** Add `bots.py`'s random-choice `Bot`, and the game loop that auto-applies bot turns between human turns.
7. **Scaffold Godot project.** New `godot/` project with `GulkClient.gd` connecting to the server and logging received state.
8. **New-game screen.** `NewGameScreen.tscn` for player/joker count, sends the start-game message.
9. **Game screen.** `GameScreen.tscn` rendering scores, hand, current trick, and bid/play controls constrained by the legal-moves data attached to each update; placeholder (non-art) card visuals.
10. **End-to-end playtest.** Play a full hand human-vs-bots, fix whatever the first real playthrough surfaces.

## Verification
- `gulk-lib`: unit tests for `get_legal_bids`/`get_legal_cards`/`get_next_actor` (pytest, `inline-snapshot`, matching existing test style in `packages/gulk-lib/tests`), plus update `scripts/random_game.py` and the integration test's random-play loop to call the new `legal_actions` module instead of its local copy, confirming the existing golden-file integration test (`test_random_game`) still passes unchanged.
- `gulk-server`: a small integration test using a `websockets` test client — connect, start a game, receive the initial update, send an illegal action and assert an error reply, send a legal one and assert bots auto-play their turns.
- End-to-end: run `gulk-server` locally, open the Godot project in the editor, play through at least one full hand (bid, play a trick, see scoring applied) against the bots, confirming the UI matches server-side state at each step.
