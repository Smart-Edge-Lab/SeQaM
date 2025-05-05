#!/bin/bash -x

DEPLOY_DIR="/tmp/deploy"
mkdir -p "$DEPLOY_DIR"
cd "$DEPLOY_DIR"
git clone /home/emulate/bare-repos/emulate-edge-diagnostics-platform.git
git checkout dev
./api/bin/build.sh
./api/deploy/k8s/deploy.sh
