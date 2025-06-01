set -e
ruff check --fix .
ruff format .
mypy --strict .
pytest -vv .
