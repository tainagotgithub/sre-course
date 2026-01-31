import os
# --- Datadog Integration ---
# patch_all() MUST be called as early as possible to instrument libraries
try:
    # Force service and environment to ensure visibility in Datadog
    os.environ["DD_SERVICE"] = "sre-lab"
    os.environ["DD_ENV"] = "development"
    os.environ["DD_VERSION"] = "1.1.0"

    from ddtrace import tracer, patch, patch_all
    patch_all()
    # In FastAPI, trace usually comes from Starlette
    patch(starlette=True, fastapi=True)
    
    from datadog import statsd, initialize
    initialize(statsd_host=os.getenv("DD_AGENT_HOST", "localhost"), 
               statsd_port=int(os.getenv("DD_DOGSTATSD_PORT", 8125)))
except ImportError:
    statsd = None

import asyncio
import random
import time
from typing import Dict, Any
from fastapi import FastAPI, HTTPException

app = FastAPI(
    title="Catalog Service (SRE Lab with Datadog)",
    description="API to simulate a catalog service with chaos injection, instrumented with Datadog.",
    version="1.1.0",
)

# --- Chaos Simulation State ---
MOCK_DB_LATENCY_SECONDS = float(os.getenv("DB_LATENCY_SECONDS", "0.0"))
MOCK_DB_FAILURE_RATE = float(os.getenv("DB_FAILURE_RATE", "0.0"))
MOCK_CACHE_FAILURE_RATE = float(os.getenv("CACHE_FAILURE_RATE", "0.0"))
CPU_STRESS_ENABLED = os.getenv("CPU_STRESS_ENABLED", "false").lower() == "true"


# --- Component Simulation ---
product_cache: Dict[str, Dict[str, Any]] = {}
mock_database: Dict[str, Dict[str, Any]] = {
    "1": {"id": "1", "name": "Gamer Laptop", "price": 7500.00, "description": "Powerful for gaming and work."},
    "2": {"id": "2", "name": "Ultrawide Monitor", "price": 2200.00, "description": "Total immersion with a curved screen."},
    "3": {"id": "3", "name": "Mechanical Keyboard", "price": 450.00, "description": "Cherry MX Red switches."},
    "4": {"id": "4", "name": "Wireless Mouse", "price": 300.00, "description": "Ergonomic and high precision."},
}

# --- Emergency Cache (Fallback) ---
fallback_static_cache = {
    "1": {"id": "1", "name": "Laptop (Emergency Cache)", "price": 7500.00, "description": "Static fallback info."},
    "2": {"id": "2", "name": "Monitor (Emergency Cache)", "price": 2200.00, "description": "Static fallback info."},
}

# Memory leak manager
memory_leak_list = []

# --- Chaos Helper Functions ---
def stress_cpu(duration_seconds: float = 0.5):
    """Function that consumes CPU for a set period."""
    start_time = time.time()
    while time.time() - start_time < duration_seconds:
        _ = 1 + 1

# --- Advanced Resilience Patterns ---

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.last_failure_time = 0

    def record_failure(self):
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.last_failure_time = time.time()
            self.state = "OPEN"
            print("CIRCUIT BREAKER: State changed to OPEN")
            if statsd: statsd.gauge("catalog.circuit_breaker.state", 1)

    def record_success(self):
        self.failures = 0
        self.state = "CLOSED"
        if statsd: statsd.gauge("catalog.circuit_breaker.state", 0)

    def can_execute(self) -> bool:
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                print("CIRCUIT BREAKER: State changed to HALF_OPEN")
                if statsd: statsd.gauge("catalog.circuit_breaker.state", 0.5)
                return True
            if statsd: statsd.gauge("catalog.circuit_breaker.state", 1)
            return False
        if statsd: statsd.gauge("catalog.circuit_breaker.state", 0)
        return True

db_circuit_breaker = CircuitBreaker()

class SaturationManager:
    def __init__(self):
        self.requests_last_minute = []
        self.threshold = 10  # Starts degrading after 10 reqs/10s

    def record_request(self):
        now = time.time()
        self.requests_last_minute.append(now)
        # Clear requests older than 10 seconds (for fast lab feedback)
        self.requests_last_minute = [t for t in self.requests_last_minute if now - t < 10]

    @property
    def current_load(self):
        return len(self.requests_last_minute)

    @property
    def dynamic_latency(self):
        if self.current_load > self.threshold:
            # Increase 0.5s for each request above threshold
            return (self.current_load - self.threshold) * 0.5
        return 0.0

db_saturation = SaturationManager()

class ConnectionPool:
    def __init__(self, max_size: int = 5):
        self.max_size = max_size
        self.active_connections = 0

    def acquire(self):
        if self.active_connections >= self.max_size:
            if statsd: statsd.increment("catalog.db.pool.exhausted")
            return False
        self.active_connections += 1
        if statsd: statsd.gauge("catalog.db.pool.active", self.active_connections)
        return True

    def release(self):
        self.active_connections = max(0, self.active_connections - 1)
        if statsd: statsd.gauge("catalog.db.pool.active", self.active_connections)

db_pool = ConnectionPool(max_size=5)

# --- Application Endpoints ---
@app.get("/")
async def root():
    """ Welcome page with resilience status. """
    return {
        "message": "Welcome to the ADVANCED Chaos Engineering Lab!",
        "system_status": {
            "circuit_breaker": db_circuit_breaker.state,
            "db_load": db_saturation.current_load,
            "db_dynamic_latency": f"{db_saturation.dynamic_latency}s"
        },
        "useful_endpoints": {
            "documentation": "/docs",
            "health_check": "/health",
            "example_product": "/products/1",
            "bulk_retries_test": "/products/bulk/test"
        }
    }

@app.get("/products/{product_id}", response_model=Dict[str, Any])
async def get_product(product_id: str):
    """
    Fetches product info with Circuit Breaker and Saturation.
    """
    print(f"Received request for product_id: {product_id}")

    if CPU_STRESS_ENABLED:
        stress_cpu()

    # 1. Try to fetch from cache
    try:
        if random.random() < MOCK_CACHE_FAILURE_RATE:
            raise ConnectionError("Simulated Cache is unavailable")
        
        if product_id in product_cache:
            if statsd: statsd.increment("catalog.cache.hit")
            return {"source": "cache", "data": product_cache[product_id]}
        else:
            if statsd: statsd.increment("catalog.cache.miss")

    except Exception as e:
        print(f"ERROR: Failed to access cache: {e}.")

    # 2. Fetch from DB (with Circuit Breaker and Pool)
    if not db_circuit_breaker.can_execute():
        if statsd: statsd.increment("catalog.circuit_breaker.rejected")
        
        # --- FALLBACK LOGIC (APM Interaction) ---
        with tracer.trace("logic.fallback", resource="Emergency Cache") as span:
            span.set_tag("resilience.circuit_breaker.state", "OPEN")
            if product_id in fallback_static_cache:
                span.set_tag("app.fallback_used", "true")
                if statsd: statsd.increment("catalog.fallback.hit")
                return {
                    "source": "fallback_emergency", 
                    "data": fallback_static_cache[product_id],
                    "note": "Circuit Open! Returning emergency data."
                }
        
        raise HTTPException(
            status_code=503, 
            detail="Circuit Breaker is OPEN and no fallback available."
        )

    if not db_pool.acquire():
        with tracer.trace("db.pool_error") as span:
            span.set_tag("db.pool.active", db_pool.active_connections)
            span.set_tag("db.pool.max", db_pool.max_size)
            span.error = 1
        raise HTTPException(status_code=503, detail="Database Connection Pool Exhausted")

    db_saturation.record_request()
    
    # Create custom span for DB Query
    with tracer.trace("db.query", resource="MockPostgres") as span:
        span.set_tag("db.pool.active", db_pool.active_connections)
        span.set_tag("product.id", product_id)

        try:
            if random.random() < MOCK_DB_FAILURE_RATE:
                db_circuit_breaker.record_failure()
                span.set_tag("error.message", "Simulated DB Failure")
                raise ConnectionError("Simulated DB is unavailable")

            # Latency = Manual value + Dynamic Saturation
            total_latency = MOCK_DB_LATENCY_SECONDS + db_saturation.dynamic_latency
            
            if total_latency > 0:
                print(f"Simulating total DB latency: {total_latency}s (Injected: {MOCK_DB_LATENCY_SECONDS}s, Saturation: {db_saturation.dynamic_latency}s)")
                await asyncio.sleep(total_latency)

            product_data = mock_database.get(product_id)
            
            if not product_data:
                span.set_tag("product.found", "false")
                raise HTTPException(status_code=404, detail="Product not found")

            db_circuit_breaker.record_success()
            product_cache[product_id] = product_data
            
            if statsd:
                statsd.gauge("catalog.db.load", db_saturation.current_load)
                statsd.histogram("catalog.db.query.duration", total_latency)
                statsd.gauge("catalog.db.latency.total", total_latency)

            return {"source": "database", "data": product_data, "latency_info": f"{total_latency}s"}

        except Exception as e:
            db_circuit_breaker.record_failure()
            span.set_tag("error.type", type(e).__name__)
            if not isinstance(e, HTTPException):
                raise HTTPException(status_code=500, detail=str(e))
            raise
        finally:
            db_pool.release()

@app.get("/products/bulk/test")
async def bulk_test(requests: int = 15):
    """
    Simulates a 'Retry Storm' or traffic spike to test saturation and Circuit Breaker.
    """
    tasks = [get_product("1") for _ in range(requests)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    summary = {
        "total": requests,
        "success": len([r for r in results if isinstance(r, dict)]),
        "failed": len([r for r in results if not isinstance(r, dict)]),
    }
    return {"message": "Bulk test completed", "summary": summary}

@app.get("/health")
async def health_check():
    """ Simple health check endpoint. """
    return {"status": "ok", "circuit_breaker": db_circuit_breaker.state}

# --- Chaos Control Endpoints ---
@app.post("/chaos/configure")
async def configure_chaos(
    db_latency: float = 0.0,
    db_failure_rate: float = 0.0,
    cache_failure_rate: float = 0.0,
    cpu_stress: bool = False,
    cb_threshold: int = 5
):
    """Single endpoint to configure all chaos parameters."""
    global MOCK_DB_LATENCY_SECONDS, MOCK_DB_FAILURE_RATE, MOCK_CACHE_FAILURE_RATE, CPU_STRESS_ENABLED
    
    MOCK_DB_LATENCY_SECONDS = max(0, db_latency)
    MOCK_DB_FAILURE_RATE = max(0, min(1, db_failure_rate))
    MOCK_CACHE_FAILURE_RATE = max(0, min(1, cache_failure_rate))
    CPU_STRESS_ENABLED = cpu_stress
    db_circuit_breaker.failure_threshold = cb_threshold

    if statsd:
        statsd.gauge("catalog.chaos.db_latency", MOCK_DB_LATENCY_SECONDS)
        statsd.gauge("catalog.chaos.db_failure_rate", MOCK_DB_FAILURE_RATE)
        statsd.gauge("catalog.chaos.cache_failure_rate", MOCK_CACHE_FAILURE_RATE)
        statsd.gauge("catalog.chaos.cpu_stress_enabled", 1 if CPU_STRESS_ENABLED else 0)
        statsd.gauge("catalog.chaos.cb_threshold", cb_threshold)


    return {
        "message": "Chaos configuration updated.",
        "settings": {
            "db_latency_seconds": MOCK_DB_LATENCY_SECONDS,
            "db_failure_rate": MOCK_DB_FAILURE_RATE,
            "cache_failure_rate": MOCK_CACHE_FAILURE_RATE,
            "cpu_stress_enabled": CPU_STRESS_ENABLED,
            "circuit_breaker_threshold": cb_threshold
        }
    }

@app.post("/chaos/reset")
async def reset_chaos():
    """Resets everything and clears the Circuit Breaker."""
    db_circuit_breaker.record_success()
    return await configure_chaos()

@app.post("/chaos/clear_cache")
async def clear_cache():
    """ Clears the simulated cache. """
    global product_cache
    product_cache = {}
    return {"message": "Cache cleared successfully."}

@app.post("/chaos/leak")
async def simulate_leak(items: int = 1000):
    """Simulates a memory leak to observe in Datadog."""
    global memory_leak_list
    for i in range(items):
        memory_leak_list.append("A" * 1024) # 1KB per item
    
    if statsd:
        statsd.gauge("catalog.app.memory_leak_size", len(memory_leak_list))
    
    return {"message": f"Injected {items}KB into memory.", "total_items": len(memory_leak_list)}
