## Make all targets .PHONY
.PHONY: $(shell sed -n -e '/^$$/ { n ; /^[^ .\#][^ ]*:/ { s/:.*$$// ; p ; } ; }' $(MAKEFILE_LIST))

SHELL = /usr/bin/env bash
USER_NAME = $(shell whoami)
USER_ID = $(shell id -u)
HOST_NAME = $(shell hostname)

ifeq (., $(shell which docker-compose))
	DOCKER_COMPOSE_COMMAND = docker compose
else
	DOCKER_COMPOSE_COMMAND = docker-compose
endif

SERVICE_NAME = app
CONTAINER_NAME = bullyguard-data-preparation-container

DIRS_TO_VALIDATE = bullyguard
DOCKER_COMPOSR_RUN = ${DOCKER_COMPOSE_COMMAND}	 run --rm $(SERVICE_NAME)
DOCKER_COMPOSE_EXEC = ${DOCKER_COMPOSE_COMMAND} exec $(SERVICE_NAME)

export

## returns: true if the stem is a non-empty environment variable, or raises an error
guard-%:
	@#$(or ${$*}, $(error $* is not set))

## call entrypoint:
process-data: up
	$(DOCKER_COMPOSE_EXEC) python ./bullyguard/process_data.py

## starts jupyter notebook
notebook: up
	$(DOCKER_COMPOSE_EXEC) jupyter-lab --ip 0.0.0.0 --port 8888 --no-browser

## using isort:
sort: up
	$(DOCKER_COMPOSE_EXEC) isort --atomic $(DIRS_TO_VALIDATE)

## check the sorting using isort
sort-check: up
	$(DOCKER_COMPOSE_EXEC) isort --check-only --atomic bullyguard $(DIRS_TO_VALIDATE)

## format code using Black
format: up
	$(DOCKER_COMPOSE_EXEC) black $(DIRS_TO_VALIDATE)

## check format using black
format-check: up
	$(DOCKER_COMPOSE_EXEC) black --check $(DIRS_TO_VALIDATE)

## format and sort code with black an isort
format-and-sort: sort format

## Linting using flake8
lint: up format-check sort-check
	$(DOCKER_COMPOSE_EXEC) flake8 $(DIRS_TO_VALIDATE)

## check type annotations with mypy
check-type-annotations: up
	$(DOCKER_COMPOSE_EXEC) mypy $(DIRS_TO_VALIDATE)

## Run tests with pytest
test: up
	$(DOCKER_COMPOSE_EXEC) pytest

##perform full check
full-check: lint check-type-annotations
	$(DOCKER_COMPOSE_EXEC) pytest --cov  --cov-report xml --verbose

## builds docker image
build:
	$(DOCKER_COMPOSE_COMMAND) build $(SERVICE_NAME)

## remove poetry.lock and build docker image
build-for-dependencies:
	rm -f *.lock
	$(DOCKER_COMPOSE_COMMAND) build $(SERVICE_NAME)

## lock dependencies with poetry
lock-dependencies: build-for-dependencies
	$(DOCKER_COMPOSE_RUN) bash -c "if [ -e /home/$(USER_NAME)/poetry.lock.build ]; then \
        cp /home/$(USER_NAME)/poetry.lock.build ./poetry.lock; \
    else \
        poetry lock; \
    fi"

## startup docker containers using "docker compose up -d"
up:
	$(DOCKER_COMPOSE_COMMAND) up -d

## docker compose down
down:
	$(DOCKER_COMPOSE_COMMAND) down

## open interactive shell in docker container
exec-in: up
	docker exec -it $(CONTAINER_NAME) bash

.DEFAULT_GOAL := help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
# call Make
.PHONY: help
help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=36 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')