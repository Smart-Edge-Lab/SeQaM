#!/bin/bash -x

cd "$(dirname "$0")" || exit $?
export PRIVATE_DOCKER_REGISTRY=172.22.174.190:5000
DAEMON_SETTINGS_FILE=/etc/docker/daemon.json

if [ -f $DAEMON_SETTINGS_FILE ]; then
  echo "File $DAEMON_SETTINGS_FILE already exists."
else
  envsubst < _etc_docker_daemon.json > $DAEMON_SETTINGS_FILE || {
    err=$?
    echo "Sorry, but you have no permissions to write to $DAEMON_SETTINGS_FILE"
    echo "Try with sudo"
    exit $err
  }
  service docker restart
fi
