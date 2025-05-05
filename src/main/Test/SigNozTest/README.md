# Running SigNoz with Docker Compose

This example runs the official SigNoz platform without any modification included in EDP, so you can get in touch with it if you desire.

1. It is better if you run SigNoz in your VM, as we have already docker and all the dependencies open. However, be aware that if you have Jaeger running there, you must stop it first.
2. In a directory of your choosing, clone the SigNoz repository and cd into the signoz/deploy directory by entering the following commands:
```bash
git clone -b main https://github.com/SigNoz/signoz.git && cd signoz/deploy/
```
3. To install SigNoz, enter the docker compose up command, specifying the following: -f and the path to your configuration file -d to run containers in the background

```bash
docker compose -f docker/clickhouse-setup/docker-compose.yaml up -d
```
4. Ensure that your containers are running correctly. To view the status of your containers, run the following command:

```bash
docker ps
```

![](img/Signoz-containers.png)


5. Wait for all the pods to be in running state, and then point your browser to http://IP-ADDRESS:3301/ to access the dashboard, replacing <IP-ADDRESS> with the IP address of the machine where you installed SigNoz. If you're running SigNoz on your local machine, you should point your browser to http://localhost:3301/.


To uninstall SigNoz, when you are done using it:

```bash
docker compose -f docker/clickhouse-setup/docker-compose.yaml down -v
```

__Note:__ The docker-compose.yaml installs a sample application named HotR.O.D that generates tracing data. You can explore the SigNoz dashboard with the data provided by the sample application.

# Remove the sample application

1.	From the directory in which you installed SigNoz, open Docker Compose file deploy/docker/clickhouse-setup/docker-compose.yaml in a plain-text editor.

2.	Comment out or remove the services.hotrod and services.load-hotrod sections, which are located at the end of the file.

![](img/delete-default-app.png)


3.	Run once again the docker compose command from the same directory, or use the prior command from the deploy directory.

# Run the provided Examples

Before running the examples, make sure you have python3 and pip properly installed and working.
The shared folder contains multiple examples showing how to use the different signals that can be sent to a collector with OpenTelemetry (logs, metrics, traces). You will interact with them using the OpenTelemetry SDK for Python.  
More information here: Signals | OpenTelemetry
To execute the scripts, you will need to install the requirements.txt. 

_Hint: Please, if you notice that a dependency is missing, let us know to properly update the file._


## Logs Example

A log is a timestamped text record, with metadata. Although logs are an independent data source, they may also be attached to spans. In OpenTelemetry, any data that is not part of a distributed trace or a metric is a log. Signoz makes it possible to relate traces with logs through the provided GUI.
There is a specific python script that you should check to understand how to send logs to a exporter. First use the Console as exporter and then you can use the OTLP exporter (this is how you send the data to Signoz)


## Metrics Example
A metric is a measurement of a service captured at runtime. The moment of capturing a measurements is known as a metric event, which consists not only of the measurement itself, but also the time at which it was captured and associated metadata. OpenTelemetry allows to gather custom metrics embedded in the application. However, it is also possible to collecto host metrics. This example shows how to create your own metrics. If you are interested in getting host metrics such as CPU, GPU, memory, etc, check here: 

- [OpenTelemetry](https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/receiver/hostmetricsreceiver/README.md)

- [observIQ](https://observiq.com/blog/how-to-monitor-host-metrics-with-opentelemtry)

There is a specific python script that you should check to understand how to create a metric such as a counter and show it through the Console as exporter. Afterwards, you can use the OTLP exporter to send it to Signoz, but this will require you to modify the collector yaml file to create a new metric.


## Traces Example

Traces is what we are concerned about (at least for now), as they give us the big picture of what happens when a request is made to or from an application client. With traces we can see the overall end-to-end latency but also the duration of each of the steps (spans) the application performed.

In a distributed application (like an edge-dependent application), you will have a client and a server application segment. The idea is to track the set of events/steps (spans) and the duration of each one of them, while the application is working. In the files you will have two examples:
1.	Simple Trace creation: A unique file with a couple of parent and child spans that export data through the console or the Signoz collector. It will be a good idea if first you export the traces to the console to see the data. Make sure you identify the relation between the trace id and span id in each span. This will be important for the second example.

2.	Propagated Trace: In a distributed application we need to know the duration of the steps performed in both, the client and the server. OpenTelemetry allows to do it by propagating the trace id from the client to the server, by injecting this information in the headers of the communication established. Then, the server reads this id and creates a span based on it. Both applications need to have the same exporter for this idea to work, as the client and the server will send their own traces separately to the general collector, then this will recognize that the trace id is the same and put everything together.
