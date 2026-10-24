.PHONY: install run test coverage lint seed evaluate benchmark up down clean

install:
	pip install -r requirements.txt -r requirements-dev.txt

run:
	uvicorn app.main:app --reload

test:
	pytest -v

coverage:
	pytest -v --cov=app --cov-report=term-missing

lint:
	ruff check .

seed:
	python scripts/seed.py

benchmark:
	python scripts/benchmark.py

evaluate:
	python scripts/benchmark.py

up:
	docker compose up --build

down:
	docker compose down

clean:
	rm -f helpdesk.db
