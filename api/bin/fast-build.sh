#!/bin/bash

cd "$(dirname "$0")" || exit $?

. config.sh

docker build --build-arg VERSION="$VERSION" -t "$EDPAPI_IMAGE_NAME" ..
cd ../../src/main/Central/build || exit $?
docker build --build-arg VERSION="$VERSION" -t "${SEQAM_COMMAND_TRANSLATOR_IMAGE_NAME}" -f Dockerfile-command-translator ..
docker build --build-arg VERSION="$VERSION" -t "${SEQAM_EVENT_ORCHESTRATOR_IMAGE_NAME}" -f Dockerfile-event-orchestrator ..
docker build --build-arg VERSION="$VERSION" -t "${SEQAM_EXPERIMENT_DISPATCHER_IMAGE_NAME}" -f Dockerfile-experiment-dispatcher ..

cd ../..

docker build --build-arg VERSION="$VERSION" -t "${SEQAM_DISTRIBUTED_EVENT_MANAGER_IMAGE_NAME}" -f Distributed/Modules/EventManager/Dockerfile .

docker build --build-arg VERSION="$VERSION" -t "${SEQAM_NETWORK_EVENT_MANAGER_IMAGE_NAME}" -f Network/Modules/EventManager/Dockerfile .
