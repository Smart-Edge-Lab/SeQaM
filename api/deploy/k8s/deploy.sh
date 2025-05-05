#!/bin/bash -x

cd "$(dirname "$0")"

cd ../../bin/
. config.sh
cd -

envsubst < deploy.yaml | microk8s kubectl apply -f -
microk8s kubectl get deployments
microk8s kubectl get pods

microk8s kubectl apply -f service.yaml
microk8s kubectl get services
