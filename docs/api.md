# SmokeTest API Documentation

## Overview

The SmokeTest App API provides a simple REST interface for managing tasks with JWT authentication support.

**Base URL:** `http://localhost:8000`

**API Version:** `v1`

## Endpoints

### Health Check

#### `GET /health`

Returns the current status of the API.

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

List all tasks.

**Response:**

- **Status:** 200 OK
- **Content-Type:** application/json
- **Body:** Array of TaskResponse objects
  ```json
  [
    {
      "id": 1,
      "title": "Task title",
      "description": "Task description",
      "completed": false,
      "priority": "medium"
    }
  ]
  ```

**Example Request:**

```bash
curl -X GET http://localhost:8000/api/v1/tasks
```

**Example Response:**

```json
[
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
]
```

---

#### `POST /api/v1/tasks`

Create a new task.

**Request:**

- **Content-Type:** application/json
- **Body:** TaskCreate object
  - `title` (string, required): Task title (max 255 characters)
  - `description` (string, optional): Task description
  - `priority` (string, optional): Task priority level (default: "medium")

**Response:**

- **Status:** 201 Created
- **Content-Type:** application/json
- **Body:** TaskResponse object
  - `id` (integer): Task ID
  - `title` (string): Task title
  - `description` (string | null): Task description
  - `completed` (boolean): Task completion status
  - `priority` (string): Task priority level

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

Update a task (partial update supported).

**Parameters:**

- `task_id` (path, integer, required): The ID of the task to update

**Request:**

- **Content-Type:** application/json
- **Body:** TaskUpdate object (all fields optional)
  - `title` (string, optional): New task title
  - `description` (string, optional): New task description
  - `completed` (boolean, optional): New completion status
  - `priority` (string, optional): New priority level

**Response:**

- **Status:** 200 OK
- **Content-Type:** application/json
- **Body:** TaskResponse object

**Example Request:**

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

**Error Response:**

- **Status:** 404 Not Found
- **Body:**
  ```json
  {
    "detail": "Task not found"
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
| `title` | string | Yes | - | Task title (max 255 characters) |
| `description` | string | No | null | Optional task description |
| `priority` | string | No | "medium" | Task priority level |

```json
{
  "title": "New task",
  "description": "Task description",
  "priority": "medium"
}
```

### TaskUpdate

Request schema for updating an existing task. All fields are optional.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | No | New task title |
| `description` | string | No | New task description |
| `completed` | boolean | No | New completion status |
| `priority` | string | No | New priority level |

```json
{
  "completed": true
}
```

### TaskResponse

Response schema for task operations.

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Task ID (auto-generated) |
| `title` | string | Task title |
| `description` | string \| null | Task description (null if not set) |
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

---

## Authentication

The API uses JWT (JSON Web Token) authentication for protected endpoints. The authentication scheme uses HTTP Bearer tokens.

### Authentication Scheme

- **Type:** HTTP Bearer Token (JWT)
- **Header:** `Authorization: Bearer <token>`
- **Algorithm:** HS256
- **Token Expiry:** 30 minutes

### Token Structure

JWT tokens contain the following claims:

- `sub` (string): User ID (stored as a string)
- `exp` (integer): Token expiration time (Unix timestamp)

**Note:** The `role` claim is not currently included in the token payload. This is a known limitation that affects the `require_admin` dependency (see below).

### Obtaining a Token

Tokens are generated using the `create_token(user_id: int)` function from `app.auth`. This is typically done during login or user registration.

**Token Creation Example:**

```python
from app.auth import create_token

# Create a token for user ID 123
token = create_token(user_id=123)
# Returns: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

The token is valid for 30 minutes from the time of creation (as configured by `access_token_expire_minutes` in the application settings).

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
- Returns the token payload (including `sub` claim)
- Raises 401 Unauthorized for expired or invalid tokens

### Admin Access

The `require_admin` dependency checks for admin role in the token payload:

- Returns the token payload if the user has role="admin"
- Raises 403 Forbidden if the role claim is missing or not "admin"

**Known Limitation:** The `create_token` function does not include the `role` claim in the token payload. Consequently, the `require_admin` dependency will always reject tokens, even for valid admin users. This is a documented bug that will be addressed in a future update.

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
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzEyMzQ1Njc4fQ.signature"

# Use the token in a request
curl -X GET http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer $TOKEN"
```

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

### HTTP Status Codes

| Status Code | Description | Common Causes |
|-------------|-------------|---------------|
| `400` | Bad Request | Malformed JSON, missing required fields |
| `401` | Unauthorized | Missing or invalid authentication token |
| `403` | Forbidden | Valid token but insufficient privileges (admin required) |
| `404` | Not Found | Requested resource doesn't exist |
| `422` | Unprocessable Entity | Validation error (invalid field types, values too long) |

### Example Error Responses

#### 400 Bad Request

```json
{
  "detail": "Invalid JSON format"
}
```

#### 404 Not Found

```json
{
  "detail": "Task not found"
}
```

---

## Placeholder Features

The following features are documented as "not yet implemented" in the current codebase:

### Caching

A caching backend stub (`CacheBackend` class) exists but is not currently implemented. The cache would store task query results to improve performance.

**Status:** Not yet implemented

### Rate Limiting

Rate limiting is not currently enforced on any API endpoints.

**Status:** Not yet implemented

### Filtering and Pagination

Query parameters for filtering tasks (by status, priority, etc.) and pagination (limit, offset) are not currently supported.

**Status:** Not yet implemented

