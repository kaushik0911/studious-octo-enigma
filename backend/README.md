uv run alembic upgrade head

uv run python -m main

alembic revision --autogenerate -m "alter email column in Author table"
