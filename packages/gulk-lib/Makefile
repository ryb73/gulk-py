test:
	uv run pytest

watch:
	watchexec -e py -- uv run pyrefly check "&&" uv run pytest --inline-snapshot=create,fix,update,trim

.PHONY: test watch
