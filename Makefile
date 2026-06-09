.PHONY: install test up down logs

install:
	uv pip install -r requirements.txt

test:
	pytest -q

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

