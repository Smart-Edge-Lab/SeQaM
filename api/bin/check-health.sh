#!/bin/bash

RED='\033[0;31m'
NC='\033[0m' # No Color

check_health() {
  h=$(curl -s -o /dev/null -w "%{http_code}" localhost:$2/health)
  if [ "$h" == 200 ]
  then
    echo -e "\U2705 $1 is healthy"
  else
    echo -e "${RED}$1 outputs $h, so it is not healthy${NC}"
    docker logs $1
    exit 1
  fi
}

check_central_components_health() {
  check_health build-edpapi-1 ${API_PORT}
  check_health build-seqam-command-translator-1 ${COMMAND_TRANSLATOR_PORT}
  check_health build-seqam-event-orchestrator-1 ${EVENT_ORCHESTRATOR_PORT}
  check_health build-seqam-experiment-dispatcher-1 ${EXPERIMENT_DISPATCHER_PORT}
}
