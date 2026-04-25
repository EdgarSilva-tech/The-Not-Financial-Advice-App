# Functional Requirements
## Financial Intelligence Multi-Agent System

**Version:** 0.1.0  
**Status:** Draft  
**Last Updated:** 2026-04-25

---

## Table of Contents

1. [Overview](#1-overview)
2. [User Management](#2-user-management)
3. [Entity Following](#3-entity-following)
4. [Data Ingestion](#4-data-ingestion)
5. [Weekly Digest](#5-weekly-digest)
6. [Conversational Chat Interface](#6-conversational-chat-interface)
7. [On Demand Research and Reports](#7-on-demand-research-and-reports)
8. [Trend and Momentum Surfacing](#8-trend-and-momentum-surfacing)
9. [Notifications and Alerts](#9-notifications-and-alerts)
10. [Appendix A — Sub-Agents](#appendix-a--sub-agents-tbd)

---

## 1. Overview

### 1.1 Purpose

This system provides a personalised financial research and intelligence platform for self-directed investors who conduct their own research. It aggregates data from multiple specialised sources, applies multi-agent reasoning, and delivers personalised insights, reports, and digests tailored to each user's followed entities and risk appetite.

### 1.2 Target User

Self-directed investors and researchers who actively follow financial markets, economic indicators, and specific companies or sectors, and who want aggregated, reasoned, and personalised financial intelligence without relying on generic tools.

### 1.3 V1 Scope

Version 1 is scoped to US markets, US-listed companies, US economic indicators, and US market indices. International markets and entities are out of scope for V1.

### 1.4 Key Principles

- The system provides information and surfaces patterns — it does not provide financial advice
- Suggestions are framed as "worth paying attention to" rather than prescriptive recommendations
- All outputs are grounded in retrieved data, not LLM training data alone
- The system prioritises availability over strict consistency, with explicit data freshness indicators on all outputs

---

## 2. User Management

- The system shall allow users to register using email and password
- The system shall authenticate users via JWT-based authentication
- The system shall maintain a user profile containing basic personal information
- The system shall allow users to define investment interests and preferred sectors as part of their profile
- The system shall allow users to define a risk appetite level: conservative, moderate, or aggressive
- The system shall use risk appetite to filter and frame outputs across all system features including reports, digests, trend surfacing, and chat responses
- The system shall store and maintain per-user history including conversations, generated reports, and followed entities
- The system shall maintain a distilled user context summary per user, updated by the summarisation service on relevant user events such as new conversations, preference changes, and new followed entities

---

## 3. Entity Following

> **V1 Scope: US entities only**

- The system shall allow users to follow individual US-listed companies
- The system shall allow users to follow US economic indicators (e.g. CPI, unemployment rate, Fed funds rate, GDP)
- The system shall allow users to follow US market indices (e.g. S&P 500, NASDAQ, Dow Jones)
- The system shall allow users to follow US market sectors (e.g. technology, energy, healthcare)
- The system shall surface entity-specific data, news, and analysis based on followed entities
- The system shall personalise all outputs based on the combination of followed entities and user risk appetite

---

## 4. Data Ingestion

### 4.1 Ingestion Pipelines

- The system shall maintain multiple independent ingestion pipelines, each operating at a cadence appropriate to its data type
- The system shall ingest market price data on a daily cadence, storing Open, High, Low, Close, and Volume (OHLCV) per entity per day as a permanent record
- The system shall cache intraday price data with a TTL of 24 hours, after which it is discarded in favour of the permanent daily OHLCV record
- The system shall ingest news and analyst commentary on a scheduled cadence of every few hours
- The system shall ingest economic indicator data aligned to official release schedules
- The system shall ingest SEC filings on a daily cadence via the EDGAR API
- The system shall ingest data continuously for all tracked entities regardless of which specific users follow them

### 4.2 Data Freshness and Availability

- The system shall tag all ingested data with a timestamp indicating when it was last fetched
- The system shall expose data freshness indicators to the user in all outputs
- The system shall prioritise availability over strict consistency, accepting that data may be slightly stale between ingestion cycles
- The system shall allow users to manually trigger a data refresh for a specific followed entity, bypassing cache and fetching the latest available data
- The system shall cache ingested data with a defined TTL per data type to avoid redundant external API calls

### 4.3 Data Retention

| Data Type | Retention Policy |
|---|---|
| Market prices (OHLCV) | Permanent |
| Economic indicator releases | Permanent |
| SEC filings | Permanent (minimum 3 years) |
| News articles | 90 days (full content), then summary only |
| Analyst commentary | 90 days (full content), then summary only |
| Intraday price cache | 24 hours |

### 4.4 Summarisation Service

- The system shall maintain a structured summary per tracked entity, organised into sections by data type: recent news, analyst sentiment, filing highlights, and market context
- The system shall update the relevant summary section when new content is ingested for that entity
- The system shall consolidate expiring content into the entity summary before permanent deletion of raw content
- The system shall treat entity summaries as first-class artifacts queryable by agents for report generation, digest generation, and chat responses
- Entity summaries shall serve as the primary knowledge input for agent operations, reducing the need for raw document retrieval
- The system shall maintain a separate distilled user context summary per user, updated on relevant user events
- The user context summary shall include risk appetite, followed entities, preferences, and summarised recent interaction history
- Entity summarisation shall be triggered by ingestion events
- User context summarisation shall be triggered by user interaction events
- Both summary types shall share the same underlying summarisation infrastructure but operate as separate pipelines

---

## 5. Weekly Digest

- The system shall generate a personalised weekly digest for each user based on their followed entities and risk appetite
- The digest shall contain three sections: Hottest Trends, Macro Economics, and For You
- The Hottest Trends section shall be generated by an agent reasoning over algorithmically computed signals across US markets, including price movements, volume anomalies, and news mention frequency
- The Macro Economics section shall summarise recent US economic indicator releases, Fed activity, and macro context, framed according to the user's risk appetite
- The For You section shall report on the user's followed entities with analysis framed according to their risk appetite
- The For You section shall include adjacent entity suggestions beyond explicitly followed entities, drawn from the same and related sectors
- The breadth of adjacent suggestions shall be proportional to user risk appetite: conservative profiles receive fewer and closer suggestions; aggressive profiles receive broader suggestions
- Digest generation shall consume entity summaries from the summarisation service as its primary knowledge input
- The system shall deliver the weekly digest both in-app and via email
- The system shall generate and deliver digests on Monday by default
- The system shall allow users to configure their preferred digest delivery day

---

## 6. Conversational Chat Interface

- The system shall restrict conversation to investment and finance related topics, declining to respond to unrelated queries
- The system shall maintain stateful conversation history per user across sessions
- The system shall load the distilled user context summary before processing any query, including risk appetite, followed entities, preferences, and summarised recent history
- The orchestrator shall decompose incoming queries into sub-questions informed by the loaded user context before dispatching to sub-agents
- The orchestrator shall dispatch sub-questions to relevant specialised sub-agents concurrently
- Each sub-agent shall use its own tools and data sources to answer its assigned sub-question
- Upon receiving sub-agent responses the orchestrator shall perform a self-validation step, evaluating whether the collected context is sufficient and coherent relative to the original query
- Based on self-validation the orchestrator shall decide to call additional sub-agents, re-query existing sub-agents, or proceed to answer
- The orchestrator shall enforce a maximum iteration limit on sub-agent calls to prevent unbounded reasoning loops
- If the confidence threshold is not reached within the maximum iterations the system shall ask the user a clarification question rather than returning a low confidence answer
- If the confidence threshold is reached the system shall return a personalised answer framed through the user's risk appetite and context
- All answers shall be factual and grounded in data retrieved by sub-agents rather than LLM training data alone

---

## 7. On Demand Research and Reports

- The system shall allow users to request research reports via the chat interface
- The orchestrator shall detect report generation as a distinct intent within the chat flow
- The orchestrator shall evaluate whether the requested topic is sufficiently scoped before proceeding
- If the topic is too broad the system shall ask a clarifying question to narrow the scope before initiating report generation
- The system shall allow reports to span multiple entities where the topic warrants it
- Report generation shall perform deep retrieval from raw data sources rather than relying on entity summaries
- All reports shall be personalised through the user's risk appetite, followed entities, and preferences
- Reports shall contain relevant news, latest developments, recent filings, financial analyst commentary, and agent reasoning over retrieved data
- All sources shall be cited within the report
- Report depth and length shall be proportional to topic scope with no fixed page limit
- Reports shall be generated as professional PDF documents
- Completed reports shall be stored in object storage and accessible via on-demand presigned URLs
- The system shall notify the user of report completion via both email and in-app notification
- The email notification shall contain a deep link to the presigned URL for direct download
- The system shall maintain a reports section in the application where users can view and download all previously generated reports

---

## 8. Trend and Momentum Surfacing

> **Note:** The algorithmic approach for hotness score computation is TBD and requires further research and design before implementation.

- The system shall track multiple specialised data sources continuously to identify emerging trends and momentum signals across followed entities
- The system shall use an algorithmic approach to compute trend and momentum signals, with agent reasoning applied over those signals
- The system shall expose trend and momentum signals via a market dashboard
- The dashboard shall display a hotness score per entity on a 0 to 100 scale representing current momentum and activity level
- The system shall personalise which trends are surfaced and emphasised based on user risk appetite and followed entities
- Conservative users shall see stability and risk-weighted signals emphasised
- Aggressive users shall see high momentum and high volatility signals emphasised

### 8.1 Candidate Signal Types (TBD — to be validated and formalised)

| Entity Type | Candidate Signals |
|---|---|
| Companies | Price momentum, volume anomalies, news mention frequency, earnings surprises |
| Sectors | Aggregate earnings beats, capital flows, analyst rating changes |
| Economic Indicators | Deviation from consensus forecasts, rate of change relative to historical patterns |
| Indices | Breadth indicators, volatility measures, relative strength |

---

## 9. Notifications and Alerts

- The system shall notify users via both in-app notifications and email
- The system shall send a notification upon weekly digest generation and delivery
- The system shall send a notification upon research report completion
- The system shall send a notification when significant trend or momentum signals are detected for followed entities
- Email notifications shall be delivered via Resend
- Email notifications for reports and digests shall contain a deep link to a presigned URL allowing the user to download the document directly from object storage
- In-app notifications shall be delivered in real time
- The system shall maintain a notification history per user accessible within the application
- Users shall be able to mark notifications as read
- Users shall be able to configure notification preferences, opting out of specific notification types if desired

---

## Appendix A — Sub-Agents (TBD)

The specialised sub-agents and their responsibilities, tools, and data sources are to be defined following completion of the functional requirements. Sub-agent design will be derived from the capabilities implied across sections 5, 6, 7, and 8.
