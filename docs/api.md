# SmokeTest API Documentation

## Overview

The SmokeTest App API provides a simple REST interface for managing tasks with JWT authentication support.

**Base URL:** `http://localhost:8000`

**API Version:** `v1`

---

## Endpoints

### Health Check

#### `GET /health`

Returns the current status of the API. This endpoint is exempt from rate limiting.

**Response:**

- **Status:** 200 OK
- **Content-Type:** application/json
- **Body:**
  ```json
  {
    "status": "ok"
  }
  ```

**Example Request:**

```bash
curl -X GET http://localhost:8000/health
```

**Example Response:**

```json
{
  "status": "ok"
}
```

---

### Tasks

#### `GET /api/v1/tasks`

List all tasks with optional filtering and pagination.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `completed` | boolean | No | - | Filter by completion status (true/false) |
| `priority` | string | No | - | Filter by priority level (low, medium, high) |
| `limit` | integer | No | 50 | Number of results to return (min: 1, max: 100) |
| `offset` | integer | No | 0 | Number of results to skip for pagination (min: 0) |

**Response:**

- **Status:** 200 OK
- **Content-Type:** application/json
- **Body:** PaginatedTaskResponse object
  - `items` (array): Array of TaskResponse objects
  - `total` (integer): Total number of tasks matching the filter
  - `limit` (integer): Limit applied to this query
  - `offset` (integer): Offset applied to this query

**Example Request - Basic:**

```bash
curl -X GET http://localhost:8000/api/v1/tasks
```

**Example Response - Basic:**

```json
{
  "items": [
    {
      "id": 1,
      "title": "Complete documentation",
      "description": "Write API documentation for the SmokeTest App",
      "completed": false,
      "priority": "high"
    },
    {
      "id": 2,
      "title": "Review code",
      "description": null,
      "completed": true,
      "priority": "medium"
    }
  ],
  "total": 2,
  "limit": 50,
  "offset": 0
}
```

**Example Request - Filter by Priority:**

```bash
curl -X GET "http://localhost:8000/api/v1/tasks?priority=high"
```

**Example Request - Filter by Completed Status:**

```bash
curl -X GET "http://localhost:8000/api/v1/tasks?completed=false"
```

**Example Request - Pagination:**

```bash
# Get first page with 10 items per page
curl -X GET "http://localhost:8000/api/v1/tasks?limit=10&offset=0"

# Get second page
curl -X GET "http://localhost:8000/api/v1/tasks?limit=10&offset=10"
```

**Example Request - Combined Filters:**

```bash
# Get only incomplete high-priority tasks, first 5 results
curl -X GET "http://localhost:8000/api/v1/tasks?completed=false&priority=high&limit=5"
```

---

#### `POST /api/v1/tasks`

Create a new task.

**Request:**

- **Content-Type:** application/json
- **Body:** TaskCreate object
  - `title` (string, required): Task title (max 255 characters, HTML stripped)
  - `description` (string, optional): Task description (HTML stripped)
  - `priority` (string, optional): Task priority level (default: "medium")
  - `completed` (boolean, optional): Initial completion status (default: false)

**Response:**

- **Status:** 201 Created
- **Content-Type:** application/json
- **Body:** TaskResponse object
  - `id` (integer): Task ID
  - `title` (string): Task title (sanitized)
  - `description` (string | null): Task description (sanitized)
  - `completed` (boolean): Task completion status
  - `priority` (string): Task priority level

**Validation Rules:**

- `title` is required and cannot be empty
- `title` is limited to 255 characters (after HTML stripping)
- `title` and `description` have HTML tags stripped automatically
- `priority` accepts any string value (no enum validation)

**Example Request:**

```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Write documentation",
    "description": "Complete API docs for the SmokeTest App",
    "priority": "high"
  }'
```

**Example Response:**

```json
{
  "id": 1,
  "title": "Write documentation",
  "description": "Complete API docs for the SmokeTest App",
  "completed": false,
  "priority": "high"
}
```

**Error Responses:**

- **Status:** 422 Unprocessable Entity
- **Body:**
  ```json
  {
    "detail": [
      {
        "type": "value_error",
        "loc": ["body", "title"],
        "msg": "Value error, title cannot be empty",
        "input": ""
      }
    ]
  }
  ```

---

#### `GET /api/v1/tasks/{task_id}`

Get a single task by ID.

**Parameters:**

- `task_id` (path, integer, required): The ID of the task to retrieve

**Response:**

- **Status:** 200 OK
- **Content-Type:** application/json
- **Body:** TaskResponse object

**Example Request:**

```bash
curl -X GET http://localhost:8000/api/v1/tasks/1
```

**Example Response:**

```json
{
  "id": 1,
  "title": "Write documentation",
  "description": "Complete API docs for the SmokeTest App",
  "completed": false,
  "priority": "high"
}
```

**Error Response:**

- **Status:** 404 Not Found
- **Body:**
  ```json
  {
    "detail": "Task not found"
  }
  ```

---

#### `PATCH /api/v1/tasks/{task_id}`

Update a task (partial update supported). Only fields provided in the request body will be updated.

**Parameters:**

- `task_id` (path, integer, required): The ID of the task to update

**Request:**

- **Content-Type:** application/json
- **Body:** TaskUpdate object (all fields optional)
  - `title` (string, optional): New task title (max 255 characters, HTML stripped)
  - `description` (string, optional): New task description (HTML stripped)
  - `completed` (boolean, optional): New completion status
  - `priority` (string, optional): New priority level

**Response:**

- **Status:** 200 OK
- **Content-Type:** application/json
- **Body:** TaskResponse object

**Validation Rules:**

- `title` cannot be empty if provided
- `title` is limited to 255 characters (after HTML stripping)
- `title` and `description` have HTML tags stripped automatically
- Fields not included in the request are not modified

**Example Request - Partial Update:**

```bash
curl -X PATCH http://localhost:8000/api/v1/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{
    "completed": true
  }'
```

**Example Response:**

```json
{
  "id": 1,
  "title": "Write documentation",
  "description": "Complete API docs for the SmokeTest App",
  "completed": true,
  "priority": "high"
}
```

**Example Request - Update Title:**

```bash
curl -X PATCH http://localhost:8000/api/v1/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated title"
  }'
```

**Error Response - Task Not Found:**

- **Status:** 404 Not Found
- **Body:**
  ```json
  {
    "detail": "Task not found"
  }
  ```

**Error Response - Validation Error:**

- **Status:** 422 Unprocessable Entity
- **Body:**
  ```json
  {
    "detail": [
      {
        "type": "value_error",
        "loc": ["body", "title"],
        "msg": "Value error, title cannot exceed 255 characters",
        "input": "a very long title..."
      }
    ]
  }
  ```

---

#### `DELETE /api/v1/tasks/{task_id}`

Delete a task.

**Parameters:**

- `task_id` (path, integer, required): The ID of the task to delete

**Response:**

- **Status:** 204 No Content
- **Body:** (empty)

**Example Request:**

```bash
curl -X DELETE http://localhost:8000/api/v1/tasks/1
```

**Error Response:**

- **Status:** 404 Not Found
- **Body:**
  ```json
  {
    "detail": "Task not found"
  }
  ```

---

## Schemas

### TaskCreate

Request schema for creating a new task.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `title` | string | Yes | - | Task title (max 255 characters, HTML stripped) |
| `description` | string | No | null | Optional task description (HTML stripped) |
| `priority` | string | No | "medium" | Task priority level |
| `completed` | boolean | No | false | Initial completion status |

```json
{
  "title": "New task",
  "description": "Task description",
  "priority": "medium",
  "completed": false
}
```

### TaskUpdate

Request schema for updating an existing task. All fields are optional; only provided fields will be updated.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | No | New task title (HTML stripped, max 255 chars) |
| `description` | string | No | New task description (HTML stripped) |
| `completed` | boolean | No | New completion status |
| `priority` | string | No | New priority level |

```json
{
  "completed": true
}
```

### TaskResponse

Response schema for task operations. This is the format returned by all task endpoints.

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Task ID (auto-generated) |
| `title` | string | Task title (sanitized) |
| `description` | string \| null | Task description (sanitized, null if not set) |
| `completed` | boolean | Task completion status |
| `priority` | string | Task priority level |

```json
{
  "id": 1,
  "title": "Task title",
  "description": "Task description",
  "completed": false,
  "priority": "medium"
}
```

**Note:** The Task database model includes `created_at` and `updated_at` timestamps, but these are not included in the API response schema.

### PaginatedTaskResponse

Response schema for paginated list operations.

| Field | Type | Description |
|-------|------|-------------|
| `items` | array | Array of TaskResponse objects |
| `total` | integer | Total number of tasks matching the filter |
| `limit` | integer | Limit applied to this query |
| `offset` | integer | Offset applied to this query |

```json
{
  "items": [
    {
      "id": 1,
      "title": "Task title",
      "description": "Task description",
      "completed": false,
      "priority": "medium"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

---

## HTML Sanitization

All text fields (`title` and `description`) are automatically sanitized to remove HTML tags. This prevents XSS attacks and ensures data consistency.

**Sanitization Rules:**

1. HTML tags are stripped (e.g., `<script>alert('xss')</script>` becomes `alert('xss')`)
2. Title is trimmed of leading/trailing whitespace
3. Empty titles (after stripping) are rejected with 422 error

**Example of Sanitization:**

```bash
# Request with HTML in title
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "<b>Bold Task</b><script>alert(1)</script>",
    "description": "<p>Description with HTML</p>"
  }'
```

**Response (HTML stripped):**

```json
{
  "id": 1,
  "title": "Bold Taskalert(1)",
  "description": "Description with HTML",
  "completed": false,
  "priority": "medium"
}
```

---

## Authentication

The API uses JWT (JSON Web Token) authentication for protected endpoints. The authentication scheme uses HTTP Bearer tokens.

### Authentication Scheme

- **Type:** HTTP Bearer Token (JWT)
- **Header:** `Authorization: Bearer <token>`
- **Algorithm:** HS256
- **Token Expiry:** 24 hours

### Token Structure

JWT tokens contain the following claims:

- `sub` (string): User ID (stored as a string)
- `role` (string): User role (e.g., "user", "admin")
- `exp` (integer): Token expiration time (Unix timestamp)

**Example Payload:**

```json
{
  "sub": "123",
  "role": "user",
  "exp": 1713456789
}
```

### Obtaining a Token

Tokens are generated using the `create_token(user_id: int, role: str)` function from `app.auth`. This is typically done during login or user registration.

**Token Creation Example:**

```python
from app.auth import create_token

# Create a token for user ID 123 with default role
token = create_token(user_id=123)
# Returns: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Create a token for admin user
token = create_token(user_id=123, role="admin")
```

The token is valid for 24 hours from the time of creation.

### Using Tokens

Include the token in the `Authorization` header of your requests:

```bash
curl -X GET http://localhost:8000/api/v1/protected-endpoint \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Protected Endpoints

Currently, the task endpoints (`/api/v1/tasks/*`) do not require authentication. However, the authentication system is in place for future use.

### Token Verification

The `verify_token` dependency validates JWT tokens:

- Checks token signature and expiry
- Returns the token payload (including `sub` and `role` claims)
- Raises 401 Unauthorized for expired or invalid tokens

### Admin Access

The `require_admin` dependency checks for admin role in the token payload:

- Returns the token payload if the user has role="admin"
- Raises 403 Forbidden if the role claim is missing or not "admin"

### Error Responses

#### 401 Unauthorized

Returned when the token is missing, expired, or invalid.

```json
{
  "detail": "Token expired"
}
```

or

```json
{
  "detail": "Invalid token"
}
```

#### 403 Forbidden

Returned when the user doesn't have admin privileges (when `require_admin` dependency is used).

```json
{
  "detail": "Admin required"
}
```

### Example: Authenticated Request

```bash
# First, obtain a token (typically from a login endpoint)
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6InVzZXIiLCJleHAiOjE3MTIzNDU2Nzh9.signature"

# Use the token in a request
curl -X GET http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer $TOKEN"
```

---

## Rate Limiting

Rate limiting is implemented using a sliding window algorithm backed by Redis. This prevents API abuse and ensures fair usage.

### Rate Limit Configuration

- **Default Limit:** 100 requests per minute per client IP
- **Window Size:** 60 seconds (sliding window)
- **Exempt Endpoints:** `/health` endpoint is exempt from rate limiting
- **Header-based Identification:** Uses `X-Forwarded-For` header if present, otherwise client IP

### Rate Limit Headers

All responses include rate limit information in the headers:

| Header | Description |
|--------|-------------|
| `X-RateLimit-Limit` | Maximum requests allowed per window |
| `X-RateLimit-Remaining` | Remaining requests in current window |
| `X-RateLimit-Reset` | Unix timestamp when the window resets |

**Example Headers:**

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1713456820
```

### Rate Limit Exceeded

When the rate limit is exceeded, the API returns a 429 status code with retry information.

**Response:**

- **Status:** 429 Too Many Requests
- **Headers:**
  - `Retry-After`: Seconds until the request can be retried
  - `X-RateLimit-*`: Rate limit information
- **Body:**
  ```json
  {
    "detail": "Rate limit exceeded",
    "retry_after": 45
  }
  ```

**Example Request:**

```bash
curl -X GET http://localhost:8000/api/v1/tasks
```

**Example Response (rate limit exceeded):**

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
Retry-After: 45
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1713456820

{
  "detail": "Rate limit exceeded",
  "retry_after": 45
}
```

### Redis Unavailable

If Redis is unavailable, rate limiting fails open (allows the request) with a warning logged. The request proceeds normally without rate limit headers.

---

## Caching

Redis-backed caching is implemented for task queries to improve performance and reduce database load.

### Cache Behavior

- **Cache Backend:** Redis
- **Default TTL:** 300 seconds (5 minutes)
- **Cache Key Pattern:** `tasks:all:{completed}:{priority}:{limit}:{offset}`
- **Cache Invalidation:** Cache is invalidated on task creation, update, and deletion

### Cached Endpoints

The following endpoint responses are cached:

- `GET /api/v1/tasks` - Cached based on filter and pagination parameters

### Cache Headers

Currently, cache headers are not included in responses. Cache behavior is transparent to clients.

### Cache Miss

On cache miss, the API:

1. Queries the database
2. Serializes the results
3. Stores in Redis with 5-minute TTL
4. Returns the response

### Cache Hit

On cache hit, the API:

1. Retrieves cached data from Redis
2. Deserializes the response
3. Returns immediately without database query

### Cache Invalidation

Cache is automatically invalidated when:

- A new task is created (`POST /api/v1/tasks`)
- A task is updated (`PATCH /api/v1/tasks/{task_id}`)
- A task is deleted (`DELETE /api/v1/tasks/{task_id}`)

### Redis Unavailable

If Redis is unavailable:

- Cache operations fail silently
- API continues to serve requests from database
- Warning is logged

---

## Error Handling

The API uses standard HTTP status codes and returns error details in JSON format.

### Error Response Format

All error responses follow this structure:

```json
{
  "detail": "Error message describing what went wrong"
}
```

For validation errors (422), the format includes detailed field-level information:

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "field_name"],
      "msg": "Value error, specific error message",
      "input": "invalid_value"
    }
  ]
}
```

### HTTP Status Codes

| Status Code | Description | Common Causes |
|-------------|-------------|---------------|
| `200` | OK | Request successful |
| `201` | Created | Resource created successfully |
| `204` | No Content | Resource deleted successfully |
| `400` | Bad Request | Malformed JSON, missing required fields |
| `401` | Unauthorized | Missing or invalid authentication token |
| `403` | Forbidden | Valid token but insufficient privileges (admin required) |
| `404` | Not Found | Requested resource doesn't exist |
| `422` | Unprocessable Entity | Validation error (invalid field types, values too long) |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Unexpected server error |

### Example Error Responses

#### 400 Bad Request

```json
{
  "detail": "Invalid JSON format"
}
```

#### 401 Unauthorized - Token Expired

```json
{
  "detail": "Token expired"
}
```

#### 401 Unauthorized - Invalid Token

```json
{
  "detail": "Invalid token"
}
```

#### 403 Forbidden

```json
{
  "detail": "Admin required"
}
```

#### 404 Not Found

```json
{
  "detail": "Task not found"
}
```

#### 422 Unprocessable Entity - Empty Title

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "title"],
      "msg": "Value error, title cannot be empty",
      "input": ""
    }
  ]
}
```

#### 422 Unprocessable Entity - Title Too Long

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "title"],
      "msg": "Value error, title cannot exceed 255 characters",
      "input": "a very long title..."
    }
  ]
}
```

#### 429 Too Many Requests

```json
{
  "detail": "Rate limit exceeded",
  "retry_after": 45
}
```

---

## Complete Example Workflow

Here's a complete workflow demonstrating the main API features:

```bash
#!/bin/bash

# Base URL
BASE_URL="http://localhost:8000"

# 1. Health check
echo "=== Health Check ==="
curl -s "$BASE_URL/health" | jq .

# 2. Create tasks
echo -e "\n=== Create Task 1 ==="
TASK1=$(curl -s -X POST "$BASE_URL/api/v1/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Write API documentation",
    "description": "Document all endpoints",
    "priority": "high"
  }')
echo "$TASK1" | jq .
TASK1_ID=$(echo "$TASK1" | jq -r '.id')

echo -e "\n=== Create Task 2 ==="
TASK2=$(curl -s -X POST "$BASE_URL/api/v1/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implement caching",
    "description": "Add Redis caching",
    "priority": "high",
    "completed": true
  }')
echo "$TASK2" | jq .

# 3. List all tasks
echo -e "\n=== List All Tasks ==="
curl -s "$BASE_URL/api/v1/tasks" | jq .

# 4. Filter by priority
echo -e "\n=== Filter by High Priority ==="
curl -s "$BASE_URL/api/v1/tasks?priority=high" | jq .

# 5. Filter by completion status
echo -e "\n=== Filter by Completed ==="
curl -s "$BASE_URL/api/v1/tasks?completed=true" | jq .

# 6. Get single task
echo -e "\n=== Get Single Task ==="
curl -s "$BASE_URL/api/v1/tasks/$TASK1_ID" | jq .

# 7. Update task (mark as completed)
echo -e "\n=== Update Task ==="
curl -s -X PATCH "$BASE_URL/api/v1/tasks/$TASK1_ID" \
  -H "Content-Type: application/json" \
  -d '{"completed": true}' | jq .

# 8. Delete task
echo -e "\n=== Delete Task ==="
curl -s -X DELETE "$BASE_URL/api/v1/tasks/$TASK1_ID"
echo "Task deleted (HTTP 204)"

# 9. Verify deletion (should return 404)
echo -e "\n=== Verify Deletion (404 Expected) ==="
curl -s "$BASE_URL/api/v1/tasks/$TASK1_ID" | jq .
```

---

## Configuration

The API behavior can be configured through environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./tasks.db` | Database connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |
| `SECRET_KEY` | `dev-secret-change-in-prod` | JWT signing key |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token expiry (minutes) - **Note: Currently uses 24 hours instead** |
| `RATE_LIMIT_PER_MINUTE` | `100` | Requests per minute per client |

**Note:** Configuration is loaded from `.env` file if present.

---

## Limitations and Known Issues

1. **Token Expiry Mismatch:** The `ACCESS_TOKEN_EXPIRE_MINUTES` setting is configured but the actual token expiry is hardcoded to 24 hours in `auth.py`.

2. **No Enum Validation on Priority:** The `priority` field accepts any string value. There's no validation to ensure it's one of "low", "medium", "high".

3. **Task Endpoints Not Protected:** All task endpoints currently allow anonymous access. Authentication is in place but not enforced on these endpoints.

4. **Cache Headers Not Included:** While caching is implemented, cache-related headers (e.g., `X-Cache-Hit`) are not included in responses.

5. **No Bulk Operations:** There's no endpoint for bulk creating, updating, or deleting tasks.

---

**Documentation Version:** 1.0.0  
**Last Updated:** 2026-04-23  
**API Version:** 0.1.0
