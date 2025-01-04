default:
    just --list --unsorted

# renew app and run migrations
[group('setup')]
renew: build db-upgrade

# build all or selected services
[group('build')]
build:
    docker-compose build;

# TODO: Version number/tag
[group('build')]
build-prod:
    docker-compose -f compose.yaml build;

# start dev containers and attach
[group('manage')]
up SERVICE="":
    if [ "{{SERVICE}}" = "" ]; then \
        docker-compose up; \
    else \
        docker-compose up {{SERVICE}}; \
    fi

# start dev containers detached
[group('manage')]
up-d SERVICE="":
    if [ "{{SERVICE}}" = "" ]; then \
        docker-compose up -d; \
    else \
        docker-compose up {{SERVICE}} -d; \
    fi

# stops running containers
[group('manage')]
stop:
    docker-compose stop

# stops and removes running containers and associated networks
[confirm('\033[31mWarning: This action will stop and remove all running containers, networks, and volumes defined in your compose.yml.\nAll unsaved data in the containers will be lost.\033[0m\nAre you sure you want to proceed with docker-compose down? (y/n)')]
[group('manage')]
down:
    docker-compose down

# shell into the specified container/ service (dev)
[group('dev')]
sh SERVICE:
    docker-compose exec {{SERVICE}} bash

# run the test suite for the specified container/ service
[group('dev')]
test SERVICE:
    docker-compose run {{SERVICE}} pytest

# db create revision from webapp (manually create migration)
[group('db')]
db-add-rev MSG:
    docker-compose run core-id alembic revision -m "{{MSG}}"

# db upgrade via webapp
[group('db')]
db-upgrade:
    docker-compose run core-id alembic upgrade head
