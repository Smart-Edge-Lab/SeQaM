#!/bin/bash -x

cd "$(dirname "$0")" || exit $?

SAVE_IMAGES="$1"
cd ../api/bin/ || exit $?
if [ -n "$SAVE_IMAGES" ]
then
  ./fast-build.sh || exit $?
fi
. config.sh
cd - || exit $?

# https://stackoverflow.com/questions/77038302/load-local-docker-images-using-docker-compose-yml
save_image_as_tar() {
  # locally: save every image mentioned in the Compose file
  if [ -n "$SAVE_IMAGES" ]
  then
    cd "$1" || exit $?
    docker save -o "$2.tar" "${@:3}" || exit $?
    gzip -f "$2.tar"
    cp ../load-image.sh .
    cd - || exit $?
  fi
}

mkdir -p "seqam-central/config"
cp "${SEQAM_CONFIG_PATH}"/* seqam-central/config || {
  err=$?
  echo did you forget to run install.sh ?
  exit $err
}
cp ../api/src/edpapi_fh_dortmund_project_emulate/static/ecdsa.pub seqam-central/config
envsubst < templates/seqam-central.template.yaml > seqam-central/docker-compose.yaml
save_image_as_tar seqam-central seqam.central "${EDPAPI_IMAGE_NAME}" "${SEQAM_COMMAND_TRANSLATOR_IMAGE_NAME}" \
  "${SEQAM_EVENT_ORCHESTRATOR_IMAGE_NAME}" "${SEQAM_EXPERIMENT_DISPATCHER_IMAGE_NAME}" || exit $?

mkdir -p "seqam-distributed-event-manager"
envsubst < templates/seqam-distributed-event-manager.template.yaml > seqam-distributed-event-manager/docker-compose.yaml
save_image_as_tar seqam-distributed-event-manager seqam-distributed-event-manager \
  "${SEQAM_DISTRIBUTED_EVENT_MANAGER_IMAGE_NAME}" || exit $?

mkdir -p "seqam-network-event-manager"
envsubst < templates/seqam-network-event-manager.template.yaml > seqam-network-event-manager/docker-compose.yaml
save_image_as_tar seqam-network-event-manager seqam-network-event-manager \
  "${SEQAM_NETWORK_EVENT_MANAGER_IMAGE_NAME}" || exit $?
