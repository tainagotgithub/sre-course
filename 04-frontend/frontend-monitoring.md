# Frontend and UX Monitoring

Unlike the backend, where we focus on CPU and database latency, in the frontend, the "truth" lies in the user's browser. Monitoring the interface means ensuring the experience is fast, functional, and free of visible errors.

---

## 1. Synthetic Monitoring

Synthetic tests are robots that simulate user behavior at regular intervals (e.g., every 5 minutes) from different global locations.

### Why use it?
*   **Proactive Detection:** You find out the login is broken before the first customer complains.
*   **Performance Baseline:** Measures page speed under ideal and constant conditions.
*   **SLA Monitoring:** Proves the site was "up" from a perspective external to your infrastructure.

### How to configure in Datadog:
1.  Go to **UX Monitoring** -> **Synthetics Tests**.
2.  Click **New Test** -> **Browser Test**.
3.  **Define Requests:** Enter your application's URL (e.g., `https://myapp.com`).
4.  **Select Locations:** Choose where the robot will access from (e.g., São Paulo, Virginia, Tokyo).
5.  **Recording Steps:** Use the Datadog extension to "record" a flow (e.g., "Click home" -> "Fill search" -> "Click buy").
6.  **Set Assertion:** Define what validates success (e.g., "The text 'Success' must appear on screen").
7.  **Alert Conditions:** Configure to notify the team if the test fails in more than 2 locations simultaneously.

---

## 2. RUM (Real User Monitoring)

While Synthetics are robots, **RUM** collects data from **real users**.

### What Frontend cares about:
*   **Core Web Vitals (Google):**
    *   **LCP (Largest Contentful Paint):** How long does it take for the largest content to load? (Goal: < 2.5s)
    *   **FID (First Input Delay):** How long does the site take to react to the first click? (Goal: < 100ms)
    *   **CLS (Cumulative Layout Shift):** Does content "jump" on the screen while loading? (Goal: < 0.1)
*   **Resource Errors:** Broken images (404) or failures in third-party scripts (Analytics, Pixels).
*   **Long Tasks:** JavaScript scripts that block the main thread for more than 50ms, causing "stuttering".

---

## 3. Error and Exception Tracking

JavaScript errors on the client often don't reach the server logs. This is where **Error Tracking** tools come in.

### Tool References:
*   **Datadog Error Tracking:** Integrated with RUM, aggregates similar errors and shows the "bread-crumb trail" (what the user clicked before the error).
*   **Rollbar / Sentry:** Specialists in capturing browser exceptions, with *Source Maps* support (allows seeing the error in your original code, not minified code).
*   **LogRocket / FullStory:** Allows "replaying" the user session (video) to see exactly what they did to trigger the bug.

---

## Suggested Exercise
1.  Access Datadog (or a similar tool).
2.  Create a basic **Uptime Monitor** (HTTP Check) for the homepage.
3.  Google the "LCP" of the site you use most and understand why it is fast or slow.

---
> [!IMPORTANT]
> **Golden Tip:** Synthetic tests tell you if the site is **ALIVE**. RUM tells you if the site is **GOOD**. You need both.
