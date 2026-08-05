## What this is

Integration tests that chain multiple `GameEvent`s through `apply_event()` and check the
resulting `GameState`, as opposed to `tests/test_apply_event.py`'s one-event-at-a-time unit
tests.

## Conventions

- **Input** (the event sequence): hardcoded Python objects directly in the test, same style
  as `tests/test_apply_event.py` (`build_deck()`, `make_player()`, etc.)
- **Output** (expected `GameState`): a golden file, external to the test source, via
  `inline_snapshot`'s built-in `external()` — not a hand-rolled fixture loader, not a new
  dependency. See existing tests for usage.

## Gotcha: creating a new named golden file

Naming an `external("some_name.ext")` explicitly (rather than calling it bare) means, on
first creation, plain `make update-snapshots` (`--inline-snapshot=create,trim`) is **not**
enough — it raises `StorageLookupError`, because a named-but-nonexistent location isn't
treated as "empty" by inline-snapshot's internal check (only a location with no name at all
is). To seed a newly-named external for the first time, run once with `fix` included,
scoped to just the test node you're creating (not the whole suite — `fix` will silently
overwrite any other mismatching snapshot it collects along the way):

```
uv run pytest tests/integration/test_integration.py::test_new_game --inline-snapshot=create,fix,trim
```

After that, `make update-snapshots` / `make test` work normally against the now-existing
file. `fix` is deliberately left out of `make update-snapshots` in the package `Makefile` (to
avoid silently overwriting existing snapshots on mismatch).
