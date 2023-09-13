# Command shortcuts for building and running Docker images

mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
current_dir := $(notdir $(patsubst %/,%,$(dir $(mkfile_path))))
current_abs_path := $(subst Makefile,,$(mkfile_path))

build-pipeline:
	cd $(current_abs_path)
	docker-compose --profile pipeline build

run-pipeline:
	cd $(current_abs_path)
	docker-compose --profile pipeline up --build

run-dashboard:
	cd $(current_abs_path)
	docker-compose --profile dashboard up --build
	docker-compose up

clean:
	find . | grep -E "(/__pycache__\$$|/migrations/.*_initial.py)" | xargs rm -rf
	rm -rf pgdata/*

.PHONY: clean
