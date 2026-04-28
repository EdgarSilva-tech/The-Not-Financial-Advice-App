# Non-Functional Requirements
## Financial Intelligence Multi-Agent System

**Version:** 0.1.0  
**Status:** Draft — Partially Complete  
**Last Updated:** 2026-04-28

---

## Table of Contents

1. [Performance](#1-performance)
2. [Availability](#2-availability)
3. [Caching Strategy](#3-caching-strategy)
4. [Scalability](#4-scalability)
5. [Reliability](#5-reliability-tbd)
6. [Security](#6-security-tbd)
7. [Observability](#7-observability-tbd)
8. [Maintainability](#8-maintainability-tbd)
9. [Data Integrity](#9-data-integrity-tbd)

---

## 1. Performance

### 1.1 Chat Interface

- The system shall begin streaming a response within **3 seconds** of query receipt (time to first token)
- Simple queries shall complete streaming within **15 seconds**
- Complex multi-agent queries shall complete streaming within **45 seconds**
- The system shall stream responses token by token rather than returning complete responses
- The system shall notify the user in real time if response time is expected to exceed normal thresholds due to query complexity or system load

### 1.2 Report Generation

- Reports shall be generated and delivered within **10 minutes** of request
- The user shall be notified immediately upon report completion via in-app notification and email

### 1.3 Digest Generation

- Weekly digests shall be fully generated and delivered by **10:00 local time** on the user's configured delivery day
- The digest generation pipeline shall begin well in advance of the delivery deadline to ensure reliable on-time delivery

### 1.4 Trend and Momentum Dashboard

- Hotness scores shall be updated **twice daily** on trading days:
  - **Midday update:** 13:00 ET (approximately midpoint of NYSE trading hours)
  - **End of day update:** 16:30 ET (30 minutes after NYSE close, allowing closing data to settle)
- Hotness scores remain static between scheduled updates
- The timestamp of the last score update shall be visible to the user at all times

---

## 2. Availability

### 2.1 Uptime Target

- The system shall target **99.9% uptime**, equivalent to approximately 8.7 hours of downtime per year

### 2.2 Degraded Mode Behavior

- When an external data source is unavailable the system shall serve cached or summarised data rather than failing
- Stale data shall never be served silently — all outputs shall display the timestamp of the most recent successful data fetch
- If no cached data exists for an unavailable source the system shall inform the user which source is unavailable and answer using all available data from other sources
- The system shall prioritise availability over strict consistency across all features

### 2.3 Manual Refresh Under Degraded Conditions

- If a user triggers a manual data refresh and the relevant source is unavailable the system shall queue the refresh request rather than failing immediately
- The system shall inform the user that it is experiencing difficulties and will complete the refresh as soon as possible
- The system shall notify the user via in-app notification when the queued refresh eventually completes

---

## 3. Caching Strategy

Caching serves dual purposes in this system: performance optimisation to reduce redundant external API calls, and a reliability mechanism to serve data during source outages.

| Data Type | Cache TTL | Rationale |
|---|---|---|
| Intraday price data | 24 hours | Discarded after permanent daily OHLCV record is written |
| News articles | 4 hours | Aligned to ingestion cadence of every few hours |
| Entity summaries | 12 hours | Updated by ingestion events; manual refresh available |
| Economic indicators | 24 hours | Release schedule driven; rarely changes intraday |
| SEC filings | 24 hours | Aligned to daily ingestion cadence |
| Hotness scores | Until next scheduled update | Midday (13:00 ET) and EOD (16:30 ET) updates define windows |
| User context summary | 1 hour | Updated on user events; should remain relatively fresh |

---

## 4. Scalability

### 4.1 Concurrent User Target

- The system shall support a minimum of **100 concurrent users** in V1

### 4.2 Chat Scalability

- Chat service components shall be stateless and horizontally scalable
- The system shall handle up to **800 simultaneous sub-agent calls** under peak chat load
- This figure is derived from 100 concurrent users each triggering an average of 8 sub-agent calls per query
- External API rate limits shall be handled gracefully with retry logic and exponential backoff across all agents

### 4.3 Report Generation Scalability

- Report generation shall be processed via a task queue with controlled concurrency limits
- Concurrency limits prevent simultaneous report requests from exhausting LLM API budgets or compute resources
- Queued reports shall be processed in order with the user notified upon completion

### 4.4 Digest Generation Scalability

- Digest generation shall use a staggered pipeline to avoid thundering herd behaviour at delivery time
- Generation shall begin well before the 10:00 delivery target, processing users progressively rather than simultaneously
- Specific stagger interval TBD based on average digest generation time during testing

---

## 5. Reliability (TBD)

> To be defined. Areas to cover:
> - Agent failure and crash recovery mid reasoning loop
> - LLM API timeout and error handling
> - Sub-agent timeout behavior and partial result handling
> - Retry strategies and circuit breaker patterns
> - Message queue durability guarantees
> - Pipeline failure alerting and recovery

---

## 6. Security (TBD)

> To be defined. Areas to cover:
> - JWT authentication and token expiry
> - API rate limiting per user
> - Presigned URL expiry windows
> - Data isolation between users
> - Secret management and environment variable handling
> - Input validation and prompt injection protection for LLM inputs

---

## 7. Observability (TBD)

> To be defined. Areas to cover:
> - OpenTelemetry instrumentation across all services and agents
> - Distributed tracing for multi-agent reasoning chains
> - Metrics: latency per agent, token usage, pipeline completion times, error rates
> - Logging standards and structured log format
> - Alerting thresholds for latency, error rate, and pipeline failures
> - Dashboard design for system health monitoring

---

## 8. Maintainability (TBD)

> To be defined. Areas to cover:
> - Code quality standards and pre-commit hooks
> - Testing strategy: unit, integration, and system-level evals
> - DVC for data and model artifact versioning
> - CI/CD pipeline design
> - Documentation standards
> - Agent evaluation framework at component and system level

---

## 9. Data Integrity (TBD)

> To be defined. Areas to cover:
> - Consistency guarantees on user account and profile data
> - Report and digest immutability after generation
> - Audit trail for agent reasoning chains
> - Data retention enforcement and deletion guarantees
> - Knowledge graph consistency on entity updates
