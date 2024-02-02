up:
	docker-compose up -d

kill:
	docker-compose kill

build:
	docker-compose build

ps:
	docker-compose ps

logs:
	docker-compose logs -f

db-genmigration:
	docker-compose exec app alembic revision --autogenerate 

db-upgrade:
	docker-compose exec app alembic upgrade head

db-downgrade:
	docker-compose exec app alembic downgrade -1 

fmt:
	docker-compose exec app ruff format

lint:
	docker-compose exec app ruff --fix

check:
	docker-compose exec app ruff 

test:
	docker-compose exec app pytest tests/

pre-commit:
	pre-commit run --all-files
