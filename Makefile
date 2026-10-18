.PHONY: install run test lint seed evaluate up down clean

install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --reload

test:
	pytest -v

lint:
	ruff check .

seed:
	python scripts/seed.py

evaluate:
	python scripts/evaluate_ai.py

up:
	docker compose up --build

down:
	docker compose down

clean:
	rm -f helpdesk.db
