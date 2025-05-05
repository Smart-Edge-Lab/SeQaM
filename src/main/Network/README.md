# Network EDP Components

The EDP components to trigger events in the network emulator (as for now, only containerlab), are to be deployed as an agent. That means, they must directly run in the same host where the emulator is deployed. This is mandatory, as to trigger the events, EDP Network agent will require to interact with the SW components that represent the network devices.

After you download the repo in the host, you need to execute the `NetworkEventManagerModule.py` script from the Network components.


## Containerlab

If you are using EDP to trigger events on containerlab, you need to make sure you follow these rules:

1) The name of the load clients containers is restricted to `loadclient(number)`, where number must match the number of the router where the load client is connected to. For example `loadclient1` must be connected to `router1`, `loadclient25` to `router25` and so on. This is not required for load servers.

```sh
network_load src_device_type:router src_device_name:router1 interface:eth2 load:5 time:5s
```

This EDP command will internally invoke a command in the `loadclient1` container to run a client to repeatedly send a 5MB file over the interface `eth2` of `router1` for `5` seconds.


2) Note that currently, the `loadclient` can only generate loads of 1MB, 2MB, 5MB, 10MB, 15MB, 20MB, 30MB, 40MB and 50MB. That means the load argument must only be one of the above file sizes. If you dont do so, the client running within the `loadclient` will crash.

3) If you plan to have several loaders in different links of the network, you need to manually create them. While doing so, remember to modify the port (and maybe IP) of each of the `cli.py` and `sockser.py` you add to your network scenario. After, create a docker image for each `loadclient` and `loadserver` respectivelly and declare this links in the containerlab configuration file.

4) If you change the name of your containerlab configuration yml file, you will have to also change the `manageInterface.sh` and `manageLoad.sh` as they require the name of the container, which in turn depends on the network scenario name. Make sure with `docker ps` that the name matches before generating any event.

```sh
#For example in manageLoad.sh:
docker exec clab-testnetwork-loadclient$loadclient python3 cli.py  "$load.jpg" $time_in_seconds
#testnetwork is the name of the network scenario declared
```

***Note:***  As for now, this is not to be automated in this release and thus, network scenario configuration is your task.
