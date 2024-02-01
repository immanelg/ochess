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
	docker-compose exec app alembic downgrade {{args}}

fmt:
	docker-compose exec app ruff format src

lint:
	docker-compose exec app ruff --fix src

lint-fmt: format lint

test:
	docker-compose exec app pytest tests/

pre-commit:
	pre-commit run --all-files

ui-build:
	npm run build

ui-build-watch:
	npm run watch

ui-fmt:
	npm run fmt

ui-test:
	npm run test
