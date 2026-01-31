---

## Learning Journey: The SRE Reasoning

This laboratory was built to simulate the evolution of an incident, from symptom to root cause. The line of reasoning follows this progression:

1.  **Level 1: Visibility (Where does it hurt?)** -> Understand the *Golden Signals* (Latency, Error, Traffic).
2.  **Level 2: Active Defense (How do I protect myself?)** -> See the **Circuit Breaker** prevent the fault from bringing down the app.
3.  **Level 3: Resource Management (Where is the bottleneck?)** -> Identify when the problem is not the code, but the exhausted **Connection Pool**.
4.  **Level 4: Continuity (Does the user notice?)** -> Implement **Graceful Degradation** with fallback to save the experience.
5.  **Level 5: Forensics (Why did it happen?)** -> Use the **APM "Detective"** to find the exact span that changed the system's behavior.

### How to Follow the Lab: The SRE Mindset
In each experiment, don't just "run the command". Follow this mental cycle:
1.  **Hypothesis:** "If I increase latency to 10s, what happens to the requests?"
2.  **Injection:** Apply chaos via `/chaos/configure`.
3.  **Observation:** Look at the **Trace Flame Graph** in Datadog. Find the tag `db.pool.active`.
4.  **Analysis:** "Did the Circuit Breaker open? Did the fallback work? Did P99 spike?"
5.  **Proposal:** "What could we change in the infra or code to mitigate this?"

---

## Part 1: Simulated Practical Lab (Theoretical Exercise)

**Objective:**
Practice the complete methodology of a Chaos Engineering experiment: define the steady state, formulate a hypothesis, observe the (simulated) results of a controlled failure, and propose resilience improvements.

**The Lab Environment (Setup):**

*   **Target Application:** `sre-lab`, a simple RESTful API responsible for fetching product information. The main endpoint is `GET /products/{id}`.
*   **Architecture:**
    *   An **API Gateway** forwards requests to `sre-lab`.
    *   `sre-lab` looks for data in a **Redis** cache.
    *   In case of a cache miss, it searches the **Postgres** database.
*   **Monitoring (Simulated Control Panel):**
    *   P95 Latency (API)
    *   Error Rate (API)
    *   Cache Hit Rate
    *   Service CPU

---

### The Theoretical Experiment: Step by Step

#### Step 1: Define the Steady State
"On a normal day, our panel shows:"
*   **P95 Latency:** ~50ms
*   **Error Rate:** ~0.1%
*   **Cache Hit Rate:** ~90%
*   **Service CPU:** ~15%

#### Step 2: Formulate the Hypothesis
**The Chaos:** "We're going to introduce a **3-second** latency in ALL queries to our Postgres database."
**Your Task:** "What do you expect to happen to each of the four metrics on our panel?"

#### Step 3: Observe the (Simulated) Results
"After the experiment, the panel showed the following spikes:"
*   **P95 Latency:** **~5000ms (5 seconds)**
*   **Error Rate:** **30%**
*   **Cache Hit Rate:** **Dropped to 15%**
*   **Service CPU:** **Spiked to 80%**

#### Step 4: Analysis and Corrective Actions
**Your Task:**
1.  "Why did the latency go to 5s, and not 3s?"
2.  "Why did the error rate explode to 30% if the DB was just slow?"
3.  "Why did the cache hit rate plummet?"
4.  "Based on this, list 2-3 resilience improvements for the backlog."

---
---

## Part 2: Practical Lab with Datadog (Real-World Observability)

**Objective:**
Execute the lab using the provided FastAPI application and the Datadog platform to visualize the real impact of chaos experiments.

### Prerequisites

1.  **Datadog Account.**
2.  **Datadog Agent** installed and running locally.
    *   Follow the [official Datadog instructions](https://docs.datadoghq.com/agent/basic_agent_usage/).
    *   Check status with `datadog-agent status`.

### Step 1: Install Dependencies
Navigate to the `lab` directory and install the dependencies.
```bash
cd lab
pip install -r requirements.txt
```

### Step 2: Configure the Environment
Export the following environment variables in your terminal:
```bash
export DD_SERVICE="sre-lab"

# Environment (e.g., dev, staging, prod)
export DD_ENV="development"

# Your application version
export DD_VERSION="1.1.0"

# Enables log injection
export DD_LOGS_INJECTION=true

# Optional: Datadog Agent address (if not localhost)
# export DD_AGENT_HOST=localhost
```

### Step 3: Run the Application with `ddtrace-run`
To enable automatic Datadog instrumentation, use `ddtrace-run` to start the application:
```bash
ddtrace-run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
Your application is now sending traces, metrics, and logs to Datadog.

### Step 4: The Hands-on Lesson in Datadog

#### 1. Create your Observability Dashboard
In Datadog, create a new dashboard to monitor the "steady state":
*   **Requests per Second:** `trace.fastapi.request.hits`
*   **Error Rate:** `trace.fastapi.request.errors`
*   **P95 Latency:** `trace.fastapi.request.duration`
*   **Cache Hit Rate:** `sum:catalog.cache.hit{*} / (sum:catalog.cache.hit{*} + sum:catalog.cache.miss{*})`
*   **DB Query Duration:** `catalog.db.query.duration`

#### 2. Run Chaos Experiments
Use the Swagger UI (`http://localhost:8000/docs`) and the `POST /chaos/configure` endpoint to inject chaos.

#### 3. Observe the Impact in Datadog
*   **In the Dashboard:** See the graphs change in real-time, validating your hypotheses.
*   **In APM > Traces:** Find a slow trace. Click on it to see the "flame graph" and visualize exactly where the time was spent.
*   **In Logs:** If you inject failures, you will see error logs correlated with the traces that failed.

This workflow — **define, observe, experiment, analyze** — using a real observability platform is at the heart of an SRE's work.

---
---

---

## Part 3: Advanced Resilience Scenarios

Now that you've mastered the basics, let's level up. The application now has **self-protection** and **dynamic degradation** mechanisms.

### 1. Saturation: The Load Effect on the DB
Database latency is no longer just what you configure. It now automatically increases if there are many concurrent requests.

*   **The Experiment:**
    1.  Clear the cache (`POST /chaos/clear_cache`).
    2.  Access the bulk test endpoint: `GET /products/bulk/test?requests=15`.
    3.  **Observe:** Why did the last requests take much longer than the first ones? How did Saturation affect the P99?

### 2. Circuit Breaker: System Protection
The Circuit Breaker prevents a slow or broken service from continuing to receive load.

*   **The Experiment:**
    1.  Configure 100% DB error (`db_failure_rate: 1.0`).
    2.  Make repeated requests until the state changes to `OPEN`.
    3.  **Analysis:** Verify if the response time for blocked requests was instantaneous.

---

## Part 4: Resource Exhaustion and "Trace Detective"

In this final phase, we simulate low-level infrastructure problems and use Datadog's APM to investigate the custom tags we injected into the code.

### 1. Experiment: Connection Pool Exhaustion
The database has a physical limit on connections. If they take too long, new requests will be blocked.

*   **The Chaos:**
    1.  Configure 10s DB latency (`db_latency: 10.0`).
    2.  Run the bulk test with high load: `GET /products/bulk/test?requests=10`.
    3.  Since the maximum pool is **5**, half of the requests should fail instantly with `503 Pool Exhausted`.
*   **In Datadog:** Look for the error spans. See the `db.pool.active` tag to confirm the pool was at `5/5`.

### 2. Experiment: Trace Detective (Graceful Degradation)
What happens when the system decides not to error, but to return "stale" data to save the user experience?

*   **The Chaos:**
    1.  Keep the Circuit Breaker **OPEN** (100% DB error).
    2.  Note that the API returns `200 OK` but with the field `"source": "fallback_emergency"`.
*   **APM Investigation:**
    1.  Go to **APM > Traces** and find one of these success requests.
    2.  Open the Flame Graph and look for the custom span **`logic.fallback`**.
    3.  Check the tags: `app.fallback_used: true` and `resilience.circuit_breaker.state: OPEN`.
    4.  **Discussion:** How does this tag help you proactively understand that the system is in survival mode?

### 3. Experiment: Memory Leak
Simulate an application that consumes memory without stopping.

*   **The Chaos:**
    1.  Run the command `POST /chaos/leak` several times in a row.
    2.  **Observe:** Monitor the `catalog.app.memory_leak_size` metric on your dashboard.

---
> [!TIP]
> **APM Tip:** Use the **Trace Map** in Datadog to visually see how the request "dies" at the Circuit Breaker before even trying to reach the database.
