# Observability Architecture: Traces, Agents, and Deep-Dive Flows

This document details the data flows, protocols, and low-latency mechanisms that make up a modern observability system.

---

## StatsD vs OpenTelemetry: Protocol vs Framework

While both collect data, the technical philosophy behind them is radically different.

### 1. StatsD (Metrics Protocol)
StatsD is a **simple textual protocol** based on UDP. It doesn't care about connection state or whether the data arrived.

- **Focus:** Metrics only (Counters, Gauges, Histograms).
- **Transport:** UDP (Port 8125). Zero network overhead for the application.
- **Data Model:** Flat (Key-Value). E.g.: `response_time:150|ms`. 
- **Philosophy:** "Fire and forget". Extremely lightweight, ideal for apps that cannot have latency added by observability.
- **Limitation:** No native support for distributed Tracing or Logs. Tags are an extension (DogStatsD).

### 2. OpenTelemetry (Telemetry Framework)
OTel is a **unified standard and a set of SDKs** that handle the complete data lifecycle (Traces, Metrics, Logs).

- **Focus:** Full Telemetry (Metrics + Traces + Logs + Profiles).
- **Transport:** OTLP (gRPC or HTTP/JSON). Requires TCP/TLS handshake, which ensures delivery but adds computational cost.
- **Data Model:** Structured and Semantic. Follows the **Attributes** pattern (nested metadata).
- **Philosophy:** "Total interoperability". Data is rich, standardized, and injected with context (Context Propagation).
- **Limitation:** Higher memory/CPU consumption in the SDK. More complex configuration (Collectors, Processors).

### Technical Comparison Table

| Feature | StatsD (DogStatsD) | OpenTelemetry (OTLP) |
| :--- | :--- | :--- |
| **Protocol** | UDP (Custom Text) | gRPC / HTTP (Protobuf) |
| **Delivery Guarantee** | None (Best Effort) | High (Retry & Backoff) |
| **Payload** | Small (Simple Text) | Large (Protobuf Messages) |
| **Context** | Limited (Tags only) | Rich (Linkage between signals) |
| **Standardization** | Fragmented | Universal (W3C) |

---

## 1. Distributed Tracing and Context Propagation

Tracing isn't just about what happens inside an app, but how the request travels.

### Propagation Mechanisms
To maintain the Trace lineage between services (e.g., Python App -> Go API -> DB), the `trace_id` and `parent_id` need to be injected into HTTP headers.
- **Header Standards:**
    - **W3C (Traceparent):** The modern unified standard (`00-4bf92...`).
    - **B3 (Zipkin):** Common in legacy or Java Spring environments.
    - **Datadog Headers:** `x-datadog-trace-id` (64-bit integer) and `x-datadog-parent-id`.

### Sampling Strategies
Capturing 100% of traces in high-volume systems is prohibitive due to cost and storage.
- **Head-based Sampling:** The decision to capture or not is made at the **beginning** of the request (by the Library). If the library decides not to capture, nothing is sent.
- **Tail-based Sampling:** The Agent (or an OTel Collector) receives 100% of spans, stores them in memory, and decides to keep only the traces that:
    - Show an error (`status:error`).
    - Have latency above a specific percentile (e.g., > P95).
    - Are statistically relevant.

---

## 2. StatsD and DogStatsD: Low Latency via UDP

The StatsD protocol was created to be "fire and forget".

- **UDP Protocol (Port 8125):** Unlike TCP, UDP does not require a 3-way handshake. The application "fires" a network packet and immediately returns to processing code (latency < 1ms).
- **Packet Format:** `metric:value|type|#tags`. Example: `catalog.db.load:12|g|#env:dev,version:1.1.0`.
- **Aggregation in the Agent:**
    - The Agent does not send every packet received to the SaaS.
    - It maintains a **Flush Window** (usually 10 seconds).
    - It sums all `counters`, takes the average of `gauges`, and calculates histograms locally, sending only the compressed summary to the cloud.

---

## 3. The Agent Pipeline (Datadog/OTel)

Internal processing in the agent follows an event-driven architecture:

1.  **Ingestion (Receivers):** Listens on specific ports (8126 for Traces, 8125 for StatsD, Socket for Logs).
2.  **Normalization:** Converts proprietary formats (e.g., traces from Python, Ruby, Java) to a common internal data model.
3.  **Obfuscation:** The Agent filters sensitive data (Credit card patterns, passwords in SQL queries) before sending it outside the network.
4.  **Forwarder (HTTPS 443):** Manages the output buffer. If the network goes down, the Agent stores data on disk (persistent buffer) until connectivity returns.

---

## 4. AWS Connectivity and Security (IAM)

When the Agent runs on AWS (EC2, EKS, or Fargate), communication is optimized:

### Authentication via Cross-Account
The Datadog-AWS integration does not use AK/SK (Access Keys). It uses **IAM Roles with External ID**:
1.  Datadog generates a unique `External ID` for your account.
2.  You create a Role in AWS that allows Datadog (AWS ID `464660061966`) to `sts:AssumeRole`.
3.  This ensures that even if someone discovers your Role name, they cannot assume it without the correct External ID.

### VPC Endpoints (AWS PrivateLink)
In high-security environments (with controlled internet), the Agent doesn't go through the NAT Gateway. It uses an internal **VPC Endpoint** to speak directly to the Datadog backbone via the private AWS network, reducing egress costs and increasing security.

---

## 5. OpenTelemetry Collector Pipeline

If you choose OTel instead of a proprietary agent, the flow is defined by this pipeline in `config.yaml`:

```yaml
receivers:
  otlp:
    protocols: [grpc, http]
processors:
  batch: # Groups spans to optimize sending
  resourcedetection: # Automatically detects if on AWS/GCP
exporters:
  datadog:
    api: {key: "XXXX"}
```

This Collector can run as a **Sidecar** (next to the app container) or as a centralized **Gateway** in the cluster.
