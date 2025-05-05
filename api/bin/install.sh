#!/bin/bash

cd "$(dirname "$0")"

. install.config.sh

cd ../..

if [ -f $SEQAM_CONFIG_PATH/ModuleConfig.json ]
then
  echo Config is already installed on $SEQAM_CONFIG_PATH
else
  echo Installing configuration on $SEQAM_CONFIG_PATH
  mkdir -p "$SEQAM_CONFIG_PATH"
  cp src/main/Central/Configuration/* $SEQAM_CONFIG_PATH
fi

OPENSSH_PRIVATE_KEY=$SEQAM_CONFIG_PATH/ecdsa
OPENSSH_PUB_KEY=api/src/edpapi_fh_dortmund_project_emulate/static/ecdsa.pub

if [ -f $OPENSSH_PRIVATE_KEY ]
then
  echo Key $OPENSSH_PRIVATE_KEY already exists
else
  ssh-keygen -q -t ecdsa -N '' -f $OPENSSH_PRIVATE_KEY <<<y >/dev/null 2>&1
  chmod 600 $OPENSSH_PRIVATE_KEY
  mv ${OPENSSH_PRIVATE_KEY}.pub $OPENSSH_PUB_KEY
  echo OpenSsh key pair was generated
fi
