# RNG Design

Pylatro's RNG subsystem is designed to reproduce Balatro-style seeded behavior for deterministic tutorials and seed follow-alongs.

## Architecture

- Lua bridge: `src/pylatro/rng/bridge.lua`
- Python wrapper: `src/pylatro/rng/engine.py`
- Event-order API: `src/pylatro/rng/events.py`
- Verification reports: `src/pylatro/rng/report.py`

## Why Lua bridge first

Balatro's RNG path uses Lua `math.randomseed` and `math.random` seeded from stream-specific values after `pseudoseed`. The safest way to preserve behavior is to execute equivalent Lua code directly instead of rewriting all numeric details in pure Python first.

## Current runtime mode

The current implementation runs through `lupa` and includes a compatibility RNG in the Lua bridge for environments where Lua's native `math.randomseed` integer semantics differ from Balatro's target runtime.

- Implemented now: deterministic, reproducible seeded behavior across sessions and tests.
- Planned next: LuaJIT-specific path to maximize one-to-one matching with Balatro's runtime behavior.

## Precision considerations

Key precision points retained:

- Stream advancement constants and modulo ordering
- Decimal formatting to `%.13f` during stream advancement
- Key-scoped mutable stream state

## State model

The engine stores the full pseudorandom table and supports snapshot/restore to make run save/load deterministic.

## Current scope

Implemented in this phase:

- Core key-stream RNG calls
- Startup pulls
- Shop joker/consumable pulls with resample keys
- Edition poll helper
- Erratic deck face generation
- Seed trace reporting

Next integration phase will wire this subsystem directly into run simulation and full content pools.
