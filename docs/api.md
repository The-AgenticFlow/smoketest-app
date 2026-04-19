# SmokeTest API Documentation

> **This document is intentionally incomplete.**
> It serves as a stub for the LORE documentation issue.

## Endpoints

### Health Check

`GET /health`

Returns `{"status": "ok"}`.

### Tasks

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/tasks | List all tasks |
| POST | /api/v1/tasks | Create a task |
| GET | /api/v1/tasks/:id | Get a task |
| PATCH | /api/v1/tasks/:id | Update a task |
| DELETE | /api/v1/tasks/:id | Delete a task |

## Authentication

> **TODO:** Document the auth flow (login, token, admin routes).

## Caching

> **TODO:** Document Redis caching behavior once implemented.

## Rate Limiting

> **TODO:** Document rate limiting headers and 429 responses.
