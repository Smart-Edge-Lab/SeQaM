#!/bin/sh
 docker exec -d clab-testnetwork-client ip link set eth1 up
 docker exec -d clab-testnetwork-client ip addr add 192.168.1.2/24 dev eth1
 docker exec -d clab-testnetwork-client ip route add 192.168.0.0/16 via 192.168.1.1 dev eth1
 

 docker exec -d clab-testnetwork-server ip link set eth1 up
 docker exec -d clab-testnetwork-server ip addr add 192.168.5.2/24 dev eth1
 docker exec -d clab-testnetwork-server ip route add 192.168.0.0/16 via 192.168.5.1 dev eth1

 docker exec -d clab-testnetwork-loadclient ip link set eth1 up
 docker exec -d clab-testnetwork-loadclient ip addr add 192.168.4.2/24 dev eth1
 docker exec -d clab-testnetwork-loadclient ip route add 192.168.0.0/16 via 192.168.4.1 dev eth1

 docker exec -d clab-testnetwork-loadserver ip link set eth1 up
 docker exec -d clab-testnetwork-loadserver ip addr add 192.168.3.2/24 dev eth1
 docker exec -d clab-testnetwork-loadserver ip route add 192.168.0.0/16 via 192.168.3.1 dev eth1




 

