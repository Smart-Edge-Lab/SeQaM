# SeQaM (Service Quality Management) Platform Specification

## Intro

SeQaM Platform should be useful for conducting experiments with client-server application response time (end-to-end latency) under different loads. The results of the experiments should help getting insights on how to reduce this response time for mission-critical applications.


## Architecture

SeQaM should consist of eight components:

1. [**Command Translator**](#1-command-translator)
2. [**Event Orchestrator**](#2-event-orchestrator)
3. [**Experiment Dispatcher**](#3-experiment-dispatcher)
4. [**Web Frontend Console**](#4-web-frontend-console)
5. [**Distributed Event Manager Agent**](#5-distributed-event-manager-agent)
6. [**Network Event Manager Agent**](#6-network-event-manager-agent)
7. [**Agentless (ssh) Manager**](#7-agentless-ssh-manager)
8. [**API**](#8-api)

All components, except of [**Agentless (ssh) Manager**](#7-agentless-ssh-manager), should have a [**/health**](#health-api) endpoint responding on http GET requests with http **200 OK**. This endpoint can be used as a health check to ensure that specific component is up and running.

The health of the [**Agentless (ssh) Manager**](#7-agentless-ssh-manager) can be checked with a try to execute some basic shell command like **echo**.


## Synopsis

The following conventions apply to the SYNOPSIS section and can be used as a guide in other sections. We [borrow it from gnu man page](https://gitlab.com/man-db/man-db/-/blob/main/man/man1/man.man1#L150):

**bold text**     ---     type exactly as shown.

*italic text*     ---   replace with appropriate argument.

\[**abc**\]      ---       any or all arguments within \[ \] are optional.

*argument* ...    ---   argument is repeatable.

\[*expression*\] ... ---  entire expression within \[ \] is repeatable.


## 1. Command Translator

### Command Translator functional requirements

The **Command Translator** should have an endpoint accepting a [plain text input](#command-translator-input-payload) using http POST method. The plain text input can be accompanied by an optional **ExperimentContext** header value.

This plain text input should be converted to [output json payload](#command-translator-output-payload) and posted towards the [**Event Orchestrator**](#2-event-orchestrator).

It also should carry the optional **ExperimentContext** input header value in the **experiment_context** field of the [output payload](#command-translator-output-payload).

The **Command Translator** should respond immediately with http **200 OK** regardless of did it deliver or not the output payload to the [**Event Orchestrator**](#2-event-orchestrator).

In case of unsuccessful delivery, the **Command Translator** should send a POST request with an error message to the [**API**](#broadcast-to-all-web-frontend-console-sessions-api). The latter should broadcast the message to all open [**Web Frontend Console**](#4-web-frontend-console) sessions.

The **Command Translator** should resolve the urls of the target [**Event Orchestrator**](#2-event-orchestrator) and [**API**](#8-api) endpoints from [**Module Configuration Files**](#module-configuration-files).

### Command Translator input payload

*action* \[ *arg-name*:*arg-value* \] ...

where any or all *arg-values* can be optionally quoted with single or double quotes; these optional quotes become mandatory if a value contains whitespaces.

**ssh** action supports a shorten form of the above format:

**ssh** *src_device_type* *src_device_name* \[*command*\] ...

where *command* can readily contain any number of whitespaces without the requirement to be quoted,

that is equivalent to

**ssh** **src_device_type**:*src_device_type* **src_device_name**:*src_device_name* **command**:**"**\[*command*\] ...**"**

where \[*command*\] should be quoted with either double or single quotes if it contains whitespaces.

### Command Translator output payload

```json
{
  "action": "*action*",
  "arg1-name": "arg1-value",
  "arg2-name": "arg2-value",
  ...,
  "argN-name": "argN-value",
  "experiment_context": "*optional ExperimentContext header value*"
}
```

where *action* is the first term in the plain text input, *argX-name*, *argX-value* are the colon(**:**)-separated name-value pairs.

### Module Configuration Files

The **Module Configuration Files** should consist of a **ModuleConfig.json** file, an **env** file and an auto-generated ssh private key.

#### ModuleConfig.json

The format of the **ModuleConfig.json** file is as follows:

```json
{
  "modules": [
    {
          "*module-name*":{
             "name":"*Human-readable module name*",
             "description":"*Short human-readable description of the module functionality*",
             "port": *port*,
             "host": "*host*",
             "paths":[
                {
                   "*action*":{
                      "endpoint":"/*path*/"
                   },
                  ...
                }
             ]
          }
       },
    ...
  ]
}
```

where *module-name* is a machine-friendly module identifier in latin letters without whitespaces like **command_translator**, **event_orchestrator** or **experiment_dispatcher**;
*Human-readable module name* and *Short human-readable description of the module functionality* are any texts in any human language with any number of white spaces;
*port* is an integer port number being exposed by the appropriate component;
The *host* can be specified by hostname, IPv4 literal, or IPv6 literal;
*action* is the action name reflecting the one in the [input payload](#command-translator-input-payload);
*path* is the url path that should handle the *action*.

#### env

The format of the **env** file is as follows:

```shell
ENVIRONMENT_VARIABLE1_NAME=ENVIRONMENT_VARIABLE1_VALUE
ENVIRONMENT_VARIABLE2_NAME=ENVIRONMENT_VARIABLE2_VALUE
...
ENVIRONMENT_VARIABLEN_NAME=ENVIRONMENT_VARIABLEN_VALUE
```

The environment variables declared in the **env** file can be used in any json configuration file including **ModuleConfig.json** as follows:

```json
$ENVIRONMENT_VARIABLE_NAME | *default-value*
```
where **\$ENVIRONMENT\_VARIABLE\_NAME** is the environment variable name prefixed with the **\$** sign;
*default-value* is the default value that should be used in case when the environment variable is not declared or is empty.

#### Examples

##### ModuleConfig.json example

```json
{
  "modules": [
    {
      "event_orchestrator": {
        "name": "Event Orchestrator",
        "description": "Get event requests",
        "port": $EVENT_ORCHESTRATOR_PORT | 8002,
        "host": "$EVENT_ORCHESTRATOR_HOST | 172.22.174.157",
        "paths": [
          {
            "event": {
              "endpoint": "/event/"
            }
          }
        ]
      }
    },
    ...
  ]
}
```

##### env example

```shell
API_HOST="172.22.229.149"
API_PORT=8000
EVENT_ORCHESTRATOR_HOST="172.22.229.149"
EVENT_ORCHESTRATOR_PORT=8012
```

## 2. Event Orchestrator

### Event Orchestrator functional requirements

The **Event Orchestrator** should have an endpoint accepting the incoming POST requests with [json payloads](#command-translator-input-payload) and redirect them to [**Distributed Event Manager Agent**](#5-distributed-event-manager-agent), [**Network Event Manager Agent**](#6-network-event-manager-agent), or [**Agentless (ssh) Manager**](#7-agentless-ssh-manager).

It should support json payload equivalents to the following plain-text actions (see [input](#command-translator-input-payload) and [output](#command-translator-output-payload)):

### Hello action

[Synopsis](#synopsis):

**hello**

is a health-check action that should propagate from [**Command Translator**](#1-command-translator) to [**Event Orchestrator**](#2-event-orchestrator) and broadcast all open [**Web Frontend Console**](#4-web-frontend-console) sessions that **Event Orchestrator** is reachable.

### Cpu load action

[Synopsis](#synopsis):

**cpu_load** **time**:*duration* **load**:*load-value* **src_device_type**:*src_device_type* **src_device_name**:*src_device_name* **cores**:*number-of-cores* \[
**comment**:"*any optional human-readable comment*"
**mode**:*stress-mode*
**random_seed**:*random-seed*
**load_min**:*load-min*
**load_max**:*load-max*
**load_step**:*load-step*
**time_step**:*time-step*
\]

where *duration* expected to be suffixed with time-unit: **s** for seconds, **m** for minutes, **h** for hours, **d** for days, or **y** for years;
*load-value* --- stress degree in percents;
*src_device_type* --- type of the device that should be stressed;
*src_device_name* --- name of the device that should be stressed;
*number-of-cores* --- number of CPU cores that should be used in the stress;
**comment** can be useful to attach some descriptive text to the experiment action;  

#### Dynamic-load options

*stress-mode* is an optional string that can be either **stat** for static (default), **rand** for random, **inc** for increasing or **dec** for decreasing stress mode;

*random-seed* is an optional integer value used only in **rand** **mode** and should allow reproducing the same random load from one experiment to another;

*load-min* is an optional integer minimal value of the load (defaults to zero), so that **inc** **mode** should start from that value, **rand** **mode** should not go below that value, **dec** **mode** should decrease load until that value;

*load-max* is an optional integer maximal value of the load (defaults to one hundred), so that **dec** **mode** should start from that value, **rand** **mode** should not go above that value, **inc** **mode** should increase load until that value;

*load-step* is an optional integer value (defaults to 1) that should be added in the **inc** **mode** or subtracted in the **dec** **mode** on every iteration;

*time-step* is an optional integer value (defaults to 1) that represents the duration of every iteration; the time-unit is equal to that used in the *duration* argument.

The action payload should be redirected using http POST to the [**Distributed Event Manager Agent**](#5-distributed-event-manager-agent) endpoint, whose url should be resolved from the [**Scenario Configuration File**](#scenario-configuration-file) by specified *src_device_type* and *src_device_name*.

### Scenario Configuration File

The **Scenario Configuration File** should have the following format:

```json
{
  "distributed": {
    "*device_type*": [
      {
        "name": "*device_name*",
        "description": "*human-readable device description*",
        "host": "*host*",
        "port": *agent-port*,
        "ssh_port": *ssh-daemon-port*,
        "ssh_user": "*ssh-username*",
        "paths": [
          {
            "*action*": {
              "endpoint": "/*path*/"
            },
            ...
          }
        ]
      },
      ...
    ]
  }
}
```

where *device_type* is the name of device category; it should represent either *src_device_type* or *dst_device_type*; example device types are **ue** (user equipment), **server**, and **router**; 

*device_name* is the computer-friendly identifier of the device, something like the hostname; example *device_names* are **ue001**, **ue002**, **svr101**, **svr102**, **ntw_agent**; the device name should be unique within every *device_type* set;

*human-readable device description* is an optional info about the device;

the *host* can be specified by hostname, IPv4 literal, or IPv6 literal;

*agent-port* is an optional integer port where either [**Distributed Event Manager Agent**](#5-distributed-event-manager-agent) or [**Network Event Manager Agent**](#6-network-event-manager-agent) should be listening on; it is optional because the host can alternatively be controlled using an [agentless ssh](#7-agentless-ssh-manager) approach;

*ssh-daemon-port* is an optional integer port (defaults to 22) where an [ssh daemon](#7-agentless-ssh-manager) should be listening on; it is optional because the host can alternatively be controlled using [agents](#5-distributed-event-manager-agent);

*ssh-username* is useful for the [agentless ssh](#7-agentless-ssh-manager) approach and denotes the name of the user under which the bash commands should be executed; 

*action* is an action name like [cpu load](#cpu-load-action), [network load](#network-load-action), [start module](#start-module-action) or [stop module](#stop-module-action);

*path* is an endpoint url path that should handle the *action*.

### Network load action

[Synopsis](#synopsis):

**network_load** **time**:*duration* **load**:*load-value* **src_device_type**:*src_device_type* **src_device_name**:*src_device_name* **dst_device_type**:*dst_device_type* **dst_device_name**:*dst_device_name* \[
**comment**:"*any optional human-readable comment*"
**mode**:*stress-mode*
**random_seed**:*random-seed*
**load_min**:*load-min*
**load_max**:*load-max*
**load_step**:*load-step*
**time_step**:*time-step*
\]

where *duration* means the same as in the [**Cpu load action**](#cpu-load-action).

*load-value* --- stress degree in Megabytes;

*src_device_type*, *src_device_name* and *dst_device_type*, *dst_device_name* mean the sender (source) and receiver (destination) devices, respectively, and the specified amount of network traffic should flow from the source to the destination; the IP addresses of these source and destination devices should be resolved from the [**Scenario Configuration File**](#scenario-configuration-file);

**comment**, **mode**, **random_seed**, **load_min**, **load_max**, **load_step** and **time_step** have the same meaning and purpose as in [Cpu load action](#cpu-load-action).

The action payload should be enriched with the destination device IP address from the [**Scenario Configuration File**](#scenario-configuration-file) by specified *dst_device_type*, *dst_device_name* and redirected using http POST to the [**Network Event Manager Agent**](#6-network-event-manager-agent) endpoint, whose url is resolved from the same [**Scenario Configuration File**](#scenario-configuration-file) by specified *src_device_type* and *src_device_name*.

### Start module action

[Synopsis](#synopsis):

**start_module** **module**:*module*

where *module* is the module name from [**Module Configuration Files**](#module-configuration-files).

The action payload should be extended with **"start": "True"** field and sent towards the *start* endpoint url configured in the [**Module Configuration Files**](#module-configuration-files) for the appropriate module.

### Stop module action

[Synopsis](#synopsis):

**stop_module** **module**:*module*

where *module* is the same as in the [Start module action](#start-module-action).

The action payload should be extended with **"start": "False"** field and sent towards the *stop* endpoint url configured in the [**Module Configuration Files**](#module-configuration-files) for the appropriate module.

### Ssh action

[Synopsis](#synopsis):

**ssh** *src_device_type* *src_device_name* \[*command*\] ...

where *src_device_type* --- type of the device that should execute the *command*;
*src_device_name* --- name of the device that should execute the *command*.

The action should execute the given *command* on the device specified by *src_device_type* and *src_device_name* using an [ssh daemon](#7-agentless-ssh-manager). The host, port and username, that should be used to connect to the ssh daemon on the device, are resolved from the [**Scenario Configuration File**](#scenario-configuration-file).

The ssh private key should be saved among the [**Module Configuration Files**](#module-configuration-files).

The ssh public key should be accessible using an arbitrary [url on the **API**](#get-ssh-public-key-api).


## 3. Experiment Dispatcher

### Experiment Dispatcher functional requirements

The **Experiment Dispatcher** should expose an endpoint accepting POST requests "*start*" and "*stop*". The url paths of these requests should be put into the [**Module Configuration file**](#moduleconfigjson).

#### Experiment Dispatcher start action

When the *start* request comes, it should read the [**Experiment Configuration file**](#experiment-configuration-file) and send actions, that are stated there, to the [**Command Translator**](#1-command-translator). The actions should be sent in the order and time as they are specified in the [**Experiment Configuration file**](#experiment-configuration-file). 

The *experiment-name* from the [**Experiment Configuration File**](#experiment-configuration-file) should be sent towards **OTLP Collector** as a name of the parent span of the experiment trace (*experiment* span).
The host running the **OTLP Collector** should be resolved from the [**env Module Configuration file**](#env) like the following:

```shell
OTLP_URL=172.22.229.149:4317
```

Every **command** in the [**Experiment Configuration File**](#experiment-configuration-file) should be sent to the [**Command Translator**](#1-command-translator) with the **ExperimentContext** header carrying the parent *experiment* span context.

#### Experiment Configuration file

The **Experiment Configuration file** should specify the *experiment-name* and list a sequence of **command** -- **executionTime** pairs. Where **executionTime** is the *time* (in milliseconds since the start of the experiment) when the **command** should be sent towards the [**Command Translator**](#1-command-translator); the **command** should be specified in the form of plain text as described in the [**Command Translator** input payload](#command-translator-input-payload).

The **Experiment Configuration file** should follow the below format:

```json
{
  "experiment_name": "*experiment-name*",
  "eventList": [
    {
      "command": "*action* [ *arg-name*:*arg-value* ] ...",
      "executionTime": *time*
    },
    ...
  ]
}
```

The **commands** in the **eventList** can have **executionTimes** and *durations* (see [cpu load](#cpu-load-action) and [network load](#network-load-action)) that overlap each other. So several commands can be running simultaneously.

#### Experiment Dispatcher stop action

When the *stop* request comes, the **Experiment Dispatcher** should stop sending the actions listed in the [**Experiment Configuration file**](#experiment-configuration-file).


## 4. Web Frontend Console

### Web Frontend Console functional requirements

The **Web Frontend Console** should provide user with a GUI where (s)he should be able to type the [plain-text commands](#command-translator-input-payload), send them to the [**Command Translator**](#1-command-translator), and read the status and error messages from the components.

It should resolve the [**Command Translator**](#1-command-translator) host and port from the [**Module Configuration file**](#moduleconfigjson).


## 5. Distributed Event Manager Agent

### Distributed Event Manager Agent functional requirements

The **Distributed Event Manager Agent** should expose an endpoint accepting a json payload equivalent to [Cpu load action](#cpu-load-action). The mapping between this plain text representation to json should be done as described [here](#command-translator-output-payload).

It should stress the specified number of Cpu *cores* to the specified *load* percentage on the node where the agent is being executed during the specified *duration*. The dynamic load behavior should be implemented as described in the [Cpu load action](#cpu-load-action).

The stress action should extract the parent *experiment* span context from the **experiment_context** field and submit the action span to the **OTLP Collector** as a child span.
The host running the **OTLP Collector** should be resolved from the [**env Module Configuration file**](#env) like [here](#experiment-dispatcher-start-action).


## 6. Network Event Manager Agent

### Network Event Manager Agent functional requirements

The **Network Event Manager Agent** should expose an endpoint accepting a json payload equivalent to [Network load action](#network-load-action). The mapping between this plain text representation to json should be done as described [here](#command-translator-output-payload).

It should stress the connection between the *source* and *destination* devices with the specified *load* Megabytes of traffic during the specified *duration*. The dynamic load behavior should be implemented as described in the [Cpu load action](#cpu-load-action).

The stress action should extract the parent *experiment* span context from the **experiment_context** field and submit the action span to the **OTLP Collector** as a child span.
The host running the **OTLP Collector** should be resolved from the [**env Module Configuration file**](#env) like [here](#experiment-dispatcher-start-action).


## 7. Agentless (ssh) Manager

### Agentless (ssh) Manager functional requirements

The **Agentless (ssh) Manager** should run an ssh daemon. This daemon should listen on the configurable port and allow executing *ssh* commands under a configurable user using a secret private ssh key coupled to the public ssh key exposed by the [**API**](#get-ssh-public-key-api). The ssh daemon port and username should match the ones declared in the [**Scenario Configuration file**](#scenario-configuration-file). The secret private key should be stored among the [**Module Configuration files**](#module-configuration-files).


## 8. API

### API functional requirements

#### Get ssh public key API

The **API** should expose the public part of the ssh key pair used in the [**Agentless (ssh) Manager](#7-agentless-ssh-manager) under the url like

```shell
http://${API_HOST}:${API_PORT}/static/ecdsa.pub
```

---

#### API Overview

Also, it should expose a set of endpoints as follows:

![API endpoints](img/API-endpoints.png)

#### Health API

| Method | URL |
|--------|-----|
| GET | /health |

should be useful for health-check.

##### Response (200)

Should mean that **API** component is up and running.

---

#### Get Apps API

| Method | URL |
|--------|-----|
| GET | /apps |

##### Response (200)

Should return a string array of application (service) names. These denote applications that are instrumented using OTLP and submit trace data there.

---

#### Get Experiments API

| Method | URL |
|--------|-----|
| GET | /experiments |


##### Response (200)

Should return an array of experiment names that were executed by the [**Experiment Dispatcher**](#3-experiment-dispatcher). Every experiment name should equal to the *experiment-name* in the [**Experiment Configuration file**](#experiment-configuration-file).

---

#### Get Experiment by Name API

| Method | URL |
|--------|-----|
| GET | /experiments/{name} |

#### Parameters
| Name | In | Description | Required |
|------|----|-------------|----------|
| name | path |  | Required |

##### Response (200)

Should return a list of experiment actions and their timing details for the given experiment *name*. Possible actions are specified [here](#2-event-orchestrator)

##### Response (422)
| Field | Type | Description |
|-------|------|-------------|
| detail | array |  |

Should mean an error while getting details of the experiment with the given *name*.

---

#### Get Experiment Statistics for an Application API

| Method | URL |
|--------|-----|
| GET | /experiments/{exp_name}/apps/{app_name} |

#### Parameters
| Name | In | Description | Required |
|------|----|-------------|----------|
| exp_name | path |  | Required |
| app_name | path |  | Required |
| extra_statistics | query |  | Optional |
| raw_data | query |  | Optional |

##### Response (200)

Should return statistics of the traces that happened during the experiment with name *exp_name* in the application or service named *app_name*. The detailed statistics should be accessible by turning on the **extra_statistics** flag. All span data should be retrieved when the **raw_data** flag is turned on. 

##### Response (422)
| Field | Type | Description |
|-------|------|-------------|
| detail | array |  |

Should mean that some error occurred while collecting the statistics.

---

#### Get Servers API

| Method | URL |
|--------|-----|
| GET | /apps/{app_name}/servers |

#### Parameters
| Name | In | Description | Required |
|------|----|-------------|----------|
| app_name | path |  | Required |

##### Response (200)

Should return a string array of server host names that run the specific application (service).

##### Response (422)
| Field | Type | Description |
|-------|------|-------------|
| detail | array |  |

Should mean an error that the list of servers cannot be obtained.

---

#### Get Spans API

| Method | URL |
|--------|-----|
| GET | /apps/{app_name}/spans/{span_name} |

#### Parameters
| Name | In | Description | Required |
|------|----|-------------|----------|
| app_name | path |  | Required |
| span_name | path |  | Required |
| length | query |  | Optional |
| start_time | query |  | Optional |
| duration | query |  | Optional |

##### Response (200)

Should return a list of *length* spans or a list of spans in the time range between *start_time* and *start_time + duration* having the specified name *span_name*. 

##### Response (422)
| Field | Type | Description |
|-------|------|-------------|
| detail | array |  |

Should mean an error of inability to get the spans for the given set of options.

---

#### Get Child Spans API

| Method | URL |
|--------|-----|
| GET | /apps/{app_name}/spans/{trace_id}/{span_id}/children |

#### Parameters
| Name | In | Description | Required |
|------|----|-------------|----------|
| app_name | path |  | Required |
| trace_id | path |  | Required |
| span_id | path |  | Required |

##### Response (200)

Should return the children spans for the given *trace_id* and *span_id* parent span. This API is used internally by the *experiment* APIs above.

##### Response (422)
| Field | Type | Description |
|-------|------|-------------|
| detail | array |  |


---

#### Get Cpu API


| Method | URL |
|--------|-----|
| GET | /servers/{server_name}/metrics/cpu |

#### Parameters
| Name | In | Description | Required |
|------|----|-------------|----------|
| server_name | path |  | Required |
| duration | query |  | Optional |

##### Response (200)
| Field | Type | Description                                        |
|-------|------|----------------------------------------------------|
| cpu_load | array | list core-load_percentage pairs for every CPU core |
| t0 | integer | measurement start time                             |
| t1 | integer | measurement end time                               |
| t1_t0 | integer | difference between t1 and t0                       |

##### Response (422)
| Field | Type | Description |
|-------|------|-------------|
| detail | array |  |

---

#### Get Ram API

| Method | URL |
|--------|-----|
| GET | /servers/{server_name}/metrics/ram |

#### Parameters
| Name | In | Description | Required |
|------|----|-------------|----------|
| server_name | path |  | Required |
| duration | query |  | Optional |

##### Response (200)
| Field | Type | Description |
|-------|------|-------------|
| free | number |  |
| total | number |  |

##### Response (422)
| Field | Type | Description |
|-------|------|-------------|
| detail | array |  |

---

#### Get Frontend Page API

| Method | URL |
|--------|-----|
| GET | / |

##### Response (200)

Should return the html page of the [**Web Frontend Console**](#4-web-frontend-console).

---

#### Broadcast to all Web Frontend Console sessions API

| Method | URL |
|--------|-----|
| POST | /console |

##### Request Body
| Field | Type | Description | Required |
|-------|------|-------------|----------|
| error | integer |  | Optional |
| sender | string |  | Required |
| text | string |  | Required |

##### Response (200)

Should broadcast the given message to all open [**Web Frontend Console**](#4-web-frontend-console) sessions.

##### Response (422)
| Field | Type | Description |
|-------|------|-------------|
| detail | array |  |

---
