.PHONY: install test frontend-install frontend-build up down logs

install:
	uv pip install -r requirements.txt

test:
	pytest -q

frontend-install:
	cd frontend && npm install

frontend-build:
	cd frontend && npm run build

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f
