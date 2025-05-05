#!/bin/bash

cd "$(dirname "$0")" || exit $?

./test.sh || exit $?

../../src/bin/test.sh || exit $?

. config.sh

. check-health.sh

./fast-build.sh || exit $?

cd ../../src/main/Central/build || exit $?
export SEQAM_SKIP_MIGRATIONS=TRUE
docker compose up -d --remove-orphans || exit $?
sleep $HEALTH_CHECK_DELAY
check_central_components_health
unset SEQAM_SKIP_MIGRATIONS
docker compose down

cd ../..

cd Distributed/Modules/EventManager || exit $?
docker compose -f ./docker-compose.yml up -d --remove-orphans || exit $?
sleep $HEALTH_CHECK_DELAY
check_health distributed_event_manager ${DISTRIBUTED_EVENT_MANAGER_PORT}
docker compose -f ./docker-compose.yml down

cd ../../..

cd Network/Modules/EventManager || exit $?
docker compose up -d --remove-orphans || exit $?
sleep $HEALTH_CHECK_DELAY
check_health network_event_manager ${NETWORK_EVENT_MANAGER_PORT}
docker compose down
