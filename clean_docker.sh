#!/bin/bash

docker compose --profile "*" stop
docker builder prune -a
docker image prune -a
docker container prune
docker network prune
