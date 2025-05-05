# Performing SigNoz metric-related queries

Signoz offers several tables from where to query. As for now, we use two tables from the signoz_metrics data base:


* distributed_time_series_v4: stores information of the metrics, but only the last 2/3/4 values are stored (it seems to be refreshed automatically). This table is useful just to get the fingerprint of a certain metric
* samples_v4: stores the real values of the metrics

Both tables are related through the `fingerprint` parameter.


The local collector collects the data from the host machine where the server or client application run. It is possible to identify, what data corresponds to what collector using the `host_name` parameter. This value will be the same as when you open the cmd in that refered machine. 


The figure shows the data that was collected for cpu state in the client machine whose `host_name=UEcollector`. The name of the metric that retrieves this type of information is `system_cpu_time` and is obtained when the `cpu:{}` parameter is configured in `hostmetrics` in the distributed collector `config.yaml`

```bash
 #config.yaml of a distributed collector
  hostmetrics:
    collection_interval: 100ms
    scrapers:
      cpu: {}
      load: {}
      memory: {}
```



![](img/metrics_2.png)

Note that the distributed collector is set in debug mode by default, so you can export to the console the data the collector is gathering. This is done by creating a debugger exporter in the `config.yaml` file and configuring the pipelines.


```bash
 #config.yaml of a distributed collector
exporters:
  otlp:
    endpoint: "172.22.174.137:4317"
    # this must be replaced by the IP of your central collector. keep the port
    tls:
      insecure: true
  debug:
    # verbosity of the debug exporter: detailed, normal, basic
    verbosity: detailed
service:
  telemetry:
    metrics:
      address: 0.0.0.0:8888
  extensions: [health_check, zpages]
  pipelines:
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp]
    metrics/internal:
      receivers: [hostmetrics]
      processors: [resourcedetection, batch]
      #debug exporter is also added here
      exporters: [otlp, debug]
```

To start seeing the values being collected, just run the otel collector in an independent console, or if it is a docker container, access to it in interact mode.


```bash

cd src/main/Distributed/Collector

# run the distributed collector
# you migth need to give executable permisions to the otelcol-contrib before with chmod
./otelcol-contrib --config ./config.yaml
```

Now, in the next figure you can see an example of how the individual core state previously gathered by the distributed collector, has been stored in the clickhouse database. Take a look to how the two tables here are realted.

* **red:** the fingerprint that relates both tables for a certain metric. Each metric type has its own fingerprint.
* **green:**  The complementary information of the metric. For example, to calculate usage time of `cpu16`, you need to know the time it was idle during the last `x` seconds, where `x` is the `collection_interval`, configured in the local collector `config.yaml` for host metrics. By default it is configured to `100ms`. Each metric type has its own complementary data needed to perform the caluclations.
* **orange:** This is the time stamp of when the metric was collected in the distributed collector (not sure yet if it is collection time at the local host, or stored time at clickhouse)

*Note: the time stamp `unix_millis` in the table `distributed_time_series_v4` is useless. It only shows the time when you started the SigNoz collector, and it is therefore static for all the metrics stored there*

![](img/metrics_1.png)


Now, let´s check a little further how the `fingerprint` are assigned. To do so, we will use an example with `cpu16` state collected via the `system_cpu_time` metric.

![](img/metrics_3.png)

As you can see, the same `fingerprint` is assigned to the `value` of the `cpu16`, of the `host_name=UEcollector` and the `state=idle`. The temporality of the `system_cpu_time` is cumulative, that is to say, that the value is always increasing, therefore, to get the amount of `idle` time of `cpu16`, you need to substract two rows, which are separated *n* `collection_interval` (example below). Also, the `unit` column of the row obtained from the table `distributed_time_series_v4` is important for further analysis. In this case, we know the value is in `seconds`


Then, to get the cpu idle time during the last `collection_interval`, assuming this was `30s`, we have to request the `samples_v4` table to get the cummulative value stored in  `value` column during the last `30s` and based on a given `fingerprint`, but to know what `fingerprint` we need, we must first query the table `distributed_time_series_v4` for the specific cpu and state, in this example `cpu16` and `idle.`.  In the example, you can see that the fingerprient we have found is `124765....767`. Based in it, we now get the last two values shown in the table `samples_v4`, which are `678116` and `678086.1`. Finally, subtracting them will give the time the `cpu16` was in `idle` during the last `30s`. That is `29.33s`.


## Further explanation of fingerprint relationship across tables

Each row with different information, gets its own `fingerprint`, even if they belong to the same metric (eg. `system_cpu_time`). This sounds very confusing (and it is) but checking the following image might help.
















![](img/metrics_4.png)


As you can see here, these are some of the cpu states collected from the `system_cpu_time` table enables via `cpu: {}` in the `host_metrics`. Each core might have 8 states, which are reported independently if the core was in that state during the `collection_interval`. If you take a closer look, each state of each cpu has its own `fingerprint`. but the same `fingerprint` is repeated for the same cpu and the same state along time. 










Now, if we filter the distinct `fingerprint` for all the cores in `state=idle` in the `host_name=UEcollector` (24 in my case), you will see what we tried to explain earlier a little bit clearer. 









![](img/metrics_5.png)


Now, if we filter the distinct `fingerprint` for all the cores in `state=wait` in the `host_name=UEcollector` (24 in my case), you will notice that the `fingerprint` changes, even though it is the same cpu, but it changes because we are asking for a different state. 

![](img/metrics_6.png)

All `fingerprint` properly correspond to the ones shown in the first figure of the example.

*Note: Try to follow the `fingerprint` assigned for `cpu6` to get a better understanding* 



# Querying

Each metric collected has its own temporality and specific data, therefore, to get the information, an individual and specifyc query must be created. 

The following query shows an example of how the provided library gets the time a given cpu `{cpu_name}` was in a given state `{cpu_state}` for a given host `{host_name}`, during a given time interval `{time_diference}`.

```bash
        WITH 
        -- Step 1: Get the fingerprint dynamically
        fingerprint_cte AS (
            SELECT fingerprint
            FROM signoz_metrics.distributed_time_series_v4
            WHERE 
                metric_name = 'system_cpu_time' 
                AND simpleJSONExtractString(labels, 'host_name') = '{host_name}' 
                AND simpleJSONExtractString(labels, 'cpu') = '{cpu_name}' 
                AND simpleJSONExtractString(labels, 'state') = '{cpu_state}'
            ORDER BY unix_milli DESC 
            LIMIT 1
        ),
        -- Step 2: Get the latest timestamp and value
        latest AS (
            SELECT unix_milli, value
            FROM signoz_metrics.samples_v4
            WHERE 
                metric_name = 'system_cpu_time' 
                AND fingerprint = (SELECT fingerprint FROM fingerprint_cte)
            ORDER BY unix_milli DESC
            LIMIT 1
        ),
        -- Step 3: Calculate the target timestamp (latest - {time_difference} milliseconds)
        target_time AS (
            SELECT (unix_milli - {time_difference}) AS target_unix_milli
            FROM latest
        ),
        -- Step 4: Find the row closest to the target timestamp
        closest AS (
            SELECT 
                value AS closest_value,
                unix_milli AS closest_unix_milli
            FROM signoz_metrics.samples_v4
            WHERE 
                metric_name = 'system_cpu_time'
                AND fingerprint = (SELECT fingerprint FROM fingerprint_cte)
            ORDER BY abs(unix_milli - (SELECT target_unix_milli FROM target_time)) ASC
            LIMIT 1
        )
        -- Step 5: Calculate the value difference
        SELECT 
            l.value - c.closest_value AS value_difference,
            l.unix_milli AS latest_unix_milli,
            c.closest_unix_milli AS closest_unix_milli
        FROM 
            latest l,
            closest c;
        """
```