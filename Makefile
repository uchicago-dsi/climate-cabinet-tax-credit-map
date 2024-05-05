# Command shortcuts for building and running Docker Compose services

# Change current working directory
mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
current_dir := $(notdir $(patsubst %/,%,$(dir $(mkfile_path))))
current_abs_path := $(subst Makefile,,$(mkfile_path))
$(shell cd $(current_abs_path) > /dev/null)

# Export environment variables used by all targets
.EXPORT_ALL_VARIABLES:
DOCKER_PLATFORM := $(shell . ./set_arch.sh)

# Declare targets
run-pipeline-execution:
	docker compose --profile pipeline-execution up --build
	docker rm -f pipeline-execution

run-dashboard:
	docker compose --profile dashboard up --build

run-database:
	docker compose up --build

run-pipeline-interactive:
	docker compose --profile pipeline-interactive up --build -d
	docker exec -it pipeline-interactive /bin/bash
	docker rm -f pipeline-interactive

test-pipeline:
	docker compose -f pipeline/unittest.docker-compose.yml up -d
	docker exec -it test-app ls
	docker exec -it test-app python -m manage makemigrations
	docker exec -it test-app python -m manage migrate
	docker exec -it test-app pytest -s
	docker exec -it test-app rm -R .pytest_cache
	docker rm -f test-app test-db
