# Chaos Engineering Lab: sre-lab

This directory contains a simple FastAPI application that simulates a product catalog service. It was designed to be used in a Chaos Engineering laboratory, allowing for the controlled injection of latency, failures, and CPU stress to test system resilience.

## Simplified Architecture

*   **API Gateway** (simulated by the client)
*   **`sre-lab`** (this FastAPI application)
    *   Tries to fetch products from a **Redis Cache** (simulated)
    *   If not found, fetches from a **Postgres Database** (simulated)

## How to Run the Application

You can run the application locally (directly with Python) or using Docker.

### Option 1: Run Locally (Recommended for the Lab)

1.  **Navigate to the `lab` directory:**
    ```bash
    cd lab
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the application:**
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ```
    *   The `--reload` flag is useful for development as it automatically restarts the server when you save a file.
    *   To start with DB latency from the beginning (e.g., 3 seconds):
        ```bash
        DB_LATENCY_SECONDS=3 uvicorn main:app --host 0.0.0.0 --port 8000 --reload
        ```

### Option 2: Run with Docker

1.  **Navigate to the `lab` directory:**
    ```bash
    cd lab
    ```
2.  **Build the Docker image:**
    ```bash
    docker build -t sre-lab .
    ```
3.  **Run the Docker container:**
    ```bash
    docker run -p 8000:8000 sre-lab
    ```
    *   To start with DB latency from the beginning (e.g., 3 seconds):
        ```bash
        docker run -p 8000:8000 -e DB_LATENCY_SECONDS=3 sre-lab
        ```

## Accessing the Application and Swagger UI

After starting the application, you can access it:

*   **Main API:** `http://localhost:8000/products/{id}` (e.g., `http://localhost:8000/products/1`)
*   **Health Check:** `http://localhost:8000/health`
*   **Swagger UI (Interactive Documentation and Chaos Control):** `http://localhost:8000/docs`

## Injecting Chaos (Chaos Engineering)

The Swagger UI (`http://localhost:8000/docs`) is your control panel for injecting chaos. Use the `POST /chaos/configure` endpoint to control the experiments.

### Chaos Control Endpoint: `POST /chaos/configure`

This endpoint allows you to configure all chaos parameters at runtime:

*   `db_latency` (float): Latency in seconds for simulated database calls.
*   `db_failure_rate` (float): Failure rate (0.0 to 1.0) for simulated database calls.
*   `cache_failure_rate` (float): Failure rate (0.0 to 1.0) for simulated cache calls.
*   `cpu_stress` (boolean): Enables/disables CPU stress on the service.
*   `cb_threshold` (int): Threshold of consecutive database failures to open the **Circuit Breaker**. (Default: `5`)

### New Resilience Features

1.  **Circuit Breaker:** If the database fails `cb_threshold` times in a row, the circuit opens, and the system starts responding instantly with a `503` error, protecting the infrastructure.
2.  **Graceful Degradation (Fallback):** With the circuit open, the API will try to return data from an emergency cache to maintain minimum availability.
3.  **Dynamic Saturation:** Database latency increases as the volume of concurrent requests grows.
4.  **Connection Pool:** The simulated database has a limit of **5 connections**. If requests take too long and the pool is exhausted, new calls fail with `503 Pool Exhausted`.

**Usage Examples in Swagger UI:**

*   **Enable Fast Circuit Breaker (Threshold 2):**
    ```json
    {
      "db_latency": 0.0,
      "db_failure_rate": 1.0,
      "cache_failure_rate": 0.0,
      "cpu_stress": false,
      "cb_threshold": 2
    }
    ```
*   **Simulate Overload (Saturation and Pool):**
    Use the `GET /products/bulk/test?requests=15` endpoint to see the pool exhaust and latency rise.

### Other Chaos Endpoints:

*   `POST /chaos/reset`: Resets all chaos settings to default.
*   `POST /chaos/clear_cache`: Clears the performance cache.
*   `POST /chaos/leak?items=1000`: Simulates a memory leak to observe the impact on GC and telemetry.

## Performing the Chaos Engineering Lab

With this application, you can follow the "Simulated Practical Lab" described in the `lab.md` file (or your notes) to:

1.  **Define the Steady State:** Observe the normal behavior of the API.
2.  **Formulate a Hypothesis:** Predict what will happen when injecting a specific type of chaos.
3.  **Inject Chaos:** Use the `/chaos/*` endpoints to apply stress.
4.  **Observe Results:** Monitor the API (latency, errors) and the application console.
5.  **Analyze and Discuss:** Compare results with your hypothesis and identify weak points.
6.  **Propose Corrective Actions:** Think of resilience patterns (timeouts, circuit breakers, fallbacks) to mitigate the issues found.
