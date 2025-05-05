
# Central Components

The central components represent the core of EDP and are to be deployed isolated from the distributed and network components.



## Main Collector
EDP uses SigNoz as the general instrument for collection. The data is gathered using OpenTelemetry from the distributed components and sent to the distributed collectors. From there, each distributed collector sends to the central collector, wich in turn stores the spans, logs and metrics in the clickhouse database. 


## Console
This component is used to interact with EDP, must be run individually. Commands are sent to the other components via the console. In this version, there is no console feedback when a input is not properly sent, therefore, please be aware to double check the command before passing it to the system. The module that receives it, do implement some validation, but does not return the message to the console (yet)

## Command Translator
This component receives the commands from both, the console or the experiment dispatcher modules and translates them into a readable format for the programm (JSON). The data is furhter sent to the event orchestrator module. The validations of a command is done here. 

## Event Orchestrator
This component is in charge of generating all the events within EDP. It manages both, internal events (between central components) and distributed events (from central components to distributed components). Resquests are received and sent via REST requests.

## Experiment Dispatcher
This component helps with the creation of experiments. An experiment is a determined set of actions that occur in a determined order and at a specific time. 
The module reads the events described in `ExperimentConfig.json` and executes them in sequential manner.

More details on how to create experiments are described after. 

## Data Manager

To retrieve the data collected by EP and stored in the database, it is requiered to query clickhouse. You can do it on your owun using a clickhouse client, but EDP also provides some simple methods to get information about spans, cpu and memory consumption.

To do so, you can use the `DBclient` class, create an object of it and include it in your programm. Finally, call the provided methods according to your needs. You can also use the `send_generic_query` method to send your custom queries to clickhouse.

*Note: when getting the metrics data, you will need to specify the hostname. This is the name you see in the terminal for example, so if you use a container all-in-one setup approach, make sure you know the hostname of it to be able to retrieve the data with the methods.*

# Commands implemented

Commands can be relatively easy modified in the scripts, but its better if we consider them as hard-coded. A command represents an action to perform in any of the EDP components (central, distributed, network). The commands can be triggered from the console or automatically invoked by the experiment dispatcher module. 

In general, a command is formed by:

* **keyword:** represents the action itself that the command invokes
* **src_device_type:** the type of the device where the action is to be executed, can be `ue`, `server`, `router`
* **src_device_name:** the name of the device where the action is to be executed. This name must match the name you have configured in containerlab and also the one in the `ScenarioConfig.json` file. This is not required for `router` as they work specially depending on the network emulation environment.
* **dst_device_type:** the name of the device with which the src device will start interacting, can be `ue`, `server`, `router`. (Not all commands require this)
* **dst_device_name:** the name of the device with which the src device will start interacting. This name must match the name you have configured in containerlab and also the one in the `ScenarioConfig.json` file. (Not all commands require this)

#### Connect device (not implemented)

Connects a ue device to a given PoA or server in the network.

```bash
connect src_device_type:ue src_device_name:ue001 dst_device_type:server dst_device_name:svr102
```


#### Disconnect device (not implemented)

Disconnects a ue device from a given PoA or server in the network.

```bash
disconnect src_device_type:ue src_device_name:ue001 dst_device_type:server dst_device_name:svr102
```

#### Migrate device (not implemented)

migrates a ue device to a different PoA in the network, emulating a mobility event. Usefull in hand-over scenarios.

```bash
migrate src_device_type:ue src_device_name:ue001 dst_device_type:server dst_device_name:svr102
```

#### CPU load

Generates CPU load in a given device (ue or server)

```bash
cpu_load src_device_type:ue src_device_name:ue001 cores:5 load:20 time:60s
```
To generate the load, EDP uses stress_ng, which must run in the distributed components. This command uses also specific parameters:

* **cores:** the number of cores where the load is to be generated. If 0, all cores in the device will be stressed
* **load:** the amount of load in percentage to be put in the cores
* **time:** the time the event will endure. As for now, the event cannot be manually stopped, so it automatically stops after the defined time has elapsed. Be aware of this when generating your experiments. You need to do the math and calculate when the invoked event is to be finished to trigger a new one of this type. The time units is finally defined at the end of the number and can be in seconds `s`, minutes `m`, hours `h`.


#### Memory load

Generates memory load in a given device (ue or server). Please note that memory load, also will generate CPU load, due to the manner computers work.

```bash
memory_load src_device_type:ue src_device_name:ue001 workers:5 load:20 time:10s
```
To generate the load, EDP uses stress_ng, which must run in the distributed components. This command uses also specific parameters:

* **workers:** the number of workers used to generate load
* **load:** the amount of load in MB to generate
* **time:** the time the event will endure. As for now, the event cannot be manually stopped, so it automatically stops after the defined time has elapsed. Be aware of this when generating your experiments. You need to do the math and calculate when the invoked event is to be finished to trigger a new one of this type. The time units is finally defined at the end of the number and can be in seconds `s`, minutes `m`, hours `h`.

#### Network bandwidth modification

Triggers a bandwidth change in one of the links in your network scenario. Works for Containerlab and the specific laboratory deployment scenario configurated for testing. It can be used to simulate network traffic in a very rustic manner.

```bash
network_bandwidth src_device_type:router src_device_name:router1 interface:eth2 bandwidth:20 time:30s
```

* **interface:** the interface name of the origin router. Must match the name configured in the containerlab scenario
* **bandwidth:** the new bandwidth of the link in Mbps
* **time:** the time the event will endure. As for now, the event cannot be manually stopped, so it automatically stops after the defined time has elapsed. Be aware of this when generating your experiments. You need to do the math and calculate when the invoked event is to be finished to trigger a new one of this type. The time units is finally defined at the end of the number and can be in seconds `s`, minutes `m`, hours `h`.

#### Network traffic generation

Generates defined ammount of traffic in a specific link in your network scenario. Only works for containerlab.
This method uses a client and a server that must be attached to both sides of the link you want to stress with network traffic. The command activates the client to start sending a specific ammount of load to the server located in the other side. You need to manually attach and configure this components for your experiments. More information is given in the Network components README.

```bash
network_load src_device_type:router src_device_name:router1 interface:eth2 load:5 time:5s
```

* **interface:** the interface name of the origin router. Must match the name configured in the containerlab scenario
* **load:** the continous load to be sent in the link.
* **time:** the time the event will endure. As for now, the event cannot be manually stopped, so it automatically stops after the defined time has elapsed. Be aware of this when generating your experiments. You need to do the math and calculate when the invoked event is to be finished to trigger a new one of this type. The time units is finally defined at the end of the number and can be in seconds `s`, minutes `m`, hours `h`.


#### Start module

As for now, only implemented to generate a trigger to the experiment dispatcher module to start executing the experiment defined in the `ExperimentConfig.json` file.

```bash
start_module module:experiment_dispatcher
```

* **module:** the name of the EDP module you want to start. As for now, only experiment_dispatcher is supported.

# Deploying the platform


### Deploying the Platform Collector

This is used to run the main collector and the database. You can run this components in a separate machine to improve performance. 

At any case, make sure you update the IP address of the distributed exporters in their configuration file to point the IP of the machine where the main collector is running.

#### Running the main collector
```bash
cd src/main/Collector/deploy/docker/clickhouse-setup

# This will enable the general collector (Signoz + Clickhouse)
docker compose -f docker-compose.yaml up -d
```

#### Stop the main collector
```bash
# Stop the central collector once you are done
cd src/main/Collector/deploy/docker/clickhouse-setup
docker compose -f docker-compose.yaml down -v
```

### Deploying the Platform Components as docker


This deployment type is the easiest way to get started with the platform when running all the components in the same machine. The main collector can be still separated as it is a completely isolated unit.

The IP addresses and ports are to be taken as enviromental variables. Therefore, you need to configure them just for the first time 

#### Install the platform

```bash
# Configure the images
cd ./build

# Configure the enviromental variables to update the IP addresses and ports of the components
# The IP adress should be the IP of the machine, do not use localhost as this is to be taken by the containers.
nano .env

# Give execution permits
chmod +x deploy.sh
chmod +x destroy.sh

# Build the docker images
docker-compose build
```

#### Run the platform

```bash
# Run the platform components
./deploy.sh

# Each module will run as a webserver activelly listening to some port in the background. The console should automatically appear.

# To leave the console you can type exit
```

#### Stop the platform
```bash
# Stop the components
./destroy.sh
```

### Deploying the Platform Components as individual Agents

For this deployment type, you have to properly change the IP address and ports of the distributed components in the `ModuleConfig.json`. This deployment can be use if for some reason you want to run each component in a separate machine. Then you can only run each individual component as an agent. The main collector can be still separated as it is a completely isolated unit.

#### Install the platform

```bash
# You need to install some dependencies to enable the APIs, instrument your applications, and access the data from the database. 
pip install -r requirements.txt
```

#### Run the platform

```bash
# Run the modules individually 
cd ./Modules
python3 ./Console/ConsoleModule.py
python3 ./CommandTranslator/CommandTranslatorModule.py
python3 ./EventOrchestrator/EventOrchestratorModule.py

# Each module will run as a webserver activelly listening to some port

# If you aim to execute an experiment, you will also need to run the dispatcher
python3 ./experiment_dispatcher/ExperimentDispatcherModule.py -m trigger
#TODO: There is a typo in the folder name. dependencies must also be changed
```

#### Stop the platform
```bash
# Stop each one of the agents individually
```


## Run Events

Once the console module is active, you will see in the terminal the text `EDP >>`. This means the console is ready to receive input.

You can simply check if the module is working by typing a mirror command


```bash
EDP >> console hello_edp
```
This should print back your message.

Now, you can start sending the commands you desire. If you wanna track if they are properly implemented, open the terminal of the event orchestrator module. There you will see the logs.

```bash
EDP >> cpu_load src_device_type:ue src_device_name:ue001 cores:0 load:80 time:60s

# To leave the console you can type exit
```

## Run an Experiment

Before running, there are a set of conditions you need to make sure your set-up satisfies.


### Creating an experiment file

Experiments consist of a set of commands triggered at a certain point of time. These are configured in the `ExperimentConfig.json`. The configuration is pretty simple and must be sequential. As for now, it is not possible to generate two events at the exact same time. However, the experiment dispatcher module aims to dispatch events as fast as possible, and analyzes if a new event is to be dispatched each 2ms. It creates a thread per event request, so they do not block the queue. At any case, due to processing time, it is better if you try to dispatch two consecutive events with more than 5ms of difference. 

The following file shows an example with some commands

```json
{
  "experiment_name": "test_case_1",
  "eventList": [
    {
      "command": "cpu_load src_device_type:ue src_device_name:ue001 cores:5 load:20 time:60s",
      "executionTime": 8000
    },
    {
      "command": "memory_load src_device_type:ue src_device_name:ue001 workers:5 load:20 time:10s",
      "executionTime": 10500
    },
    {
      "command": "network_load src_device_type:router src_device_name:router1 interface:eth2 load:5 time:5s",
      "executionTime": 10510
    },
    {
      "command": "network_bandwidth src_device_type:router src_device_name:router1 interface:eth2 bandwidth:20 time:30s",
      "executionTime": 11500
    },
    {
      "command": "exit",
      "executionTime": 21000
    }
  ]
}
```
The `experiment_name` parameter is used to generate a file that contains the set of events performed in the experiment. It stores the command and the UTC time in unix format (microseconds) at which it was executed. This information can be used when you want to retrieve the data from the database for post analysis. Timestamps is the only way we provide now to get your data. The recommendation would be that you name this experiment the same as your service-name when instrumenting your application. Also, remember to change it each time you run a new experiment.

The `exit` command destroys the experiment dispatcher once all events have been dispatched.

The `executionTime` is set in milliseconds and start to count from the time the trigger signal is sent to the experiment dispatcher module. Be aware that if you want to trigger two events one after the other finishes (for example CPU load of 50% starting at t0 and finishing at t1, followed by a CPU load of 80% starting at t1), you have to consider adding up the duration of the first event to the `executionTime` of the second.

Example:

```json
   {
      "command": "cpu_load src_device_type:server src_device_name:svr101 cores:0 load:50 time:10s",
      "executionTime": 100
    },
    {
      "command": "cpu_load src_device_type:server src_device_name:svr101 cores:0 load:80 time:60s",
      "executionTime": 10105
    }
```

Here, as:
- t0=100
- duration of the first event 10s (10000ms). Therefore, the time when the event will finish is t1= 10100
- considering a buffer of 5ms for the next event
the execution time of the second event is configured as 10105.

### Start the experiment 

Here are some points you need to consider before running an experiment:

1. if you use the emulated deployment scenario, Containerlab is properly configured, up and running (Refer to the Network README). If you use the laboratory deployment scenario, all conections should be made and tested and IP addresses shoud be updated in the `ScenarioConfig.json` file.
2. Your edge application shares the same enviroment with the distributed components (namely container or physical device)
3. The distributed components are up and running (Refer to the Distributed README)
4. The traffic generators have been attached to your scenario and are up and running (Refer to the Network README)
5. The device names are properly set in the `ScenarioConfig.json` file and match with the ones in containerlab (if applies) and in the commands described in the `ExperimentConfig.json`

7. You have created/modified the `ExperimentConfig.json` accordingly.


```bash
# The experiment dispatcher waits for a trigger event from the console to start. 

# From the console:
EDP>> start_module module:experiment_dispatcher

# Note: When you run multiple experiments, make sure you change the name of each of them, so you dont lose the time information as the file will be rewriten.
```

## Creating on-demand events in runtime

If you need to create EDP events based on some custom events your analysis algorithm generates (eg. triggering a migration when you detect a certain server is about to crash), you will need to send a on-demand POST request to the command translator module with the command you would like to execute. 


```bash
curl -X POST http://IP_address:8001/translate \
     -H "Content-Type: text/plain" \
     --data "migrate src_device_type:ue src_device_name:ue002 dst_device_type:server dst_device_name:svr102"
```

Here you can implement your own logic to determine what command to execute in EDP and when.




# Customizing the Platform

### Module configuration
The platform can be easily configured by modifying the `ModuleConfig.json` file. IP adresses and ports can be configured in this file when using the agent deployment method or by modifying the .env file when using the dockerized version (More details in the Run section).

Each module is represented as a JSON with the following parameters:

* **name:** is the name of the module, this is a hardcoded parameter, therefore it is not worth changing it, as other modules use this name to generate the endpoint to which send their request from this file
* description: a small and simple description of each module
* **port:** the port the module listens to when it is deployed. This can be configured according to your needs. It is obtained from the Enviroment Variables when using the dockerized version. The system will automatically retrieve the port from here, so there is no problem if you prefer to change it.
* **host:** in case the platform components are distributed in different physicall devices, you can add their IP address here, so all the other modules can communicate with it when required. If all are in the same host, then configure it as `127.0.0.1`. Do NOT use `localhost` as DNS resolution takes unnecessary time. When using the dockerized version, the host IP is obtained from the Enviroment Variables.
* **paths:** a path is characterized by an action and an edpoint. Actions are hardcoded elements that are used by the other components of the platform to make a call to a certain action within the module. These values should not be changed, but you are free to add new ones if you need. The endpoint can be configured according to your criteria, as the components read this value before making the REST request. However, if not required, just leave them as they are set.

### Collection configuration

OpenTelemetry collector works in batches, that is to say, that the information is collected but not exported until any of the conditions of the batch is full. There are two parameters, datasize and timeout, when any of them is fullfilled, the data is forwarded to the exporter. Is you need to get this information fast in the database, you need to configure these parameters in both, the central and distributed collector(s). For the central collector, look the `otel-collector-config.yaml` file in `src/main/Central/Collector/deploy/docker/clickhouse-setup`. For the distributed collectors look for the `config.yaml` file in `src/main/Distributed/Collector`. 


```bash
processors:
  batch:
    send_batch_size: 100
    send_batch_max_size: 110
    timeout: 50ms
```
