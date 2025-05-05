#!/bin/bash

cd "$(dirname "$0")"

./test.sh || exit $?

../../src/bin/test.sh || exit $?

. config.sh

. check-health.sh

docker build --build-arg VERSION="$VERSION" -t "$EDPAPI_IMAGE_NAME" ..
cd ../../src/main/Central/build
docker build --build-arg VERSION="$VERSION" -t "${SEQAM_COMMAND_TRANSLATOR_IMAGE_NAME}" -f Dockerfile-command-translator ..
docker build --build-arg VERSION="$VERSION" -t "${SEQAM_EVENT_ORCHESTRATOR_IMAGE_NAME}" -f Dockerfile-event-orchestrator ..
docker build --build-arg VERSION="$VERSION" -t "${SEQAM_EXPERIMENT_DISPATCHER_IMAGE_NAME}" -f Dockerfile-experiment-dispatcher ..
docker compose up -d --remove-orphans || exit $?
sleep $HEALTH_CHECK_DELAY
check_central_components_health
docker compose down

cd ../..

docker build --build-arg VERSION="$VERSION" -t "${SEQAM_DISTRIBUTED_EVENT_MANAGER_IMAGE_NAME}" -f Distributed/Modules/EventManager/Dockerfile .
cd Distributed/Modules/EventManager
docker compose -f ./docker-compose.yml up -d --remove-orphans || exit $?
sleep $HEALTH_CHECK_DELAY
check_health distributed_event_manager ${DISTRIBUTED_EVENT_MANAGER_PORT}
docker compose -f ./docker-compose.yml down

cd ../../..

docker build --build-arg VERSION="$VERSION" -t "${SEQAM_NETWORK_EVENT_MANAGER_IMAGE_NAME}" -f Network/Modules/EventManager/Dockerfile .
cd Network/Modules/EventManager
docker compose up -d --remove-orphans || exit $?
sleep $HEALTH_CHECK_DELAY
check_health network_event_manager ${NETWORK_EVENT_MANAGER_PORT}
docker compose down
