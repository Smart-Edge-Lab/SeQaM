#!/bin/bash
#limit client's CPU 50% and mem 500m
docker update --cpu-period=100000 --cpu-quota=50000  clab-testnetwork-client
docker update --memory=500m --memory-swap=1g  clab-testnetwork-client

#server
docker update --cpu-period=100000 --cpu-quota=50000   clab-testnetwork-server
docker update --memory=500m --memory-swap=1g  clab-testnetwork-server

#Router1
docker update --cpu-period=100000 --cpu-quota=50000   clab-testnetwork-router1  
docker update --memory=500m --memory-swap=1g    clab-testnetwork-router1  

#Router2
docker update --cpu-period=100000 --cpu-quota=50000  clab-testnetwork-router2 
docker update --memory=500m --memory-swap=1g   clab-testnetwork-router2 
