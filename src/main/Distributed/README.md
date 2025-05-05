
# Distributed Components

These components are to be run in both `ue` and `server`. Represent the element required by EDP to handle collection and events.

Collection includes traces and metrics. Traces are sent by your application once you have instrumented it. 
Metrics are host metrics collected by the distributed collector, such as cpu, memory, network, etc. These should be collected from the same environment where your application is running (container or full machine). If you dont care about these metrics, you can simplify the EDP architecture by directly pointing your OTLP endpoint in your client and server part to the Central Collector IP address. In this case, you don´t need to run the distributed collector.

## Distributed Collector
The distributed collector is mainly used to gather host metrics from the sme environment where your application is running.







## Distributed Event Manager
This component is used to receive all the calls from the central comments in EDP. It handles the insfrastructure events, such as cpu and memory load. It also triggers the distributed collector and the edge-segment application (client or server, depending of the component). For this last point, you will need to sligthly modify your application to open an active endpoint. 


## Setup possibilities

### Containerized all-in-one setup

This setup is used when all the elements of EDP are to run in the same host (not recommended). That is to say, central, distributed, network components and network emulator run in the same machine (VM or physical). 

In this case, you need to take care of serveral aspects to let EDP work in your setup configuration.

1. Make sure you limit the resources given to your client and server containers. If you don´t do so, you will not start seeing a difference when applying load events until the value is extremely high. Also, this will affect the other EDP components and your entire experiment results will fail. This is bvecause you will stress the memory and the cpu of the complete machine, but if you limit the resources the ue or server container can use, then the load cannot start eating the resources outside the ones assigned. 

2. You need to prepare a Docker image than contains your application, the distributed components and the dependencies (eg. stress_ng SW)

3. You need to modify your application to receive a trigger signal from the distributed event manager component.

4. As EDP and several distributed components run in the same machine, all will attempt to use the same port (which is not possible), then, you have to manually change the port each Distributed Event Manager Module uses in each of your distributed components. This can be done by:

* Changing the port in the Central configuration file of EDP `ScenarioConfig.json`

```json
            {
                "name":"ue002",
                "description":"test ue",
                "port":9001, #port to change
                "host":"127.0.0.1",
                "paths":[
                   {
                      "event":{
                         "endpoint":"/event/"
                      },
                      "cpu_load":{
                        "endpoint":"/event/stress/cpu_load"
                     },
                     "memory_load":{
                       "endpoint":"/event/stress/memory_load"
                    }
                   }
                ]
            }
```
* Change the port of the module in `DistEventManagerModule.py` 

```
    t3 = threading.Thread(
        target=lambda: eventManagerRESTEngine._factory_.app.run(host="0.0.0.0",
            port=9001, debug=False, use_reloader=False
        )
    )
```


5. Make sure you properly set the IP address in the EDP configuration files and that you expose the ports in the docker image to receive incomming traffic.

6. Create the Dockerfiles and Docker images per distributed element


This is how your setup should look like:

![](img/container-based_setup.png)


#### Run the EDP Distributed Components
```bash
# After you have created the respective Dockerfile and Docker images
docker run -it --name distributed_client1 -p 9001:9001 --memory="7500m" --cpus="4" distributed_client_image1  

# Notice that the the command above introduces a hard limit of resources (which are just an example) that the docker container can use.
```



### Host/VM setup

This setup means that each of your elements (ue and servers) are an individual device (physical is prefered). Here, you deploy the distributed components as agents and need to install the dependencies they use in the host machine. 

In this case, you need to take care of.


1. Run the distributed component agent.
2. You need to modify your application to receive a trigger signal from the distributed event manager component.
3. If you run the application as a container, make sure you expose the port to receive the trigger signal

This is how your setup should look like:

![](img/vm-based_setup.png)


#### Run the EDP Distributed Components
```bash
cd src/main/Distributed/Modules/EventManager/

# run the required modules individually 

python3 ./DistEventManagerModule.py

# the module will run as a flask webserver activelly listening to port 9001
```








## Debug

In case you want to run the distributed collector manually

```bash

# now we need to enable a distributed collector for testing
# it is deployed as an agent 
cd src/main/Distributed/Collector

# run the distributed collector
# you migth need to give executable permisions to the otelcol-contrib before with chmod
./otelcol-contrib --config ./config.yaml
```