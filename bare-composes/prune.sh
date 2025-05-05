#!/bin/bash

docker container prune
docker rmi "$(docker images | grep '172.22.174.190:5000/')"
