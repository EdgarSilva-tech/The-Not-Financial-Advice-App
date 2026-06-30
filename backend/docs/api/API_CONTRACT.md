# API Contract
## Financial Intelligence Multi-Agent System

**Version:** 0.1.0  
**Status:** Draft  
**Last Updated:** 2026-05-01  
**Base URL:** `/api/v1`  
**Authentication:** JWT via HttpOnly cookie  
**Content-Type:** `application/json`

---

## Table of Contents

1. [Conventions](#1-conventions)
2. [Authentication](#2-authentication)
3. [Users](#3-users)
4. [Entities](#4-entities)
5. [Sectors](#5-sectors)
6. [Chat](#6-chat)
7. [Reports](#7-reports)
8. [Digests](#8-digests)
9. [Notifications](#9-notifications)
10. [Dashboard](#10-dashboard)
11. [Data Refresh](#11-data-refresh)
12. [Error Responses](#12-error-responses)

---

## 1. Conventions

### HTTP Methods
| Method | Usage |
|---|---|
| GET | Retrieve resources |
| POST | Create resources or trigger actions |
| PATCH | Partial update of a resource |
| DELETE | Remove a resource |

### Response Envelope
All responses follow a consistent envelope:

**Success:**
```json
{
  "status": "success",
  "data": { },
  "meta": { }
}
```

**Error:**
```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message"
  }
}
```

### Pagination
List endpoints support cursor-based pagination:
```json
{
  "status": "success",
  "data": [ ],
  "meta": {
    "cursor": "next_cursor_token",
    "has_more": true,
    "total": 100
  }
}
```

Query parameters: `?cursor=<token>&limit=<int>`

### Data Freshness
All responses that include external financial data include a `data_freshness` object:
```json
{
  "data_freshness": {
    "fetched_at": "2026-05-01T13:00:00Z",
    "is_stale": false,
    "source": "Yahoo Finance"
  }
}
```

---

## 2. Authentication

### POST `/auth/register`
Register a new user.

**Request:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "phone_number": "string"
}
```

**Response `201`:**
```json
{
  "status": "success",
  "data": {
    "user_id": "uuid",
    "username": "string",
    "email": "string",
    "email_confirmed": false
  }
}
```

---

### POST `/auth/login`
Authenticate a user. Sets HttpOnly JWT cookie on success.

**Request:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Response `200`:**
```json
{
  "status": "success",
  "data": {
    "user_id": "uuid",
    "username": "string"
  }
}
```
> JWT and refresh token set as HttpOnly cookies. No tokens in response body.

---

### POST `/auth/logout`
Invalidate the current session. Clears HttpOnly cookies.

**Request:** None

**Response `200`:**
```json
{
  "status": "success",
  "data": {
    "message": "Logged out successfully"
  }
}
```

---

### POST `/auth/refresh`
Refresh the JWT token using the refresh token cookie.

**Request:** None

**Response `200`:**
```json
{
  "status": "success",
  "data": {
    "message": "Token refreshed"
  }
}
```
> New JWT set as HttpOnly cookie.

---

### POST `/auth/confirm-email`
Confirm user email address.

**Request:**
```json
{
  "token": "string"
}
```

**Response `200`:**
```json
{
  "status": "success",
  "data": {
    "email_confirmed": true,
    "confirmed_at": "datetime"
  }
}
```

---

## 3. Users

> All endpoints require authentication.

### GET `/users/me`
Get the current user's profile.

**Response `200`:**
```json
{
  "status": "success",
  "data": {
    "user_id": "uuid",
    "username": "string",
    "email": "string",
    "phone_number": "string",
    "risk_tolerance": "conservative | moderate | aggressive",
    "investment_philosophy_1": "value | growth | macro | blue_chip",
    "investment_philosophy_2": "value | growth | macro | blue_chip",
    "digest_delivery_day": "monday | tuesday | wednesday | thursday | friday | saturday | sunday",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
}
```

---

### PATCH `/users/me`
Update the current user's profile.

**Request:**
```json
{
  "username": "string",
  "phone_number": "string",
  "risk_tolerance": "conservative | moderate | aggressive",
  "investment_philosophy_1": "value | growth | macro | blue_chip",
  "investment_philosophy_2": "value | growth | macro | blue_chip",
  "digest_delivery_day": "monday"
}
```
> All fields optional. Only provided fields are updated.

**Response `200`:**
```json
{
  "status": "success",
  "data": {
    "user_id": "uuid",
    "updated_at": "datetime"
  }
}
```

---

### PATCH `/users/me/password`
Update the current user's password.

**Request:**
```json
{
  "current_password": "string",
  "new_password": "string"
}
```

**Response `200`:**
```json
{
  "status": "success",
  "data": {
    "message": "Password updated successfully"
  }
}
```

---

## 4. Entities

### GET `/entities/search`
Search for entities to follow.

**Query Parameters:**
- `q` (string) — search term
- `type` (string) — `company | index | economic_indicator`
- `limit` (int) — default 20

**Response `200`:**
```json
{
  "status": "success",
  "data": [
    {
      "entity_id": "uuid",
      "entity_name": "Apple Inc.",
      "ticker": "AAPL",
      "exchange": "NASDAQ",
      "entity_type": "company",
      "entity_sector": "Technology",
      "entity_status": "active"
    }
  ],
  "meta": {
    "total": 5
  }
}
```

---

### GET `/entities/followed`
Get all entities the current user follows.

**Response `200`:**
```json
{
  "status": "success",
  "data": [
    {
      "entity_id": "uuid",
      "entity_name": "string",
      "ticker": "string",
      "entity_type": "string",
      "entity_sector": "string",
      "followed_at": "datetime"
    }
  ],
  "meta": {
    "total": 10
  }
}
```

---

### POST `/entities/{entity_id}/follow`
Follow an entity.

**Response `201`:**
```json
{
  "status": "success",
  "data": {
    "entity_id": "uuid",
    "followed_at": "datetime"
  }
}
```

---

### DELETE `/entities/{entity_id}/follow`
Unfollow an entity.

**Response `200`:**
```json
{
  "status": "success",
  "data": {
    "entity_id": "uuid",
    "message": "Entity unfollowed"
  }
}
```

---

### GET `/entities/{entity_id}`
Get details and latest summary for a specific entity.

**Response `200`:**
```json
{
  "status": "success",
  "data": {
    "entity_id": "uuid",
    "entity_name": "string",
    "ticker": "string",
    "exchange": "string",
    "entity_type": "string",
    "entity_sector": "string",
    "entity_description": "string",
    "summary": {
      "recent_news": "string",
      "analyst_sentiment": "string",
      "filing_highlights": "string",
      "market_context": "string"
    },
    "data_freshness": { }
  }
}
```

---

### POST `/entities/{entity_id}/refresh`
Trigger a manual data refresh for an entity.

**Response `202`:**
```json
{
  "status": "success",
  "data": {
    "entity_id": "uuid",
    "refresh_queued_at": "datetime",
    "message": "Refresh queued. You will be notified when complete."
  }
}
```

---

## 5. Sectors

### GET `/sectors`
List all available sectors.

**Response `200`:**
```json
{
  "status": "success",
  "data": [
    {
      "sector_id": "uuid",
      "sector_name": "string",
      "sector_description": "string"
    }
  ]
}
```

---

### GET `/sectors/preferred`
Get all sectors the current user prefers.

**Response `200`:**
```json
{
  "status": "success",
  "data": [
    {
      "sector_id": "uuid",
      "sector_name": "string",
      "created_at": "datetime"
    }
  ]
}
```

---

### POST `/sectors/{sector_id}/prefer`
Add a sector to user preferences.

**Response `201`:**
```json
{
  "status": "success",
  "data": {
    "sector_id": "uuid",
    "created_at": "datetime"
  }
}
```

---

### DELETE `/sectors/{sector_id}/prefer`
Remove a sector from user preferences.

**Response `200`:**
```json
{
  "status": "success",
  "data": {
    "sector_id": "uuid",
    "message": "Sector preference removed"
  }
}
```

---

## 6. Chat

> Chat uses WebSocket at `ws://base_url/chat/ws/{session_id}` for streaming.  
> The REST endpoints below manage session lifecycle.

### POST `/chat/sessions`
Create a new chat session.

**Response `201`:**
```json
{
  "status": "success",
  "data": {
    "session_id": "uuid",
    "created_at": "datetime"
  }
}
```

---

### GET `/chat/sessions`
List all chat sessions for the current user.

**Query Parameters:**
- `cursor` (string)
- `limit` (int) — default 20

**Response `200`:**
```json
{
  "status": "success",
  "data": [
    {
      "session_id": "uuid",
      "created_at": "datetime",
      "last_active_at": "datetime",
      "session_status": "active | inactive | expired",
      "message_count": 12
    }
  ],
  "meta": { }
}
```

---

### GET `/chat/sessions/{session_id}/messages`
Get message history for a session.

**Query Parameters:**
- `cursor` (string)
- `limit` (int) — default 50

**Response `200`:**
```json
{
  "status": "success",
  "data": [
    {
      "message_id": "uuid",
      "role": "user | assistant",
      "content": "string",
      "created_at": "datetime",
      "tokens_used": 120
    }
  ],
  "meta": { }
}
```

---

### DELETE `/chat/sessions/{session_id}`
Delete a chat session and its messages.

**Response `200`:**
```json
{
  "status": "success",
  "data": {
    "session_id": "uuid",
    "message": "Session deleted"
  }
}
```

---

### WebSocket `/chat/ws/{session_id}`
Stream chat messages. Established after creating a session via REST.

**Client sends:**
```json
{
  "type": "message",
  "content": "How is the energy sector looking given current Fed policy?"
}
```

**Server streams:**
```json
{ "type": "token", "content": "Based" }
{ "type": "token", "content": " on" }
{ "type": "token", "content": " current" }
```

**Server sends on completion:**
```json
{
  "type": "done",
  "message_id": "uuid",
  "tokens_used": 342,
  "data_freshness": { }
}
```

**Server sends on delay:**
```json
{
  "type": "status",
  "content": "This is taking longer than usual, still working on it..."
}
```

**Server sends on error:**
```json
{
  "type": "error",
  "code": "AGENT_ERROR",
  "message": "We are experiencing difficulties. Please try again."
}
```

---

## 7. Reports

### POST `/reports`
Request a new research report via the REST API.  
> Reports can also be requested via chat. This endpoint supports direct programmatic requests.

**Request:**
```json
{
  "topic": "string",
  "scope": "string"
}
```

**Response `202`:**
```json
{
  "status": "success",
  "data": {
    "document_id": "uuid",
    "title": "string",
    "delivery_status": "generating",
    "created_at": "datetime"
  }
}
```

---

### GET `/reports`
List all reports for the current user.

**Query Parameters:**
- `cursor` (string)
- `limit` (int) — default 20
- `status` (string) — `generating | delivered | failed`

**Response `200`:**
```json
{
  "status": "success",
  "data": [
    {
      "document_id": "uuid",
      "title": "string",
      "document_type": "report",
      "delivery_status": "string",
      "date_sent": "datetime",
      "created_at": "datetime"
    }
  ],
  "meta": { }
}
```

---

### GET `/reports/{document_id}/download`
Get a presigned URL to download a report.

**Response `200`:**
```json
{
  "status": "success",
  "data": {
    "document_id": "uuid",
    "download_url": "string",
    "expires_at": "datetime"
  }
}
```

---

## 8. Digests

### GET `/digests`
List all digests for the current user.

**Query Parameters:**
- `cursor` (string)
- `limit` (int) — default 20

**Response `200`:**
```json
{
  "status": "success",
  "data": [
    {
      "document_id": "uuid",
      "title": "string",
      "document_type": "digest",
      "delivery_status": "string",
      "date_sent": "datetime",
      "created_at": "datetime"
    }
  ],
  "meta": { }
}
```

---

### GET `/digests/{document_id}/download`
Get a presigned URL to download a digest.

**Response `200`:**
```json
{
  "status": "success",
  "data": {
    "document_id": "uuid",
    "download_url": "string",
    "expires_at": "datetime"
  }
}
```

---

### PATCH `/digests/preferences`
Update digest delivery preferences.

**Request:**
```json
{
  "delivery_day": "monday | tuesday | wednesday | thursday | friday | saturday | sunday"
}
```

**Response `200`:**
```json
{
  "status": "success",
  "data": {
    "delivery_day": "string",
    "updated_at": "datetime"
  }
}
```

---

## 9. Notifications

### GET `/notifications`
List notifications for the current user.

**Query Parameters:**
- `cursor` (string)
- `limit` (int) — default 20
- `status` (string) — `read | unread`

**Response `200`:**
```json
{
  "status": "success",
  "data": [
    {
      "notification_id": "uuid",
      "notification_text": "string",
      "notification_type": "digest_ready | report_ready | trend_alert | refresh_complete | system_alert",
      "notification_status": "read | unread",
      "created_at": "datetime",
      "read_at": "datetime"
    }
  ],
  "meta": { }
}
```

---

### PATCH `/notifications/{notification_id}/read`
Mark a notification as read.

**Response `200`:**
```json
{
  "status": "success",
  "data": {
    "notification_id": "uuid",
    "read_at": "datetime"
  }
}
```

---

### PATCH `/notifications/read-all`
Mark all notifications as read.

**Response `200`:**
```json
{
  "status": "success",
  "data": {
    "updated_count": 12
  }
}
```

---

### PATCH `/notifications/preferences`
Update notification preferences.

**Request:**
```json
{
  "digest_ready": true,
  "report_ready": true,
  "trend_alert": true,
  "refresh_complete": true,
  "system_alert": true
}
```

**Response `200`:**
```json
{
  "status": "success",
  "data": {
    "updated_at": "datetime"
  }
}
```

---

## 10. Dashboard

### GET `/dashboard/hotness`
Get hotness scores for all entities the user follows.

**Response `200`:**
```json
{
  "status": "success",
  "data": [
    {
      "entity_id": "uuid",
      "entity_name": "string",
      "ticker": "string",
      "entity_type": "string",
      "hotness_score": 78,
      "score_direction": "up | down | stable",
      "last_updated": "datetime",
      "signals": {
        "price_momentum": 0.8,
        "volume_anomaly": 0.6,
        "news_mention_frequency": 0.7
      }
    }
  ],
  "data_freshness": { }
}
```

---

### GET `/dashboard/trends`
Get top trending entities across all US markets regardless of what the user follows.

**Query Parameters:**
- `limit` (int) — default 10
- `entity_type` (string) — `company | sector | index | economic_indicator`

**Response `200`:**
```json
{
  "status": "success",
  "data": [
    {
      "entity_id": "uuid",
      "entity_name": "string",
      "ticker": "string",
      "entity_type": "string",
      "hotness_score": 92,
      "score_direction": "up | down | stable",
      "trend_summary": "string",
      "last_updated": "datetime"
    }
  ],
  "data_freshness": { }
}
```

---

### GET `/dashboard/macro`
Get current US macroeconomic overview.

**Response `200`:**
```json
{
  "status": "success",
  "data": {
    "summary": "string",
    "indicators": [
      {
        "series_id": "string",
        "indicator_name": "string",
        "latest_value": 3.2,
        "unit": "string",
        "release_date": "date",
        "trend": "up | down | stable"
      }
    ],
    "data_freshness": { }
  }
}
```

---

## 11. Data Refresh

### POST `/refresh/{entity_id}`
Queue a manual data refresh for a specific entity. Returns immediately with a queued status — the user is notified via in-app notification and email when complete.

**Response `202`:**
```json
{
  "status": "success",
  "data": {
    "entity_id": "uuid",
    "refresh_queued_at": "datetime",
    "message": "Refresh queued. You will be notified when complete."
  }
}
```

---

## 12. Error Responses

### Standard Error Codes

| HTTP Status | Error Code | Description |
|---|---|---|
| 400 | VALIDATION_ERROR | Request payload failed schema validation |
| 401 | UNAUTHORIZED | Missing or invalid authentication |
| 403 | FORBIDDEN | Authenticated but insufficient permissions |
| 404 | NOT_FOUND | Resource does not exist |
| 409 | CONFLICT | Resource already exists (e.g. duplicate follow) |
| 422 | UNPROCESSABLE | Request valid but cannot be processed (e.g. report scope too broad) |
| 429 | RATE_LIMITED | Too many requests |
| 503 | SERVICE_UNAVAILABLE | Upstream data source unavailable, serving cached data |
| 500 | INTERNAL_ERROR | Unexpected server error |

### Error Response Shape
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "email must be a valid email address",
    "field": "email"
  }
}
```

### Stale Data Warning
When data is served from cache due to a source being unavailable, a `503` is not returned — the response is `200` with a stale data flag:
```json
{
  "status": "success",
  "data": { },
  "data_freshness": {
    "fetched_at": "2026-05-01T08:00:00Z",
    "is_stale": true,
    "source": "Yahoo Finance",
    "reason": "Source temporarily unavailable. Serving cached data."
  }
}
```
