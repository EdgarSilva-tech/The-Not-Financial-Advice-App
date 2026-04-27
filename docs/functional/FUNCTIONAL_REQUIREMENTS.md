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


| Data Type                   | Retention Policy                          |
| --------------------------- | ----------------------------------------- |
| Market prices (OHLCV)       | Permanent                                 |
| Economic indicator releases | Permanent                                 |
| SEC filings                 | Permanent (minimum 3 years)               |
| News articles               | 90 days (full content), then summary only |
| Analyst commentary          | 90 days (full content), then summary only |
| Intraday price cache        | 24 hours                                  |


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


| Entity Type         | Candidate Signals                                                                  |
| ------------------- | ---------------------------------------------------------------------------------- |
| Companies           | Price momentum, volume anomalies, news mention frequency, earnings surprises       |
| Sectors             | Aggregate earnings beats, capital flows, analyst rating changes                    |
| Economic Indicators | Deviation from consensus forecasts, rate of change relative to historical patterns |
| Indices             | Breadth indicators, volatility measures, relative strength                         |


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

## Appendix A — Sub-Agents

## Overview

The system is composed of three categories of agents:


| Category          | Description                                                        |
| ----------------- | ------------------------------------------------------------------ |
| **Orchestration** | Manage query decomposition, routing, validation, and clarification |
| **Asset Class**   | Own domain-specific data retrieval and analysis per asset type     |
| **Philosophy**    | Apply investment framework lenses over asset class agent outputs   |


Asset class agents own **what** data gets retrieved. Philosophy agents own **how** that data gets interpreted and framed. The orchestrator decides **which combination** gets activated per user per query based on the loaded user context summary.

---

## Orchestration Agents

### Orchestrator

**Responsibility:** The central coordinator of the multi-agent system. Manages the full lifecycle of every user interaction from query receipt to response delivery.

**Behavior:**

- Loads the distilled user context summary before processing any query
- Detects query intent — standard chat, report generation request, or trend inquiry
- Decomposes queries into sub-questions informed by user context
- Dispatches sub-questions concurrently to relevant asset class agents
- Activates the appropriate philosophy agents based on user profile
- Delegates to the Eval agent for self-validation after each round of sub-agent responses
- Decides whether to call additional agents, re-query existing agents, or proceed to answer
- Enforces maximum iteration limits on reasoning loops
- Delegates to the Clarification agent when confidence threshold is not met
- Assembles and returns the final personalised response

**Tools & Data Sources:**

- User context summary (via Summarisation Service)
- All sub-agent outputs
- No direct external data source access

---

### Eval Agent

**Responsibility:** Validates the sufficiency and coherence of collected sub-agent context relative to the original query. Acts as the quality gate in the orchestrator's reasoning loop.

**Behavior:**

- Receives the original query, user context, and current sub-agent outputs
- Evaluates whether the collected information is sufficient to answer the query accurately
- Assigns a confidence score to the current state of information
- Returns a structured verdict: sufficient, insufficient with specific gaps identified, or ambiguous
- The orchestrator acts on this verdict to decide next steps

**Tools & Data Sources:**

- No direct external data source access
- Operates purely over orchestrator-provided context

---

### Clarification Agent

**Responsibility:** Formulates precise, helpful clarification questions when the orchestrator cannot reach the confidence threshold within the maximum iteration limit.

**Behavior:**

- Receives the original query, user context, and the Eval agent's identified gaps
- Formulates a single focused clarification question that would resolve the most critical gap
- Ensures the question is framed in plain language appropriate to the user's profile
- Never returns a low-confidence answer in place of a clarification question

**Tools & Data Sources:**

- No direct external data source access
- Operates purely over orchestrator-provided context

---

### Retrieval Agent

**Responsibility:** Shared retrieval capability invoked by other agents. Owns Graph RAG, knowledge graph traversal, entity summary access, and raw source fetching. Abstracts retrieval complexity away from domain agents.

**Behavior:**

- Accepts structured retrieval requests from any agent
- Performs knowledge graph traversal for entity relationship queries
- Executes Graph RAG over the knowledge base
- Fetches raw documents from the data store within retention windows
- Returns structured, source-attributed results

**Tools & Data Sources:**

- Knowledge graph (entity relationships, sector mappings, macro linkages)
- Entity summary store
- Raw document store (news, filings, commentary)
- Vector store for semantic search

---

### Summarisation Agent

**Responsibility:** Maintains structured, up-to-date summaries for all tracked entities and all users. Core system-wide capability consumed by agents and the orchestrator.

**Behavior:**

- Listens for ingestion events and updates relevant entity summary sections
- Folds expiring content into entity summaries before raw content deletion
- Listens for user interaction events and updates user context summaries
- Maintains entity summaries sectioned by: recent news, analyst sentiment, filing highlights, market context
- Maintains user context summaries containing: risk appetite, followed entities, preferences, summarised recent interaction history
- Exposes summaries as queryable artifacts to all agents

**Tools & Data Sources:**

- Ingestion event stream (Kafka)
- User interaction event stream
- Raw document store
- Summary store (MongoDB)

---

## Asset Class Agents

### Stocks Agent

**Responsibility:** US equity analysis. Owns stock-specific data retrieval, price analysis, earnings, and fundamental metrics.

**Data Owned:**

- Daily OHLCV price data for US-listed equities
- Earnings history and upcoming earnings calendar
- Key fundamental metrics (P/E, EPS, market cap, revenue growth)
- SEC filings via EDGAR (10-K, 10-Q, 8-K)
- Dividend history

**Tools & Data Sources:**

- Yahoo Finance / Alpha Vantage / [Polygon.io](http://Polygon.io) (free tier)
- SEC EDGAR API
- Retrieval Agent for knowledge graph and semantic search

---

### Bonds Agent

**Responsibility:** Fixed income analysis. Owns bond-specific data, yield curve analysis, and credit metrics.

**Data Owned:**

- US Treasury yield curve data
- Corporate bond yields and spreads
- Credit ratings
- Duration and maturity profiles
- Fed funds rate and interest rate expectations

**Tools & Data Sources:**

- FRED API (Treasury yields, Fed funds rate)
- Alpha Vantage / relevant free tier fixed income sources
- Retrieval Agent

---

### ETF Agent

**Responsibility:** ETF-specific analysis. Owns ETF structure, composition, and performance metrics. Delegates underlying asset analysis to the relevant asset class agents.

**Data Owned:**

- ETF holdings and composition
- Expense ratios
- Tracking error vs benchmark
- Liquidity and trading volume
- Sector and geographic exposure breakdown

**Tools & Data Sources:**

- Yahoo Finance / ETF-specific free tier sources
- Retrieval Agent
- Delegates to Stocks, Bonds, Commodities agents for underlying asset analysis

---

### Commodities Agent

**Responsibility:** Commodities market analysis. Covers precious metals, energy, and agricultural commodities.

**Data Owned:**

- Spot and futures prices for gold, silver, oil, natural gas, agricultural commodities
- Supply and demand indicators
- Commodity-specific economic drivers (e.g. oil inventory reports, gold as inflation hedge)
- Correlation with macro indicators

**Tools & Data Sources:**

- Alpha Vantage / relevant free tier commodities sources
- FRED API for macro correlations
- Retrieval Agent

---

### Real Estate Agent

**Responsibility:** US real estate market analysis. V1 covers REITs and broad real estate market indicators. Decomposition into commercial and residential sub-agents is a planned V2 enhancement.

**Data Owned:**

- REIT price data and fundamentals (FFO, dividend yield, NAV)
- Broad US real estate market indicators
- Interest rate sensitivity analysis
- Sector exposure (residential, commercial, industrial, retail) at index level

**Tools & Data Sources:**

- Yahoo Finance for REIT data
- FRED API for housing indicators (Case-Shiller, housing starts, mortgage rates)
- Retrieval Agent

> **V2 Enhancement:** Decompose into Commercial Real Estate Agent and Residential Real Estate Agent with dedicated data sources per sub-domain.

---

### Economic Data Agent

**Responsibility:** US macroeconomic data analysis. Owns all economic indicator retrieval, interpretation, and contextualization.

**Data Owned:**

- GDP growth rate
- CPI and PCE inflation measures
- Unemployment rate and non-farm payrolls
- Fed funds rate and FOMC decisions
- Consumer confidence and PMI indices
- Trade balance and current account data
- Release calendar and consensus forecast tracking

**Tools & Data Sources:**

- FRED API (primary source)
- BLS (Bureau of Labor Statistics) public API
- Retrieval Agent

---

### News & Sentiment Agent

**Responsibility:** News aggregation, sentiment analysis, and analyst commentary across all asset classes. Provides cross-cutting signal that other agents and the orchestrator consume.

**Data Owned:**

- News articles from financial sources
- Analyst ratings and price target changes
- Sentiment scores per entity (positive, neutral, negative)
- News mention frequency per entity (input to hotness scoring)
- Significant event detection (product launches, leadership changes, regulatory actions)

**Tools & Data Sources:**

- NewsAPI
- RSS feeds (Reuters, FT public feeds)
- Retrieval Agent for historical news context
- Sentiment scoring via LLM or lightweight model

---

### Trends & Momentum Agent

**Responsibility:** Computes and maintains trend and momentum signals across all tracked entities. Owns the hotness score pipeline.

**Data Owned:**

- Hotness scores (0-100) per entity
- Price momentum signals
- Volume anomaly detection
- News mention frequency trends (from News & Sentiment Agent)
- Cross-entity momentum comparisons

**Behavior:**

- Consumes algorithmic signals as tools and applies agent reasoning over them
- Does not make predictions — surfaces and interprets signals
- Hotness score computation methodology TBD

**Tools & Data Sources:**

- Price and volume data (via Stocks, ETF, Commodities agents or direct)
- News mention frequency (via News & Sentiment Agent)
- FRED data for macro momentum signals
- Retrieval Agent

> **Note:** Specific hotness score algorithms are TBD pending further research. See Section 8 of the Functional Requirements.

---

## Philosophy Agents

Philosophy agents are interpretive agents. They do not fetch data — they apply investment framework lenses over asset class agent outputs. They are activated based on the user's philosophy profile, which is derived from risk appetite and overridable by the user.

### Default Philosophy Mapping


| Risk Appetite | Default Philosophy Pair |
| ------------- | ----------------------- |
| Conservative  | Blue Chip + Value       |
| Moderate      | Value + Growth          |
| Aggressive    | Growth + Macro          |


Users have visibility into their assigned philosophies and can override either or both selections from their profile settings.

---

### Value Investing Agent

**Philosophy:** Seeks undervalued assets trading below intrinsic value with a margin of safety. Focuses on fundamentals, earnings quality, balance sheet strength, and long-term business durability.

**Analytical Focus:**

- P/E, P/B, P/FCF ratios relative to historical and sector averages
- Earnings consistency and quality
- Debt levels and balance sheet health
- Competitive moat assessment
- Discount to intrinsic value estimation

**Tools & Data Sources:**

- No direct external sources
- Operates over Stocks Agent and Economic Data Agent outputs

---

### Growth Investing Agent

**Philosophy:** Seeks companies with above-average growth potential, willing to accept higher valuations in exchange for revenue and earnings growth trajectory.

**Analytical Focus:**

- Revenue and earnings growth rates
- TAM (total addressable market) expansion signals
- R&D investment and product pipeline
- Margin expansion trends
- Relative strength vs sector peers

**Tools & Data Sources:**

- No direct external sources
- Operates over Stocks Agent, ETF Agent, and News & Sentiment Agent outputs

---

### Macro Investing Agent

**Philosophy:** Positions based on macroeconomic trends, monetary policy, geopolitical shifts, and cross-asset relationships. Top-down analytical approach.

**Analytical Focus:**

- Interest rate cycle positioning
- Inflation regime assessment
- Currency and commodity macro drivers
- Sector rotation based on economic cycle phase
- Cross-asset correlation analysis

**Tools & Data Sources:**

- No direct external sources
- Operates over Economic Data Agent, Bonds Agent, Commodities Agent, and Trends & Momentum Agent outputs

---

### Blue Chip Investing Agent

**Philosophy:** Focuses on large, financially stable, market-leading companies with consistent dividend histories and lower volatility profiles.

**Analytical Focus:**

- Dividend yield, payout ratio, and dividend growth history
- Market capitalisation and liquidity
- Revenue stability and recession resilience
- Credit quality and debt serviceability
- Long-term total return vs volatility profile

**Tools & Data Sources:**

- No direct external sources
- Operates over Stocks Agent, Bonds Agent, and Economic Data Agent outputs

---

## Agent Interaction Summary

```
User Query
    │
    ▼
Orchestrator ──── loads ────► User Context Summary
    │
    ├── dispatches concurrently ──► Asset Class Agents (relevant subset)
    │                                   │
    │                                   ├── Stocks Agent
    │                                   ├── Bonds Agent
    │                                   ├── ETF Agent
    │                                   ├── Commodities Agent
    │                                   ├── Real Estate Agent
    │                                   ├── Economic Data Agent
    │                                   ├── News & Sentiment Agent
    │                                   └── Trends & Momentum Agent
    │                                           │
    │                                   all invoke ──► Retrieval Agent
    │
    ├── activates ──► Philosophy Agents (user's two assigned philosophies)
    │                       │
    │                   reason over asset class outputs
    │
    ├── delegates ──► Eval Agent (self-validation loop)
    │                       │
    │               ┌───────┴────────┐
    │           sufficient       insufficient
    │               │                │
    │           assemble         Clarification Agent
    │           response              │
    │               │            formulate question
    │               ▼                ▼
    └──────────► Final Response to User
```

---

## Pending

- Hotness score algorithm definition (Section 8 TBD)
- V2 Real Estate decomposition into Commercial and Residential sub-agents
- Evaluation framework design (component-level and system-level evals)

