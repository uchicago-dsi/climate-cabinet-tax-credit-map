# Command shortcuts for building and running Docker Compose services

# Change current working directory
mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
current_dir := $(notdir $(patsubst %/,%,$(dir $(mkfile_path))))
current_abs_path := $(subst Makefile,,$(mkfile_path))
$(shell cd $(current_abs_path) > /dev/null)

# Export environment variables used by all targets
.EXPORT_ALL_VARIABLES:
DOCKER_PLATFORM := $(shell . ./set_arch.sh)
COMPOSE_PROJECT := "climate-cabinet-tax-credit-map"

# Declare targets
run-pipeline-execution:
	bash -c "trap 'docker compose -p $(COMPOSE_PROJECT) down' EXIT; \
		docker compose -p $(COMPOSE_PROJECT) -f compose/compose.yaml --profile pipeline up --build"

run-dashboard:
	bash -c "trap 'docker compose -p $(COMPOSE_PROJECT) down' EXIT; \
		docker compose -p $(COMPOSE_PROJECT) -f compose/compose.yaml --profile dashboard up --build"

run-database:
	bash -c "trap 'docker compose -p $(COMPOSE_PROJECT) down' EXIT; \
		docker compose -p $(COMPOSE_PROJECT) -f compose/compose.yaml up --build"

run-pipeline-interactive:
	docker compose -p $(COMPOSE_PROJECT) \
		-f compose/compose.yaml \
		-f compose/compose.interactive.yaml \
		--profile pipeline up --build -d
	bash -c "trap 'docker compose -p $(COMPOSE_PROJECT) down' EXIT; \
		docker exec -it pipeline /bin/bash"

test-pipeline:
	bash -c "trap 'docker compose -p $(COMPOSE_PROJECT) down' EXIT; \
		docker compose -p $(COMPOSE_PROJECT) -f compose/compose.unittest.yaml up -d && \
		docker exec -it test-pipeline ls && \
		docker exec -it test-pipeline python -m manage makemigrations && \
		docker exec -it test-pipeline python -m manage migrate && \
		docker exec -it test-pipeline pytest -s && \
		docker exec -it test-pipeline rm -R .pytest_cache && \
		docker rm -f test-pipeline test-postgis"
