# Command shortcuts for building and running Docker images

mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
current_dir := $(notdir $(patsubst %/,%,$(dir $(mkfile_path))))
current_abs_path := $(subst Makefile,,$(mkfile_path))

run-database:
	cd $(current_abs_path)
	docker compose up --build

build-pipeline:
	cd $(current_abs_path)
	docker compose --profile pipeline build

run-pipeline:
	cd $(current_abs_path)
	docker compose --profile pipeline up --build

run-dashboard:
	cd $(current_abs_path)
	docker compose --profile dashboard up --build
	docker compose up

test-pipeline:
	docker compose -f tests/docker-compose.unittest.yml up -d
	docker exec -it test-app ls
	docker exec -it test-app python -m manage makemigrations
	docker exec -it test-app python -m manage migrate
	# docker exec -it test-app pytest tests/test_load_tables.py::test_load_assoc_with_state_fips_match -s
	docker exec -it test-app pytest -s

clean:
	find . | grep -E "(/__pycache__\$$|/migrations/.*_initial.py)" | xargs rm -rf
	rm -rf pgdata
	cd pipeline && python3 manage.py makemigrations
	