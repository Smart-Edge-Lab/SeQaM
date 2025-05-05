#!/bin/bash

cd "$(dirname "$0")" || exit $?

. config.sh

cd ../.. || exit $?

docker build --build-arg VERSION="$VERSION" -t "$EDPAPI_IMAGE_NAME" -f api/Dockerfile . || exit $?
docker build --build-arg VERSION="$VERSION" -t "${SEQAM_COMMAND_TRANSLATOR_IMAGE_NAME}" \
  -f src/main/Central/build/Dockerfile-command-translator . || exit $?
docker build --build-arg VERSION="$VERSION" -t "${SEQAM_EVENT_ORCHESTRATOR_IMAGE_NAME}" \
  -f src/main/Central/build/Dockerfile-event-orchestrator . || exit $?
docker build --build-arg VERSION="$VERSION" -t "${SEQAM_EXPERIMENT_DISPATCHER_IMAGE_NAME}" \
  -f src/main/Central/build/Dockerfile-experiment-dispatcher . || exit $?

docker build --build-arg VERSION="$VERSION" -t "${SEQAM_DISTRIBUTED_EVENT_MANAGER_IMAGE_NAME}" \
  -f src/main/Distributed/Modules/EventManager/Dockerfile . || exit $?

docker build --build-arg VERSION="$VERSION" -t "${SEQAM_NETWORK_EVENT_MANAGER_IMAGE_NAME}" \
  -f src/main/Network/Modules/EventManager/Dockerfile . || exit $?
