test:
	uv run pytest

check:
	uv run pyrefly check
	uv run ruff check
	uv run pyright

watch:
	watchexec -e py -- make check "&&" uv run pytest --inline-snapshot=create,trim

.PHONY: test check watch
