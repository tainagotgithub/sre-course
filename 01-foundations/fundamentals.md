
## 1. Resilience and Scalability
> *The ability to grow without pain and fail without dying.*

### Scalability
It's not just about "handling more users", it's about how the system reacts to increased load.
* **Vertical (Scale Up):** Increasing the machine's capacity (More CPU/RAM). *Limit:* Cost and physical constraints.
* **Horizontal (Scale Out):** Increasing the number of machines. *Challenge:* Complexity of state management (database, sessions).

### Resilience & Chaos Engineering
* **Concept:** Resilience is a system's ability to recover from failures or degrade features gracefully (e.g., the video doesn't load, but the menu still works).
* **Chaos Engineering:** The practice of breaking things on purpose in a controlled environment.
    * *Objective:* Validate that database *failover* actually works before it breaks at 3 AM.

---

## 2. Automation and Toil (Boring Work)
> *If you need to log into the machine to fix it, you've already failed.*

### Toil
* **SRE Definition:** Manual, repetitive, tactical work that lacks long-term value and grows linearly with the service.
* **Examples:** Manually resetting a server, running log cleanup scripts by hand, creating user accounts via tickets.
* **Goal:** Google recommends limiting Toil to **50%** of an engineer's time. The rest should be project engineering.

### Automation
* **The Rule:** If you've done it 3 times, automate it.
* **Benefit:** Besides saving time, automation eliminates human error and documents the process via code (Infrastructure as Code).

> [!TIP]
> **Datadog Workflow Challenge:** Take a look at our current **Datadog Workflows**. Where do you see opportunities to automate repetitive tasks? Think about incident response, resource cleanup, or automated scaling actions.

---

## 3. Monitoring, Observability, and Metrics (SLI/SLO/SLA)
> *Turning feelings into data.*

### The Reliability Triad

#### 1. SLI (Service Level Indicator) - The Indicator
It's the "raw" metric that indicates the health of the service.
* *What to measure?* Latency, Error Rate, Saturation, Availability.

#### 2. SLO (Service Level Objective) - The Goal
It's the performance target for the SLI. This is where we define "user happiness".
* *Example:* "99.9% of requests should be served in < 200ms".
* *Note:* The SLO is internal. If violated, the engineering team stops everything to stabilize.

#### 3. SLA (Service Level Agreement) - The Contract
It's the formal promise to the customer, with penalties (money/credits).
* *Tip:* The SLA should always be **looser** than the SLO (to provide a buffer).

### Error Budget
The most important metric for negotiation between Product and Engineering.
* **Concept:** 100% availability is impossible and expensive. The Error Budget is the "slack" we can burn.
* **Practical Calculation:**
    * If the SLO is **99.9%** (three nines).
    * The Error Budget is **0.1%**.
    * **In time:** This allows for **~43 minutes** of downtime per month.
    * **Daily:** Allows for **1.44 minutes** per day.
* **Proactive Action:** Continuous monitoring warns when we are burning the budget too fast. If the budget runs out -> **Code Freeze** (no new features until the next month).

---

## 4. Capacity Management and Planning
> *Avoiding disastrous success.*

### Capacity Planning
Predicting how much resource (computational and financial) will be needed to support future growth.
* **Organic:** Natural growth in users month over month.
* **Inorganic:** Marketing events, launches, Black Friday.
* **Tools:** Load Testing to discover the breaking point before the customer does.

---

## 5. Incident Management and Post-Mortems
> *Don't waste a good crisis.*

### Incident Lifecycle
1.  **Identification:** The alert goes off (ideally before the customer complains).
2.  **Investigation:** Looking at dashboards and logs.
3.  **Resolution (Mitigation):** Stop the bleeding. *Focus:* Restore the service, not necessarily find the root cause now.
4.  **Recovery:** Cleanup and validation.
5.  **Review:** The Post-Mortem.

### Battle Tools
* **Runbook:** Step-by-step manuals ("Recipes") for execution during the stress of an incident.
* **ChatOps:** Centralizing incident communication in a channel (Slack/Teams) for a temporal record.

### Structure of an Effective Post-Mortem
It's not a bureaucratic document. It's a learning tool.
1.  **Summary:** What happened?
2.  **Timeline:** Detailed timeline (detected at 2:00 PM, mitigated at 2:15 PM).
3.  **Root Cause:** The 5 Whys.
4.  **Corrective Actions:** What will we do to ensure **this** specific error never happens again? (e.g., Improved monitoring, architecture changes).

---

## 6. Continuous Improvement and Culture

---

## Essential Bibliography

1.  **Site Reliability Engineering (Google)** - Beyer et al. (2016)
2.  **The Site Reliability Workbook** - Beyer et al. (2018)
3.  **The DevOps Handbook** - Kim et al. (2016)
4.  **Designing Data-Intensive Applications** - Kleppmann (2017)
