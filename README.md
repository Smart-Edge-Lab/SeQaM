# SeQaM

## Introduction

The Service Quality Management(SeQaM) platform is a tool developed to facilitate end-to-end service quality management for edge computing. The platform leverages telemetry for data collection from user equipment devices (UE), edge servers, and network components. This allows the correlation of multi-source information to identify and address the root causes of service quality degradation in edge computing. Furthermore, it allows the implementation of feedback mechanisms that enhance overall service quality in edge computing.


SeQaM can be used for:
- data collection for end-to-end visibility and analysis for pinpointing the root causes of service quality degradation
- the creation of controlled experimental scenarios for performance evaluation
- edge application testing and benchmarking
- analytics for data-driven decision-making that ensures end-to-end service quality
- data generation for model training. 

Moreover, the platform is designed for seamless deployment in emulated, laboratory, and real-world environments, covering an edge application’s entire life cycle, from development to testing and runtime.


![SeQaM-Deployment](imgs/Deployment_scenarios.png)


## Motivation/Problem


Edge computing enables deploying compute and storage resources at the network's edge, closer to data sources, thereby reducing latency and bandwidth by sending data to a nearby edge server instead of a far away data center. However, the distributed and heterogeneous nature of edge computing makes it difficult to ensure consistent and reliable service quality. 

End-to-end service quality refers to the overall service quality of an edge application, encompassing the entire journey from the user device, through the network, to the edge server, and back. To address the challenges that edge computing poses to guarantee end-to-end service quality, edge applications should implement adaptability techniques. These techniques enable applications to adjust their behavior in response to fluctuating conditions. Similarly, the edge infrastructure can be dynamically reallocated by shifting workloads between different edge servers based on current resource availability, network conditions, and application demands. In self-adaptive systems, this is typically achieved through a MAPE control loop (Monitor, Analyze, Plan, Execute), which allows to continuously optimize performance by monitoring changes, analyzing data, planning necessary adjustments, and executing modifications.


![SeQaM-Motivation](imgs/SeQaM-Motivation.png)



SeQaM introduces a solution for researchers, developers, and infrastructure providers to develop, implement, and test solutions that enhance end-to-end service quality in edge applications such as augmented reality, connected and autonomous vehicles, UAVs, etc. We are happy to hear about your use case and plan together a service quality management solution. 

## Current Status

SeQaM consists of the integration of a set of tools and interfaces that allow to interact with them. The source code is entirely developed in Python3 and it is also containerized for easy integration and deployment.

The data collection is done using [OpenTelemetry](https://opentelemetry.io/). Therefore any framework and language supported by OpenTelemetry is also supported by SeQaM. Thus, your edge application can be written in Java, Python, Node.js, Go, PHP,.NET, Ruby, Elixir, and Rust.

This version is the first release of SeQaM. There are some things still missing and room for improvement. Therefore, your contribution to the platform is highly appreciated.


## Contribution

 See the [Contributing](/CONTRIBUTING.md) file for detailed guidelines on how to contribute to this project.

## Releases
This version corresponds to the first release of SeQaM and the implementation code for the paper: SeQaM: A Service Quality Manager for Edge Computing in IWCMC 2025 Conference


## Acknowledgment
This work was conducted as part of project EMULATE funded by the European Union and the German Federal Ministry of Economics and Climate Action under research grant 13IPC012.

## Citation

In case you have found SeQaM useful to implement your research, please cite our work as:

