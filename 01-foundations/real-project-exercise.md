# Day 1 Challenge: Applying SLIs, SLOs, and SLAs

This exercise is designed for you to apply the concepts of **SLI**, **SLO**, and **SLA** in real-world scenarios from our operation. Since you know the business context of the **Everest** project, your challenge is to define the indicators that actually matter for it.

---

## Recap: What are we defining?

### 1. SLI (Service Level Indicator)
It's the **metric**. What do we measure to know if the system is working?
*   **Common examples:**
    *   *Availability:* Percentage of successful requests (HTTP 2xx/3xx).
    *   *Latency:* Time in milliseconds to complete an operation (P95 or P99).
    *   *Quality/Integrity:* Percentage of data processed without loss or error.

### 2. SLO (Service Level Objective)
It's the **target**. What level of service do we promise to the internal team or the business?
*   **Common examples:**
    *   99.9% availability per month.
    *   95% of requests answered in less than 200ms.
    *   File processing completed in less than 5 minutes.

### 3. SLA (Service Level Agreement)
It's the **contract/consequence**. What happens to the external customer if the SLO is broken? 
*   *Note:* Not every system has an SLA (especially internal ones), but all must have an SLO.

---

## Your Task: Practical Exercise

Based on your technical and business knowledge of the project, define the structure below:

### Scenario 1: Everest Project
*   **Proposed SLIs:** (List 2 to 3 critical metrics)
*   **Suggested SLOs:** (Define the ideal targets for each metric)
*   **What is the business impact if this SLO is broken?**
*   **How would the Error Budget of this project affect deployments?**

---

## Deliverable
Prepare a simple table:

| System | Metric (SLI) | Target (SLO) | Justification (Why does this matter?) |
| :--- | :--- | :--- | :--- |
| **Everest** | | | |

---
> [!TIP]
> **Mentor's Advice:** A good SLO is one that, if broken, actually makes someone care. If the SLO breaks and no one complains, either the metric is wrong or the target is too strict. 
