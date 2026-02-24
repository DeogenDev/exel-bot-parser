DC = docker compose
BOT = bot
WORKER = celery-worker

.PHONY: rebuild-app

rebuild-app:
	$(DC) rm -f -s -v $(BOT) $(WORKER)
	$(DC) up -d --build $(BOT) $(WORKER)
	$(DC) logs -f
