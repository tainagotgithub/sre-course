# Advanced Alerting & Incident Routing (Datadog + PagerDuty)

> *If everything is an emergency, nothing is. Alert fatigue is the silent killer of SRE teams.*

Creating dashboards is only half of the observability battle. The other half is ensuring the system can proactively notify humans when things go wrong—but **only** when human intervention is actually required.

---

## 1. Alerting Philosophy: Symptom vs. Cause
> *Alert on the user's pain, not the machine's state.*

The most common mistake in monitoring is alerting on infrastructure metrics (causes) instead of user-facing metrics (symptoms).

* **Bad Alert (Cause):** "CPU usage is at 90%". *Why is it bad?* If CPU is at 90% but response times are 50ms and no errors are occurring, the system is simply highly optimized. Waking someone up at 3 AM for this causes alert fatigue.
* **Good Alert (Symptom):** "Checkout API 99th percentile latency is > 2 seconds". *Why is it good?* This directly impacts the user's ability to buy products (Golden Signals). 
* **The SRE Approach:** Use the symptom to trigger the alert (PagerDuty) and use the causes (CPU, Memory, DB Locks) in the dashboards to investigate the root cause during the incident.

---

## 2. Composite Metrics and Complex Triggers (Datadog)
To create high-signal, low-noise alerts, we move away from simple thresholds and use **Composite Monitors** and **Metric Math**.

### Metric Math (Fractions and Ratios)
Instead of alerting on the absolute number of errors (which naturally spikes during high-traffic events like Black Friday), alert on the **Error Rate**.
* **Query example:** `sum(errors) / sum(total_requests) > 0.05` (Alert if the error rate exceeds 5% of total traffic).

### Composite Monitors (AND / OR Logic)
A Composite Monitor combines multiple individual monitors to reduce false positives.
* **Scenario:** You have a cluster of 10 nodes. 1 node crashing is handled automatically by Kubernetes (no alert needed). 3 nodes crashing is an emergency.
* **Setup:** 
  - Monitor A: `High Error Rate on API`
  - Monitor B: `Available Pods < 70%`
  - **Composite Monitor:** Trigger ONLY if `Monitor A AND Monitor B` are `True`.

### Outlier and Anomaly Detection
Datadog uses machine learning to evaluate historical trends rather than static thresholds.
* **Static Threshold:** `Traffic < 100 requests/sec` (Breaks on weekends or nights).
* **Anomaly Monitor:** `Traffic is outside the expected standard deviation for this day of the week and hour`.

---

## 3. Incident Routing & Priorities (PagerDuty)
Once an alert triggers, it needs to reach the right person with the correct level of urgency. PagerDuty acts as the routing engine.

### The Escalation Path
`Datadog Monitor -> PagerDuty Service -> Escalation Policy -> On-Call Schedule -> Target Engineer`

### Defining Incident Priorities (SEV Levels)
Not all alerts require waking someone up. A strict priority matrix is essential:

* **P1 (SEV-1) - Critical Business Impact:**
  - *Condition:* System is down or core functionality (e.g., Payments) is completely broken. SLO is burning rapidly.
  - *Action:* PagerDuty **High Urgency**. Calls the phone of the primary on-call engineer, overrides "Do Not Disturb", escalates to management if unacknowledged in 5 minutes.
* **P2 (SEV-2) - Major Degradation:**
  - *Condition:* Core feature is slow or failing for a subset of users. No workaround available.
  - *Action:* PagerDuty **High Urgency**. Phone call or loud push notification.
* **P3 (SEV-3) - Minor Issue / Warning:**
  - *Condition:* Non-critical feature is broken, or a backend job failed but will retry.
  - *Action:* PagerDuty **Low Urgency**. Sends an email or Slack message. Handled during next business hours. *Does not wake anyone up.*
* **P4/P5 - Informational:**
  - *Condition:* A deployment finished, or a server restarted successfully.
  - *Action:* Logged in a `#deployment-events` Slack channel. No PagerDuty incident created.

---

## 4. Anatomy of a Perfect Alert Payload
When a PagerDuty alert wakes an engineer up at 3 AM, they are groggy. The Datadog alert payload (`{{message}}` template) must provide immediate context.

**Checklist for an actionable alert:**
1. **Clear Name:** `[P1] Checkout API Error Rate > 5% in Production`
2. **Impact Statement:** "Users cannot complete purchases."
3. **Current Value:** `Triggered at: {{value}}`
4. **Runbook Link:** Immediate link to the documentation on how to fix/mitigate it: `[Runbook: Troubleshooting Checkout](https://wiki.company.com/runbooks/checkout)`
5. **Dashboard Link:** Direct link to the Datadog dashboard filtered by the affected environment.

**Datadog to PagerDuty Routing Example:**
```text
{{#is_alert}}
@pagerduty-Checkout-Service-High-Urgency
Please investigate immediately. 
Runbook: https://wiki.company.com/runbooks/checkout
{{/is_alert}}

{{#is_warning}}
@slack-checkout-alerts
Warning threshold reached. Please check during business hours.
{{/is_warning}}
```
