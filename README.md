# Prometheus Midware

## Hierarchy and Architecture

modules and contents:
```
- midware_prometheus/
    - daemonize.py
    - prometheus_main.py
    - prometheus.py
    - config.json
```

* **`daemonize.py`**: This module assists user to run prometheus middleware as a daemon.
* **`prometheus_main.py`**: This module contains the user interface of prometheus middlware.
* **`prometheus.py`**: This module contains the main control logic of the entire prometheus middleware, including grabbing data from the prometheus server, formatting scraped data, outputting the data into a csv file, etc.
* **`config.json`**: This is the main configuration file of prometheus middleware.

## Usage
```bash 
$ python3 prometheus_main.py [daemon|restart|stop|start]
```
Prometheus midware can be run in both background and foreground.

### Foreground
* `start`:  start argument runs the midware normally in the foreground.
```bash
$ python3 prometheus_main.py start
Starting...
Daemonize_off
...
```
### Background
* `daemon`: Daemon arguemnt input would daemonize the process using daemonize module implemented by 鎮寧. The midware will be detached from the current terminal, then run in the background.
* `stop`: Stop argument kills the background prometheus middleware process.
```bash
$ python3 zabbix_main.py daemon
Starting...
$ python3 zabbix_main.py stop
Stopping...
Daemon_has_stoped
```
## Configuration File
Every settings related to prometheus middleware can be configured in config.json.

Below is a sample `config.json`:
```json=
{
    "out_Dir": "test",
        "url": "http://dev.k8s:31390",
        "configs": [
        {
            "ip": "172.16.1.99",
            "exporter": "kubelet",
            "probe": "kubernetes_probe",
            "metrics": {
                "kubernetes_cpu_usage_sum": "sum(rate(container_cpu_usage_seconds_total{container!=\"POD\",pod!=\"\"}[3m]))",
                "kubernetes_cpu_usage_request": "sum(kube_pod_container_resource_requests_cpu_cores)",
                "kubernetes_memory_usage_sum": "sum(rate(container_memory_usage_bytes{container!=\"POD\",pod!=\"\"}[3m]))",
                "kubernetes_memory_usage_request": "sum(kube_pod_container_resource_requests_memory_bytes)",
                "kubernetes_network_transmit_bytes_total": "sum(rate(container_network_transmit_bytes_total{container!=\"POD\"}[3m]))",
                "kubernetes_network_receive_bytes_total": "sum(rate(container_network_receive_bytes_total{container!=\"POD\"}[3m]))",
                "kubernetes_container_restart_total": "sum(kube_pod_container_status_restarts_total)"
            },
            "write_metrics": [
            ]
        },
        {
            "ip": "172.16.1.99",
            "exporter": "kubelet",
            "probe": "kubernetes_container_probe",
            "metrics": {
                "kubernetes_container_cpu_usage": "rate(container_cpu_usage_seconds_total{container!=\"POD\",pod!=\"\"}[3m])",
                "kubernetes_container_memory_usage": "rate(container_memory_usage_bytes{container!=\"POD\",pod!=\"\"}[3m])"
            },
            "write_metrics": [
                "namespace",
            "pod",
            "container"
            ]
        },
        {
            "ip": "172.16.1.99",
            "exporter": "kubelet",
            "probe": "kubernetes_pod_probe",
            "metrics": {
                "kubernetes_pod_cpu_usage": "sum(rate(container_cpu_usage_seconds_total{container!=\"POD\",pod!=\"\"}[3m])) by (pod)",
                "kubernetes_pod_memory_usage": "sum(rate(container_memory_usage_bytes{container!=\"POD\",pod!=\"\"}[3m])) by (pod)"
            },
            "write_metrics": [
                "pod"
            ]

        },
        {
            "ip": "172.16.1.99",
            "exporter": "kubelet",
            "probe": "kubernetes_node_probe",
            "metrics": {
                "kubernetes_node_allocable_pods": "kube_node_status_allocatable_pods",
                "kubernetes_node_allocable_cpu_core": "kube_node_status_allocatable_cpu_cores",
                "kubernetes_node_allocable_memory": "kube_node_status_allocatable_memory_bytes"
            },
            "write_metrics": [
                "node"
            ]

        },
        {
            "ip": "172.16.1.99",
            "exporter": "kubelet",
            "probe": "kubernetes_namespace_probe",
            "metrics": {
                "kubernetes_namespace_cpu_usage": "sum(rate(container_cpu_usage_seconds_total{container!=\"POD\",namespace!=\"\"}[3m])) by (namespace)",
                "kubernetes_namespace_memory_usage": "sum(rate(container_memory_usage_bytes{container!=\"POD\",namespace!=\"\"}[3m])) by (namespace)"
            },
            "write_metrics": [
                "namespace"
            ]

        }
    ]
}
```
* **`out_Dir`**: This field specifies the output directory of the csv files.
* **`url`**: Specifies the url of your prometheus server.
* **`configs`**: This field is an array that contains the setting of different probes. Each element in this array is an object that contains the following fields:
    * **`ip`**: The IP address of your target.
    * **`exporter`**: The exporter that the probe uses.
    * **`probe`**: The name of the probe.
    * **`metrics`**: An array of metrics that you want to use in the probe. The metrics must be a *PromQL* expression. ([More information for PromQL](https://prometheus.io/docs/prometheus/latest/querying/basics/))
    * **`write_metrics`**: An array of metric labels that you want write to your csv file.

## Output CSV

The name format of the csv file is shown below:

| **Format** | ***probe name*** | @ | ***date*** | . | csv |
| - | -| - | - | - | - |
| **Example 1** |  kubernetes_probe | @ | 20201204_16_08 | . | csv |
| **Example 2** |  kubernetes_node_probe | @ | 20201204_16_10 | . | csv |

* :memo: Date format is `"%Y%m%d_%H_%M"`


The format of the content is shown below:

| **Format** | ***value*** | ***subprobe name***  |  ***subfields*** |  ***subfields*** | ... | ***target IP*** | ***date*** |
| - | -| - | - | - | - | - | - |
| **Example 1** | 0.010182706464034987 | kubernetes_container_cpu_usage | kube-system (namespace) | calico-node (container) | calico-node-2pnlr (pod) | 172.16.1.99 | 20201204_16:08:17 |
| **Example 2** | 110 | kubernetes_node_allocable_pods | 1.dev.k8s (node) | | | 172.16.1.99 | 20201204_16:10:13 |

* :memo: Date format is `"%Y%m%d_%H:%M:%S"`


### Sample

Below is a sample output csv file `kubernetes_probe@20201204_16_08.csv`:

```csv
23.3665936816224,kubernetes_cpu_usage_sum,172.16.1.99,20201204_16:08:17
1.65,kubernetes_cpu_usage_request,172.16.1.99,20201204_16:08:17
16913905.219381742,kubernetes_memory_usage_sum,172.16.1.99,20201204_16:08:17
817889280,kubernetes_memory_usage_request,172.16.1.99,20201204_16:08:17
54819.22700615068,kubernetes_network_transmit_bytes_total,172.16.1.99,20201204_16:08:17
49244.03774023048,kubernetes_network_receive_bytes_total,172.16.1.99,20201204_16:08:17
11660,kubernetes_container_restart_total,172.16.1.99,20201204_16:08:17
```
## Kubernetes Exporter
### kubelet metrics
* Provides metrics via *cAdvisor*.
* Provides container-level metrics such as resource usage from running containers.
### kube-state-metrics
* A simple service that listens to the Kubernetes API server and generates metrics about the state of Kubernetes.
* It focuses on the state of the various objects *inside Kubernetes*, such as metrics based on pod, deployments, replica sets, etc.
### apiserver metrics
* Provides metrics via *kube-apiserver*
* Provides cluster level metrics that monitors *noncontainerized* workloads, such as load-balanced cluster services, client certificates, and so on.
## Kuberentes Metrics

The following is the metric I used in this project：

* **`container_cpu_usage_seconds_total`**
    * **Exporter**: kubelet
    * **Description**: The current cumulative CPU usage time of the container
* **`container_memory_usage_bytes`**
    * **Exporter**: kubelet
    * **Description**: The current cumulative memory usage (in bytes)
* **`container_network_transmit_bytes_total`**
    * **Exporter**: kubelet
    * **Description**: The cumulative amount of data transmitted in the container network 
* **`container_network_receive_bytes_total`**
    * **Exporter**: kubelet
    * **Description**: The cumulative amount of data received in the container network
* **`kube_pod_container_resource_requests_cpu_cores`**
    * **Exporter**: kube-state-metrics
    * **Description**: The number of CPU cores currently required by the Pod
* **`kube_pod_container_status_restarts_total`**
    * **Exporter**: kube-state-metrics
    * **Description**: Cumulative number of Pods that restarts
* **`kube_pod_container_resource_requests_memory_bytes`**
    * **Exporter**: kube-state-metrics
    * **Description**: The number of memory (in bytes) currently required by the Pod
* **`kube_node_status_allocatable_cpu_cores`**
    * **Exporter**: kube-state-metrics
    * **Description**: CPU resources currently provided by Node
* **`kube_node_status_allocatable_memory_bytes`**
    * **Exporter**: kube-state-metrics
    * **Description**: Memory resources currently provided by Node
* **`kube_node_status_allocatable_pods`**
    * **Exporter**: kube-state-metrics
    * **Description**: Number of pods currently provided by Node
* **`apiserver_request_total`**
    * **Exporter**: kube-apiserver
    * **Description**: Monitor the source requests, destination request, and whether the request were successful.
    
### Kubernetes Probe
* **`kubernetes_cpu_usage_sum`**
    * **Metric**: `sum(rate(container_cpu_usage_seconds_total{container!="POD",pod!=""}[3m]))`
    * **Description**: Collect the cumulative CPU usage time of the entire Kubernetes in the past 3 minutes.
* **`kubernetes_memory_usage_sum`**
    * **Metric**: `sum(rate(container_memory_usage_bytes{container!="POD",pod!=""}[3m]))`
    * **Description**: Collect the cumulative memory usage of the entire Kubernetes in the past 3 minutes.
* **`kubernetes_cpu_usage_request`**
    * Metric: `sum(kube_pod_container_resource_requests_cpu_cores)`
    * **Description**: Collect the memory usage required and used by Pods in the entire Kubernetes.
* **`kubernetes_memory_usage_request`**
    * **Metric**: `sum(kube_pod_container_resource_requests_memory_bytes)`
    * **Description**: Collect the cumulative data transmission volume of the entire Kubernetes in the past 3 minutes.
* **`kubernetes_network_receive_bytes_total`**
    * **Metric**: `sum(rate(container_network_receive_bytes_total{container!="POD"}[3m]))`
    * **Description**: Collect the cumulative received data volume of the entire Kubernetes in the past 3 minutes.
* **`kubernetes_network_transmit_bytes_total`**
    * **Metric**: `sum(rate(container_network_transmit_bytes_total{container!="POD"}[3m]))`
    * **Description**: Collect the cumulative received data volume of the entire Kubernetes in the past 3 minutes.
* **`kubernetes_container_restart_total`**
    * **Metric**: `sum(kube_pod_container_status_restarts_total)`
    * **Description**: Collect the cumulative number of Pod restarts in the entire Kubernetes.
### Kubernetes Container Probe
* **`kubernetes_container_cpu_usage`**
    * **Metric**: `rate(container_cpu_usage_seconds_total{container!="POD",pod!=""}[3m])`
    * **Description**: Collect the cumulative CPU usage time of each container in the past 3 minutes.
* **`kubernetes_container_memory_usage`**
    * **Metric**: `rate(container_memory_usage_bytes{container!="POD",pod!=""}[3m])`
    * **Description**: Collect the cumulative memory usage of each container in the past 3 minutes.
### Kubernetes Pod Probe
* **`kubernetes_pod_cpu_usage`**
    * **Metric**: `sum(rate(container_cpu_usage_seconds_total{container!="POD",pod!=""}[3m])) by (pod)`
    * **Description**: Collect the cumulative CPU usage time of different Pods in the past 3 minutes.
* **`kubernetes_pod_memory_usage`**
    * **Metric**: `sum(rate(container_memory_usage_bytes{container!="POD",pod!=""}[3m])) by (pod)`
    * **Description**: Collect the cumulative memory usage of different Pods in the past 3 minutes.
### Kubernetes Node Probe
* **`kubernetes_node_allocable_pods`**
    * **Metric**: `kube_node_status_allocatable_pods`
    * **Description**: Collect the pod resources currently provided by each Node.
* **`kubernetes_node_allocable_cpu_core`**
    * **Metric**: `kube_node_status_allocatable_cpu_cores`
    * **Description**: Collect the CPU resource usage currently provided by each Node.
* **`kubernetes_node_allocable_memory`**
    * **Metric**: `kube_node_status_allocatable_memory_bytes`
    * **Description**: Collect the number of memory bytes currently provided by each Node.
### Kubernetes Apiserver Probe
* **`kubernetes_apiserver_success_requests`**
    * **Metric**: `sum(rate(apiserver_request_total{code=~"2.."}[3m]))`
    * **Description**: Collect all the successful requests from kube-apiserver.
* **`kubernetes_apiserver_failed_requests`**
    * **Metric**: `sum(rate(apiserver_request_total{code=~"[45].."}[3m]))`
    * **Description**: Collect all the failed requests from kube-apiserver.

* ::note:: Note that some of the above metrics calculate the average value under 3 minutes. The interval can be set to some other suitable number.

## Reference
1. [Prometheus documentation](https://prometheus.io/docs/introduction/overview/)
2. [Kubernetes in Production: The Ultimate Guide to Monitoring Resource Metrics with Prometheus](https://www.replex.io/blog/kubernetes-in-production-the-ultimate-guide-to-monitoring-resource-metrics)
3. [Metrics used in Alamada](https://github.com/containers-ai/alameda/blob/master/docs/metrics_used_in_Alameda.md)
