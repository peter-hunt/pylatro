# RNG Seed Verification

This guide covers how to verify deterministic seeded RNG behavior in Pylatro.

## 1. Install dependencies

From project root:

```bash
pip install -e .
pip install -r requirements.txt
pip install lupa pytest
```

Note: current implementation guarantees deterministic reproducibility in Pylatro. A LuaJIT-specific matching mode is planned for stricter one-to-one alignment with Balatro runtime internals.

## 2. Generate a trace report

Use the built-in report CLI:

```bash
python -m pylatro.rng.report --seed 7LB2WVPK --antes 2 --shop-cards 2 --erratic-count 20
```

Include non-erratic deck pull verification:

```bash
python -m pylatro.rng.report --seed 7LB2WVPK --antes 2 --shop-cards 2 --standard-deck default --standard-draw-count 12
```

The report includes:

- Event index
- Event type
- RNG key used
- Pre-state and post-state for that key
- Selected value
- Selected index in the source pool (`pick_index`)
- Final `trace_hash` summary line

Joker generation additionally includes explicit rarity trace lines and stream key names like `key=Joker22`, making it easy to verify ante/rarity stream usage.

Repeat the same command and confirm identical output.

## 3. Run deterministic tests

```bash
pytest -q tests/test_rng_engine.py tests/test_rng_report.py
```

These tests validate:

- Same seed produces identical sequences
- Snapshot/restore reproduces continuation exactly
- Report output stability and hash presence

## 4. Validate known public seeds

Examples from community documentation:

- `7LB2WVPK`
- `XEQH7CP9`

Run report for each and archive outputs as golden references.

## 5. Troubleshooting mismatch

If output differs across runs/platforms, check:

1. Lua runtime version and backend (`lupa`/LuaJIT)
2. Pool ordering consistency
3. Event call order drift
4. Any direct Python RNG usage mixed into deterministic flows
