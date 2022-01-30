.PHONY: format
format:
	poetry run black .

.PHONY: format-check
format-check:
	poetry run black . --check

.PHONY: test
test:
	poetry run pytest

.PHONY: test-cov
test-cov:
	poetry run pytest --cov --cov-report html


.PHONY: lint
lint:
	poetry run flake8
