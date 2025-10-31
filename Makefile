up:
	cd deploy && docker compose -f docker-compose.dev.yml up --build -d
down:
	cd deploy && docker compose -f docker-compose.dev.yml down -v
logs:
	cd deploy && docker compose -f docker-compose.dev.yml logs -f --tail=100
