# Non-Functional Requirements
## Financial Intelligence Multi-Agent System

**Version:** 0.1.0  
**Status:** Draft  
**Last Updated:** 2026-04-28

---

## Table of Contents

1. [Performance](#1-performance)
2. [Availability](#2-availability)
3. [Caching Strategy](#3-caching-strategy)
4. [Scalability](#4-scalability)
5. [Reliability](#5-reliability)
6. [Security](#6-security)
7. [Observability](#7-observability)
8. [Maintainability](#8-maintainability)
9. [Data Integrity](#9-data-integrity)

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

## 5. Reliability

### 5.1 Agent and LLM Failure Handling

- The system shall apply exponential backoff with a maximum of 3 retries before escalating any agent or LLM failure
- On retry exhaustion the system shall return a user-facing error message indicating the system is experiencing difficulties and to try again later
- On retry exhaustion the system shall fire a developer alert via email containing a link to the monitoring system for immediate investigation
- The system shall notify the user via in-app notification and email when the issue is resolved and normal service is restored
- The primary LLM provider shall be Anthropic Claude
- The system shall maintain an open source model (e.g. Llama 3 or Mistral via a hosted inference endpoint) as a fallback LLM provider for reasoning failures
- For data retrieval failures the system shall fall back to cached data with a staleness warning rather than invoking the LLM fallback
- For reasoning failures where no cache applies the system shall route to the open source fallback LLM before surfacing a user-facing error

### 5.2 Message Queue Reliability

- All RabbitMQ queues shall be configured as durable, persisting messages to disk and surviving broker restarts
- All Kafka topics shall be configured with a replication factor of at least 3
- Both RabbitMQ and Kafka shall be deployed as replicated clusters
- On broker failure the system shall route to a healthy replica after exhausting retries against the failed broker
- Dead letter queues (DLQ) shall be configured for all queues — messages that exhaust maximum retries shall be routed to the DLQ rather than being silently dropped
- DLQ contents shall be monitored and reviewed as part of incident investigation

### 5.3 Data Pipeline Reliability

- Every pipeline run shall be assigned a globally unique Snowflake ID for tracking and auditability
- A distributed lock shall be acquired at pipeline start and released only on successful completion or retry exhaustion, preventing concurrent runs of the same pipeline
- Pipelines shall process data in micro-batches with checkpoints written after each successful batch
- On pipeline crash the system shall resume from the last successful checkpoint rather than restarting from scratch
- Each batch shall be identified by a composite ID of pipeline run ID and batch sequence number
- Every ingested record shall have a natural unique identifier appropriate to its data type:
  - News articles: URL hash
  - SEC filings: EDGAR accession number
  - Economic indicators: series ID + release date
  - OHLCV price data: ticker symbol + trading date
- The database shall enforce uniqueness constraints on these identifiers
- All pipeline writes shall use upsert logic — insert if not exists, skip if exists — ensuring idempotent processing under at-least-once delivery guarantees

### 5.4 Dead Man's Switch Monitoring

- Every scheduled pipeline shall emit a heartbeat event on each successful completion
- The monitoring system shall alert the developer if an expected heartbeat is not received within a defined tolerance window
- Silent pipeline failures — where the pipeline stops running without throwing an error — shall be treated with the same severity as explicit failures

---

## 6. Security

### 6.1 Authentication and Session Management

- The system shall implement JWT-based authentication
- JWT tokens shall be stored in HttpOnly cookies, inaccessible to JavaScript to prevent XSS-based token theft
- All state-changing requests shall require a CSRF token to protect against Cross Site Request Forgery attacks
- JWT tokens shall have a defined expiry window after which re-authentication is required
- Refresh token rotation shall be implemented to maintain sessions securely without requiring frequent re-authentication

### 6.2 Authorisation

- The system shall implement Role Based Access Control (RBAC) with at minimum two roles: user and administrator
- All API endpoints shall enforce authorisation checks — no endpoint shall be accessible without appropriate role validation
- Users shall only be able to access their own data — cross-user data access shall be explicitly prevented at the API and database query level

### 6.3 Input Validation and Injection Prevention

- All incoming API request payloads shall be validated against strict schemas before any processing occurs
- The system shall reject any request that does not conform to the defined schema with an appropriate error response
- All database queries shall use parameterised inputs or ORM-enforced schemas to prevent NoSQL injection attacks
- All content fetched from external sources shall be sanitised before rendering in the frontend to prevent XSS attacks
- User-provided content shall never be rendered as raw HTML

### 6.4 Prompt Injection Protection

- All user inputs shall be sanitised before being passed to LLM agents
- The orchestrator shall validate that inputs conform to expected query patterns before dispatch
- System prompts shall maintain clear privilege separation between trusted system instructions and untrusted user content
- LLM outputs shall be treated as untrusted and validated before being passed to downstream agents or rendered to users
- The Eval agent's validation loop provides a secondary layer of output integrity checking

### 6.5 API Security

- All API endpoints shall be served over HTTPS exclusively
- The system shall implement per-user API rate limiting to prevent abuse
- All external API keys and secrets shall be stored in environment variables or a secrets manager — never hardcoded or committed to version control
- Pre-commit hooks shall include secret scanning to prevent accidental credential commits

### 6.6 Object Storage Security

- All documents stored in object storage shall be private by default
- Document access shall be granted exclusively via presigned URLs with a defined expiry window
- Presigned URLs shall be generated on demand and never stored or reused

### 6.7 Security Headers

- The system shall set a Content Security Policy (CSP) header on all responses, restricting content loading to explicitly authorised sources and preventing execution of injected scripts
- The system shall set X-Frame-Options or an equivalent CSP frame-ancestors directive to prevent clickjacking via iframe embedding
- The system shall set X-Content-Type-Options: nosniff to prevent MIME-type sniffing attacks
- The system shall set Strict-Transport-Security (HSTS) to enforce HTTPS for all browser interactions
- The system shall set a Referrer-Policy header to control referrer information exposure and protect user privacy

### 6.8 Data Privacy

- User passwords shall be hashed using a strong adaptive hashing algorithm such as bcrypt or Argon2 — never stored in plain text
- Sensitive user data shall be encrypted at rest
- User data shall be isolated at the database query level — no query shall return data belonging to another user

---

## 7. Observability

### 7.1 Observability Stack

- The system shall use OpenTelemetry (OTEL) as the instrumentation and collection standard across all services and agents
- The observability backend shall consist of Prometheus for metrics, Grafana Tempo for distributed traces, Grafana Loki for logs, and Grafana for dashboards and alerting
- All services shall be instrumented with OTEL from day one — observability is not optional and shall not be retrofitted

### 7.2 Distributed Tracing

- The system shall emit distributed traces for every user interaction covering the full request lifecycle
- Traces shall capture: orchestrator query receipt, query decomposition, sub-agent dispatch and execution time per agent, eval agent validation, response assembly, and total end-to-end latency
- Traces shall identify the slowest agent in any given request chain
- Traces shall be queryable by user, by agent, by request type, and by time window
- All agent-to-agent calls shall be captured as child spans within the parent request trace

### 7.3 Pipeline Monitoring

- The system shall track the state of every data ingestion pipeline including current status, last successful run timestamp, run duration, and historical success and failure rates
- Every pipeline run shall emit a heartbeat event on successful completion, consumed by the dead man's switch monitor
- The system shall alert the developer if an expected pipeline heartbeat is not received within the defined tolerance window
- Pipeline metrics shall be exposed on a dedicated dashboard showing health status across all pipelines simultaneously

### 7.4 External API Monitoring

- The system shall track all calls to external data providers including latency per provider, error rate per provider, and HTTP status code distribution
- The system shall track rate limit consumption per provider, exposing current usage against daily and per-minute limits
- The system shall alert the developer when rate limit consumption for any provider exceeds 80% of the available budget within a given window
- Hourly breakdowns of external API call volume shall be available to identify peak consumption windows and inform scheduling decisions

### 7.5 Token and Cost Tracking

- The system shall track LLM token consumption per request, per agent, per user, and per time window
- Hourly token consumption data shall be available to identify peak usage windows and inform scheduling and optimisation decisions
- The system shall track which agents consume the most tokens to prioritise prompt optimisation efforts
- The system shall alert the developer when daily token consumption approaches a defined budget threshold

### 7.6 Application Performance Monitoring

- The system shall track request latency per API endpoint with p50, p95, and p99 percentile breakdowns
- The system shall track error rates per endpoint over rolling time windows
- The system shall alert the developer when p95 latency on the chat endpoint exceeds 45 seconds
- The system shall alert the developer when error rate on any endpoint exceeds a defined threshold over a rolling window

### 7.7 Health Checks

- Every application service shall expose a `/health` endpoint returning both liveness and readiness status
- Liveness indicates whether the service is running and able to respond
- Readiness indicates whether the service is ready to handle requests including database connectivity and dependency availability
- Prometheus shall scrape all health endpoints on a defined polling interval
- The system shall alert the developer after 3 consecutive health check failures on any service
- Internal cluster health for RabbitMQ, Kafka, and MongoDB shall be monitored via their native mechanisms and exposed to Grafana

### 7.8 Storage Monitoring

- The system shall monitor database storage capacity continuously
- The system shall emit a warning alert when storage utilisation reaches 75% of capacity
- The system shall emit a critical alert when storage utilisation reaches 90% of capacity

### 7.9 Alerting Summary

All alerts shall be delivered to the developer via email and shall include sufficient context for immediate investigation.

| Alert | Severity | Trigger |
|---|---|---|
| Pipeline heartbeat missed | Critical | Expected heartbeat not received within tolerance window |
| Service health check failed | Critical | 3 consecutive failures on any service |
| Agent crash after retry exhaustion | Critical | Retry limit exceeded on any agent |
| P95 chat latency exceeded | Warning | Chat p95 latency exceeds 45 seconds |
| Token budget threshold reached | Warning | Daily token consumption exceeds defined budget threshold |
| Rate limit threshold reached | Warning | Any provider exceeds 80% of rate limit budget |
| Error rate threshold exceeded | Warning | Endpoint error rate exceeds threshold over rolling window |
| DLQ depth growing | Warning | Dead letter queue depth exceeds defined threshold |
| Storage warning | Warning | Database storage reaches 75% capacity |
| Storage critical | Critical | Database storage reaches 90% capacity |

---

## 8. Maintainability

### 8.1 Code Quality

- The system shall use pre-commit hooks enforcing: code formatting, linting, static type checking, and secret scanning on every commit
- All code shall be statically typed
- Code style and formatting shall be enforced automatically rather than by convention

### 8.2 Testing Strategy

- The system shall maintain unit tests covering individual functions and components in isolation
- The system shall maintain integration tests covering interactions between components and external dependencies
- The system shall maintain end-to-end tests covering complete user-facing workflows
- The system shall maintain load tests validating system behaviour under the 100 concurrent user target
- The system shall maintain contract tests ensuring API contracts between services are not broken by changes
- The system shall maintain security audit checks including dependency vulnerability scanning via pip audit or equivalent on every CI run
- Agent evaluation shall be implemented at two levels: component evals per agent and system-level evals on end-to-end output quality

### 8.3 CI/CD

- The system shall use GitHub Actions for continuous integration and deployment
- Every pull request shall trigger the full test suite including unit, integration, contract, and security audit checks
- Load tests shall run on a scheduled cadence rather than on every pull request
- Deployments shall be automated on merge to main with no manual steps required

### 8.4 Data and Artifact Versioning

- The system shall use DVC for versioning data artifacts and pipeline outputs
- All changes to ingestion pipeline configurations shall be tracked and reproducible

### 8.5 Documentation

- All services and agents shall maintain up-to-date API and interface documentation
- Architectural decisions shall be recorded as Architecture Decision Records (ADRs) in the repository

---

## 9. Data Integrity

### 9.1 User Data Consistency

- User account data, profiles, preferences, and risk appetite shall be treated with strong consistency guarantees
- Changes to user preferences and risk appetite shall be reflected in all subsequent outputs within the user context summary TTL window of 1 hour

### 9.2 Report and Digest Immutability

- Generated reports and digests shall be immutable after generation
- No process shall modify a report or digest once it has been delivered to the user
- All reports and digests shall be stored with a generation timestamp and a record of the data sources and versions used

### 9.3 Agent Reasoning Audit Trail

- The system shall store the full reasoning trace for every agent interaction including: query received, sub-agents called, inputs and outputs per agent, eval agent verdicts, and final response
- Audit traces shall be retained for a minimum of 90 days
- Audit traces shall be queryable for debugging, evaluation, and incident investigation purposes

### 9.4 Data Retention Enforcement

- Data retention policies shall be enforced by an automated scheduled deletion job — no manual intervention required
- The deletion job shall run on a daily cadence and remove all records that have exceeded their defined retention window
- Deletion events shall be logged for auditability
- Before deleting expiring content the deletion job shall verify that the summarisation service has successfully incorporated the content into the relevant entity summary

### 9.5 Knowledge Graph Consistency

- Entity updates shall be propagated to the knowledge graph atomically — partial updates shall not be committed
- Knowledge graph consistency shall be verified as part of the ingestion pipeline completion check
