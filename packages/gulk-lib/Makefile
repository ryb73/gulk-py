test:
	uv run pytest

update-snapshots:
	uv run pytest --inline-snapshot=create,trim

check:
	uv run pyrefly check
	uv run ruff check
	uv run pyright

watch:
	watchexec -e py -- make check "&&" make update-snapshots

.PHONY: test check watch update-snapshots
