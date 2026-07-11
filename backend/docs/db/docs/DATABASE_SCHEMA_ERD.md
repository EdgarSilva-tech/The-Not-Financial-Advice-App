# PostgreSQL Database Schema — ERD
## Financial Intelligence Multi-Agent System

**Version:** 0.2.0  
**Status:** Draft  
**Last Updated:** 2026-05-01

---

```mermaid
erDiagram
  Users {
    uuid user_id PK
    string username
    string email
    boolean email_confirmed
    timestamp confirmed_at
    timestamp created_at
    timestamp updated_at
    string risk_tolerance
    string investment_philosophy_1
    string investment_philosophy_2
    string digest_delivery_day
    string password_hash
  }
  Sectors {
    uuid sector_id PK
    string sector_name
    string sector_description
    uuid pipeline_def_id FK
  }
  Entities {
    uuid entity_id PK
    string entity_name
    string ticker_symbol
    string exchange
    uuid entity_sector FK
    string entity_description
    string entity_type
    string entity_status
  }
  UserFollowedEntities {
    uuid id PK
    uuid user_id FK
    uuid entity_id FK
    timestamp followed_at
  }
  UserPreferredSectors {
    uuid id PK
    uuid user_id FK
    uuid sector_id FK
    timestamp created_at
  }
  Documents {
    uuid document_id PK
    string title
    string document_type
    timestamp date_sent
    string object_storage_key
    uuid request_user FK
    string delivery_status
    string error_log
    timestamp created_at
  }
  DocumentTags {
    uuid id PK
    uuid document_id FK
    string tag
  }
  Notifications {
    uuid notification_id PK
    uuid user_id FK
    string notification_text
    string notification_type
    string notification_status
    timestamp created_at
    timestamp read_at
    string error_log
  }
  ChatSessions {
    uuid session_id PK
    uuid user_id FK
    timestamp created_at
    timestamp last_active_at
    string session_status
    int message_count
  }
  ChatMessages {
    uuid message_id PK
    uuid session_id FK
    uuid user_id FK
    string role
    string content
    timestamp created_at
    int tokens_used
  }
  DataSources {
    uuid datasource_id PK
    string datasource_name
    uuid sector_id FK
    string output_type
    timestamp created_at
  }
  DataSourceLinks {
    uuid link_id PK
    uuid datasource_id FK
    string url
    string link_type
    timestamp created_at
  }
  DataSourceOutputs {
    uuid output_id PK
    uuid datasource_id FK
    string pipeline_run_id FK
    string output_key
    string output_type
    timestamp fetched_at
    timestamp expires_at
    string status
  }
  PipelineDefinitions {
    uuid pipeline_def_id PK
    string pipeline_name
    string pipeline_type
    uuid sector_id FK
    string cadence
    timestamp created_at
  }
  Pipelines {
    string pipeline_id PK
    uuid pipeline_def_id FK
    string run_status
    string run_error_log
    uuid data_source_id FK
    timestamp start_time
    timestamp end_time
  }
  PipelineCheckpoints {
    uuid checkpoint_id PK
    string pipeline_id FK
    int batch_sequence
    string checkpoint_status
    timestamp created_at
    string batch_error_log
  }
  AgentAuditTrail {
    uuid audit_id PK
    uuid user_id FK
    uuid session_id FK
    string query_text
    jsonb messages_traces
    jsonb tool_calls
    jsonb evaluation_content
    int total_tokens_used
    int total_latency_ms
    timestamp created_at
  }
  NewsArticles {
    uuid article_id PK
    uuid datasource_id FK
    uuid entity_id FK
    string url_hash
    string title
    string content
    string author
    timestamp published_at
    timestamp fetched_at
    timestamp expires_at
    float sentiment_score
    string status
  }
  SECFilings {
    uuid filing_id PK
    uuid entity_id FK
    string accession_number
    string filing_type
    timestamp filed_at
    timestamp fetched_at
    string content
    string filing_url
    string status
  }
  OHLCVPrices {
    uuid price_id PK
    uuid entity_id FK
    date trading_date
    numeric open
    numeric high
    numeric low
    numeric close
    bigint volume
    timestamp fetched_at
  }
  EconomicIndicatorReleases {
    uuid release_id PK
    uuid datasource_id FK
    string series_id
    string indicator_name
    date release_date
    numeric value
    string unit
    timestamp fetched_at
  }
  AnalystCommentary {
    uuid commentary_id PK
    uuid entity_id FK
    uuid datasource_id FK
    string content
    string analyst_name
    string rating
    numeric price_target
    timestamp published_at
    timestamp fetched_at
    timestamp expires_at
    string status
  }
  Users ||--o{ UserFollowedEntities : follows
  Users ||--o{ UserPreferredSectors : prefers
  Users ||--o{ Documents : requests
  Users ||--o{ Notifications : receives
  Users ||--o{ ChatSessions : has
  Users ||--o{ AgentAuditTrail : generates
  Entities ||--o{ UserFollowedEntities : followed_by
  Entities }o--|| Sectors : belongs_to
  Entities ||--o{ NewsArticles : covered_by
  Entities ||--o{ SECFilings : files
  Entities ||--o{ OHLCVPrices : has_prices
  Entities ||--o{ AnalystCommentary : analysed_by
  Sectors ||--o{ UserPreferredSectors : preferred_by
  Sectors ||--o{ DataSources : sourced_by
  Sectors }o--|| PipelineDefinitions : processed_by
  Documents ||--o{ DocumentTags : tagged_with
  ChatSessions ||--o{ ChatMessages : contains
  Users ||--o{ ChatMessages : sends
  ChatSessions ||--o{ AgentAuditTrail : traced_by
  DataSources ||--o{ DataSourceLinks : has_links
  DataSources ||--o{ DataSourceOutputs : produces
  DataSources ||--o{ NewsArticles : provides
  DataSources ||--o{ EconomicIndicatorReleases : provides
  DataSources ||--o{ AnalystCommentary : provides
  PipelineDefinitions ||--o{ Pipelines : runs
  Pipelines ||--o{ PipelineCheckpoints : checkpoints
  Pipelines ||--o{ DataSourceOutputs : produces_outputs
  Pipelines }o--|| DataSources : ingests
```

---

## Table Descriptions

| Table | Purpose |
|---|---|
| Users | User accounts, authentication, preferences, risk appetite, philosophy profile |
| Sectors | US market sectors — technology, energy, healthcare etc. |
| Entities | US-listed companies, indices, economic indicators |
| UserFollowedEntities | Junction table — which users follow which entities |
| UserPreferredSectors | Junction table — which users prefer which sectors |
| Documents | Unified table for reports and digests, discriminated by document_type |
| DocumentTags | Tags associated with documents |
| Notifications | In-app notification history per user |
| ChatSessions | Stateful chat session containers per user |
| ChatMessages | Individual messages within a chat session |
| DataSources | External data providers (NewsAPI, FRED, EDGAR etc.) |
| DataSourceLinks | API endpoints and documentation URLs per data source |
| DataSourceOutputs | Individual output files produced per pipeline run per data source |
| PipelineDefinitions | Pipeline definitions — what a pipeline is and its cadence |
| Pipelines | Individual pipeline run records with Snowflake IDs |
| PipelineCheckpoints | Micro-batch checkpoints for crash recovery |
| AgentAuditTrail | Full reasoning traces per agent interaction |
| NewsArticles | Ingested news articles within 90-day retention window |
| SECFilings | SEC filings via EDGAR — permanent retention |
| OHLCVPrices | Daily market prices — permanent retention |
| EconomicIndicatorReleases | FRED economic indicator releases — permanent retention |
| AnalystCommentary | Analyst commentary within 90-day retention window |

---

## Key Constraints

| Table | Unique Constraint | Purpose |
|---|---|---|
| NewsArticles | url_hash | Idempotent ingestion deduplication |
| SECFilings | accession_number | EDGAR natural deduplication key |
| OHLCVPrices | entity_id + trading_date | One price record per entity per day |
| EconomicIndicatorReleases | series_id + release_date | One release per indicator per date |
| UserFollowedEntities | user_id + entity_id | Prevent duplicate follows |
| UserPreferredSectors | user_id + sector_id | Prevent duplicate sector preferences |

---

## Pipeline Design Note

`PipelineDefinitions` separates **what a pipeline is** from **a specific execution of it**:

- `PipelineDefinitions` — defines the pipeline: its name, type, cadence, and which sector it serves. One record per pipeline type per sector. Static, rarely changes.
- `Pipelines` — records each individual run of a pipeline definition. One record per execution with its own Snowflake ID, status, start/end times, and error log.

This means a sector has a FK to `PipelineDefinitions` (its dedicated pipeline) while `Pipelines` accumulates run history over time without polluting the sector record.
