
.PHONY: all run test stop clean

all: run

run:
	docker-compose -f docker-compose.yml up -d
test:
	docker-compose exec web pytest
stop:
	docker-compose stop
clean:
	docker ps -a  | grep payroll_web | awk '{print $$1}' | xargs docker rm
