# Neo4j + Graphiti Schema
## Financial Intelligence Multi-Agent System

**Version:** 0.1.0  
**Status:** Draft  
**Last Updated:** 2026-05-01

---

## Overview

The Neo4j graph database serves two distinct but related purposes in this system:

1. **Entity Knowledge Graph** — manually defined nodes and relationships representing the financial domain: companies, sectors, indices, economic indicators and their relationships
2. **Agent Memory Graph** — managed by Graphiti, representing temporal user context, interaction history, and extracted knowledge from agent interactions

Both graphs share the same Neo4j instance but operate in distinct node label namespaces to avoid collision.

---

## Part 1 — Entity Knowledge Graph

This layer is defined and maintained by the ingestion pipelines and the Summarisation Agent. It represents the financial domain knowledge the agents reason over.

### Node Labels

#### `:Company`
Represents a US-listed company.

```cypher
(:Company {
  entity_id: UUID,           -- FK reference to PostgreSQL Entities table
  name: String,              -- e.g. "Apple Inc."
  ticker: String,            -- e.g. "AAPL"
  exchange: String,          -- e.g. "NASDAQ"
  status: String,            -- active | delisted
  summary: String,           -- latest entity summary from Summarisation Agent
  summary_updated_at: DateTime,
  embedding: List<Float>,    -- vector embedding of name + description + summary
  embedding_model: String,   -- e.g. "text-embedding-3-small"
  embedding_updated_at: DateTime,
  created_at: DateTime
})
```

#### `:Sector`
Represents a US market sector.

```cypher
(:Sector {
  sector_id: UUID,           -- FK reference to PostgreSQL Sectors table
  name: String,              -- e.g. "Technology"
  description: String,
  summary: String,           -- latest sector summary
  summary_updated_at: DateTime,
  embedding: List<Float>,    -- vector embedding of name + description + summary
  embedding_model: String,
  embedding_updated_at: DateTime,
  created_at: DateTime
})
```

#### `:Index`
Represents a US market index.

```cypher
(:Index {
  entity_id: UUID,
  name: String,              -- e.g. "S&P 500"
  ticker: String,            -- e.g. "SPX"
  summary: String,
  summary_updated_at: DateTime,
  embedding: List<Float>,    -- vector embedding of name + description + summary
  embedding_model: String,
  embedding_updated_at: DateTime,
  created_at: DateTime
})
```

#### `:EconomicIndicator`
Represents a US macroeconomic indicator.

```cypher
(:EconomicIndicator {
  entity_id: UUID,
  name: String,              -- e.g. "Consumer Price Index"
  series_id: String,         -- FRED series ID e.g. "CPIAUCSL"
  unit: String,              -- e.g. "percent", "billions of dollars"
  frequency: String,         -- monthly | quarterly | annual
  summary: String,
  summary_updated_at: DateTime,
  embedding: List<Float>,    -- vector embedding of name + description + summary
  embedding_model: String,
  embedding_updated_at: DateTime,
  created_at: DateTime
})
```

#### `:NewsEvent`
Represents a significant news event that affected one or more entities. Not every article — only events the News & Sentiment Agent flags as significant.

```cypher
(:NewsEvent {
  event_id: UUID,
  title: String,
  summary: String,
  sentiment: String,         -- positive | negative | neutral
  sentiment_score: Float,
  published_at: DateTime,
  source: String,
  article_id: UUID,          -- FK reference to PostgreSQL NewsArticles
  embedding: List<Float>,    -- vector embedding of title + summary
  embedding_model: String,
  embedding_updated_at: DateTime
})
```

#### `:MacroEvent`
Represents a significant macroeconomic event such as a Fed rate decision or major indicator release.

```cypher
(:MacroEvent {
  event_id: UUID,
  title: String,
  description: String,
  event_type: String,        -- rate_decision | indicator_release | policy_change
  occurred_at: DateTime,
  impact: String,            -- hawkish | dovish | neutral | positive | negative
  embedding: List<Float>,    -- vector embedding of title + description
  embedding_model: String,
  embedding_updated_at: DateTime
})
```

---

### Relationship Types

#### Company → Sector
```cypher
(:Company)-[:BELONGS_TO]->(:Sector)
```

#### Company → Index
```cypher
(:Company)-[:MEMBER_OF]->(:Index)
```

#### Company → Company
```cypher
(:Company)-[:COMPETES_WITH]->(:Company)
(:Company)-[:SUPPLIER_OF]->(:Company)
(:Company)-[:PARTNER_OF]->(:Company)
```
Properties:
```cypher
{
  relationship_type: String,
  confidence: Float,         -- 0.0 to 1.0, agent-assigned confidence
  established_at: DateTime
}
```

#### Company/Sector/Index → NewsEvent
```cypher
(:Company)-[:AFFECTED_BY {sentiment_score: Float, impact: String}]->(:NewsEvent)
(:Sector)-[:AFFECTED_BY {sentiment_score: Float, impact: String}]->(:NewsEvent)
(:Index)-[:AFFECTED_BY {sentiment_score: Float, impact: String}]->(:NewsEvent)
```

#### EconomicIndicator → MacroEvent
```cypher
(:EconomicIndicator)-[:RELEASED_IN]->(:MacroEvent)
```

#### MacroEvent → Sector/Index
```cypher
(:MacroEvent)-[:IMPACTS]->(:Sector)
(:MacroEvent)-[:IMPACTS]->(:Index)
```
Properties:
```cypher
{
  impact_type: String,       -- positive | negative | neutral
  confidence: Float
}
```

#### Sector → EconomicIndicator
```cypher
(:Sector)-[:CORRELATED_WITH {correlation_strength: Float}]->(:EconomicIndicator)
```

#### Index → Sector
```cypher
(:Index)-[:TRACKS]->(:Sector)
```

---

## Part 2 — Graphiti Agent Memory Graph

Graphiti manages this layer automatically. It maintains a temporal knowledge graph of user interactions, extracted entities, and relationships over time. The following describes what Graphiti creates in Neo4j — you do not define these manually.

### Graphiti-Managed Node Labels

#### `:EpisodicNode`
Represents a discrete interaction or event — a conversation turn, a report generation, a digest delivery. Graphiti creates one per episode you add.

```
Properties managed by Graphiti:
- uuid
- name
- source (message | report | digest | ingestion)
- content (the raw text of the episode)
- created_at
- valid_at (temporal timestamp of when the event occurred)
```

#### `:EntityNode`
Entities Graphiti extracts from episodes — users, companies mentioned, concepts discussed, preferences expressed.

```
Properties managed by Graphiti:
- uuid
- name
- entity_type
- summary (Graphiti maintains a running summary of what is known about this entity)
- created_at
- updated_at
```

#### `:CommunityNode`
Clusters of related entities Graphiti identifies automatically. For example a cluster of technology companies a user frequently asks about.

```
Properties managed by Graphiti:
- uuid
- name
- summary
- created_at
```

### Graphiti-Managed Relationship Types

Graphiti creates typed relationships between EntityNodes extracted from episodes:

```
(:EntityNode)-[:RELATES_TO {
  name: String,              -- relationship label e.g. "interested_in"
  fact: String,              -- the fact this relationship encodes
  created_at: DateTime,
  expired_at: DateTime,      -- Graphiti marks facts as expired when superseded
  valid_at: DateTime,
  invalid_at: DateTime
}]->(:EntityNode)
```

Graphiti also links EntityNodes back to their source episodes:

```
(:EpisodicNode)-[:MENTIONS]->(:EntityNode)
(:EntityNode)-[:MEMBER_OF]->(:CommunityNode)
```

---

## Part 3 — Cross-Graph Relationships

These relationships bridge the Graphiti memory graph and the domain knowledge graph, allowing the Orchestrator to connect user context to entity knowledge.

```cypher
-- A Graphiti EntityNode referencing a domain Company node
(:EntityNode {name: "Apple"})-[:REFERENCES]->(:Company {ticker: "AAPL"})

-- A Graphiti EntityNode referencing a domain Sector node
(:EntityNode {name: "Technology"})-[:REFERENCES]->(:Sector {name: "Technology"})

-- A Graphiti EntityNode referencing an EconomicIndicator
(:EntityNode {name: "CPI"})-[:REFERENCES]->(:EconomicIndicator {series_id: "CPIAUCSL"})
```

These cross-references allow the Orchestrator to ask questions like:
- "What does this user know about Apple?" — traverse from User EntityNode through Graphiti relationships
- "What is the current state of Apple in the knowledge graph?" — traverse to `:Company` node and its relationships

---

## Part 4 — Key Cypher Queries

### Load user context before query (Orchestrator)
```cypher
MATCH (u:EntityNode {name: $username})-[r:RELATES_TO]->(e:EntityNode)
WHERE r.expired_at IS NULL
RETURN u, r, e
ORDER BY r.valid_at DESC
LIMIT 50
```

### Get all entities related to a company
```cypher
MATCH (c:Company {ticker: $ticker})-[r]-(related)
RETURN c, type(r), related
```

### Get recent news events affecting a sector
```cypher
MATCH (s:Sector {name: $sector})-[:AFFECTED_BY]->(n:NewsEvent)
WHERE n.published_at > datetime() - duration({days: 30})
RETURN n
ORDER BY n.published_at DESC
```

### Get macro events impacting a company's sector
```cypher
MATCH (c:Company {ticker: $ticker})-[:BELONGS_TO]->(s:Sector)<-[:IMPACTS]-(m:MacroEvent)
WHERE m.occurred_at > datetime() - duration({days: 90})
RETURN c, s, m
ORDER BY m.occurred_at DESC
```

### Get competing companies in the same sector
```cypher
MATCH (c:Company {ticker: $ticker})-[:BELONGS_TO]->(s:Sector)<-[:BELONGS_TO]-(peer:Company)
WHERE peer.ticker <> $ticker
RETURN peer
```

### Get all entities a user follows (cross-graph)
```cypher
MATCH (u:EntityNode {name: $username})-[:RELATES_TO {name: "follows"}]->(e:EntityNode)-[:REFERENCES]->(domain)
RETURN domain
```

---

## Part 5 — Indexes and Constraints

```cypher
-- Uniqueness constraints
CREATE CONSTRAINT company_ticker IF NOT EXISTS
FOR (c:Company) REQUIRE c.ticker IS UNIQUE;

CREATE CONSTRAINT sector_name IF NOT EXISTS
FOR (s:Sector) REQUIRE s.name IS UNIQUE;

CREATE CONSTRAINT index_ticker IF NOT EXISTS
FOR (i:Index) REQUIRE i.ticker IS UNIQUE;

CREATE CONSTRAINT indicator_series IF NOT EXISTS
FOR (e:EconomicIndicator) REQUIRE e.series_id IS UNIQUE;

-- Performance indexes
CREATE INDEX company_name IF NOT EXISTS FOR (c:Company) ON (c.name);
CREATE INDEX news_event_published IF NOT EXISTS FOR (n:NewsEvent) ON (n.published_at);
CREATE INDEX macro_event_occurred IF NOT EXISTS FOR (m:MacroEvent) ON (m.occurred_at);
CREATE INDEX entity_node_name IF NOT EXISTS FOR (e:EntityNode) ON (e.name);

-- Vector indexes for semantic search
-- Dimension 1536 matches text-embedding-3-small; adjust if using a different model
CREATE VECTOR INDEX company_embedding IF NOT EXISTS
FOR (c:Company) ON (c.embedding)
OPTIONS {indexConfig: {
  `vector.dimensions`: 1536,
  `vector.similarity_function`: 'cosine'
}};

CREATE VECTOR INDEX sector_embedding IF NOT EXISTS
FOR (s:Sector) ON (s.embedding)
OPTIONS {indexConfig: {
  `vector.dimensions`: 1536,
  `vector.similarity_function`: 'cosine'
}};

CREATE VECTOR INDEX index_embedding IF NOT EXISTS
FOR (i:Index) ON (i.embedding)
OPTIONS {indexConfig: {
  `vector.dimensions`: 1536,
  `vector.similarity_function`: 'cosine'
}};

CREATE VECTOR INDEX indicator_embedding IF NOT EXISTS
FOR (e:EconomicIndicator) ON (e.embedding)
OPTIONS {indexConfig: {
  `vector.dimensions`: 1536,
  `vector.similarity_function`: 'cosine'
}};

CREATE VECTOR INDEX news_event_embedding IF NOT EXISTS
FOR (n:NewsEvent) ON (n.embedding)
OPTIONS {indexConfig: {
  `vector.dimensions`: 1536,
  `vector.similarity_function`: 'cosine'
}};

CREATE VECTOR INDEX macro_event_embedding IF NOT EXISTS
FOR (m:MacroEvent) ON (m.embedding)
OPTIONS {indexConfig: {
  `vector.dimensions`: 1536,
  `vector.similarity_function`: 'cosine'
}};
```

---

## Summary

| Layer | Managed By | Purpose |
|---|---|---|
| Entity Knowledge Graph | Ingestion pipelines + Summarisation Agent | Financial domain knowledge — companies, sectors, events, relationships |
| Agent Memory Graph | Graphiti | Temporal user context, interaction history, extracted knowledge |
| Cross-Graph References | Orchestrator + Summarisation Agent | Bridge between user memory and domain knowledge |
