# COLORS
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE  := $(shell tput -Txterm setaf 7)
RESET  := $(shell tput -Txterm sgr0)


TARGET_MAX_CHAR_NUM=20
## Show help
help:
	@echo ''
	@echo 'Usage:'
	@echo '  ${YELLOW}make${RESET} ${GREEN}<target>${RESET}'
	@echo ''
	@echo 'Targets:'
	@awk '/^[a-zA-Z\-\_0-9]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			helpCommand = substr($$1, 0, index($$1, ":")-1); \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			printf "  ${YELLOW}%-$(TARGET_MAX_CHAR_NUM)s${RESET} ${GREEN}%s${RESET}\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST)

.PHONY: dc-build
## Build Docker-compose
dc-build: flake8
	docker-compose build

.PHONY: dc-up
## up Docker-compose
dc-up:
	docker-compose up

.PHONY: dc-down
## down Docker-compose
dc-down:
	docker-compose down

.PHONY: start-voice-system
## start voice system
start-voice-system:
	python speech/process.py

.PHONY: flake8
## flake8
flake8:
	flake8 .

.PHONY: clean
## clean
clean:
	find . -type d -name  "__pycache__" -exec rm -r {} +


