.PHONY: install run test lint docker-up docker-down migrate seed

install:
	pip install -r requirements.txt

run:
	FLASK_ENV=development python run.py

test:
	pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html

lint:
	flake8 app/ --max-line-length=100 --exclude=__pycache__

migrate:
	flask db init && flask db migrate -m "initial" && flask db upgrade

seed:
	flask shell -c "from app.models.exam import seed_questoes; seed_questoes()"

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down -v

worker:
	celery -A run.celery worker --loglevel=info

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete
	rm -rf htmlcov .coverage
