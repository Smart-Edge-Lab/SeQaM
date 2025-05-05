#!/bin/bash -x

cd "$(dirname "$0")"

cd ../../bin/
. config.sh
cd -

mkdir -p /var/snap/microk8s/current/args/certs.d/"$PRIVATE_DOCKER_REGISTRY"
envsubst < _var_snap_microk8s_current_args_certs.d_REPOSITORY_hosts.toml > /var/snap/microk8s/current/args/certs.d/"$PRIVATE_DOCKER_REGISTRY"/hosts.toml

microk8s stop
microk8s start
