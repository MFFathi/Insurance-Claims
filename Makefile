prod:
	docker compose -f docker-compose.yml up

test:
	docker compose -f docker-compose.yml -f docker-compose.test.yml up --exit-code-from app

test-watch:
	docker compose -f docker-compose.yml -f docker-compose.test.yml -f docker-compose.test.watch.yml up --exit-code-from app