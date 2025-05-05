#!/bin/bash -x

cd "$(dirname "$0")" || exit $?

. config.sh

docker push "$EDPAPI_IMAGE_NAME"
docker push "${SEQAM_COMMAND_TRANSLATOR_IMAGE_NAME}"
docker push "${SEQAM_EVENT_ORCHESTRATOR_IMAGE_NAME}"
docker push "${SEQAM_EXPERIMENT_DISPATCHER_IMAGE_NAME}"
docker push "${SEQAM_DISTRIBUTED_EVENT_MANAGER_IMAGE_NAME}"
docker push "${SEQAM_NETWORK_EVENT_MANAGER_IMAGE_NAME}"
