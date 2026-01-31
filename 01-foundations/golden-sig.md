## The Four Golden Signals

> **Concept:** These are the essential metrics for monitoring distributed systems (as defined by Google SRE). Think of them as the "Vital Signs" of a patient in the emergency room: before ordering a complex test (deep log analysis), you check their pulse and blood pressure.

### 1. Latency
* **Definition:** The time it takes to service a request.
* **Point of Attention:** Don't just monitor the average! The average hides problems.
    * *Example:* If 50% of requests take 100ms and 50% take 10s, the average looks acceptable (~5s), but half the users are having a terrible experience.
* **SRE Tip:** It's crucial to distinguish between **success** latency and **error** latency. A 500 error can return very quickly, distorting your performance charts.

### 2. Traffic
* **Definition:** The demand placed on the system.
* **Common Metrics:**
    * *Web:* Requests per second (RPS) or HTTP requests.
    * *Backend/DB:* Transactions per second (TPS).
    * *Streaming:* Concurrent sessions.
* **Importance:** Traffic gives context to other metrics. (Did latency spike because the code is bad or because traffic tripled?)

### 3. Errors
* **Definition:** The rate of requests that fail.
* **Types:**
    * *Explicit:* HTTP 500, exceptions, connection failures.
    * *Implicit:* HTTP 200 with the wrong/empty content or responses that are too slow (client timeout).
* **Mindset:** For an SRE, "too slow" is also an error.

### 4. Saturation
* **Definition:** How "full" your service is. It's a measure of the remaining capacity.
* **Metrics:** CPU, Memory, Disk I/O, DB Connection Pool.
* **Key Difference:** While Latency and Errors show what is happening *now*, Saturation is a predictive indicator of what will happen *in the future*.
* **Analogy:** If saturation hits 100%, performance degrades abruptly.

---

### Educational Summary: The Highway Analogy

Use this table to explain the correlation between the signals:

| Golden Signal | Highway Analogy | Question an SRE asks |
| :--- | :--- | :--- |
| **Traffic** | Number of cars passing the toll booth per minute. | "What is the current demand?" |
| **Latency** | Time it takes to get from point A to point B. | "Is the user waiting too long?" |
| **Errors** | Cars broken down on the shoulder or accidents on the track. | "Are requests failing?" |
| **Saturation** | The size of the traffic jam (road density). | "Are we close to locking everything up?" |
