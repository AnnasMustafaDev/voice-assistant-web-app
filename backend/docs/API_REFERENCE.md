# API Reference

Complete API endpoint documentation for the Reception Voice Agent backend.

## Base URL

```
http://localhost:8000
```

## Authentication

All endpoints (except `/health`) support optional JWT Bearer token authentication:

```bash
Authorization: Bearer <your-jwt-token>
```

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error description"
}
```

Common status codes:
- `200` OK
- `201` Created
- `204` No Content
- `400` Bad Request
- `404` Not Found
- `500` Internal Server Error

---

## Health Check

### Get Health Status

```http
GET /health
```

**Response** (200):
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

---

## Tenants

### Create Tenant

```http
POST /tenants
Content-Type: application/json

{
  "name": "Tony's Restaurant",
  "industry": "hospitality",
  "language": "en"
}
```

**Parameters**:
- `name` (string, required) - Tenant name
- `industry` (string, optional) - Business industry
- `language` (string, default: "en") - Default language (en, de, it, etc.)

**Response** (201):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Tony's Restaurant",
  "industry": "hospitality",
  "language": "en",
  "created_at": "2024-12-21T10:30:00"
}
```

### Get Tenant

```http
GET /tenants/{tenant_id}
```

**Parameters**:
- `tenant_id` (UUID, path) - Tenant ID

**Response** (200): Same as create response

### Update Tenant

```http
PATCH /tenants/{tenant_id}
Content-Type: application/json

{
  "industry": "fine_dining",
  "language": "it"
}
```

**Parameters**:
- `tenant_id` (UUID, path) - Tenant ID
- All fields optional

**Response** (200): Updated tenant

### Delete Tenant

```http
DELETE /tenants/{tenant_id}
```

**Response** (204): No content

---

## Agents

### Create Agent

```http
POST /agents
Content-Type: application/json

{
  "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Front Desk",
  "type": "receptionist",
  "system_prompt": "You are a professional receptionist...",
  "voice": "en-US-Neural2-A"
}
```

**Parameters**:
- `tenant_id` (UUID, required) - Parent tenant
- `name` (string, required) - Agent name
- `type` (string, required) - receptionist | real_estate | custom
- `system_prompt` (string, optional) - Custom system prompt
- `voice` (string, default: "en-US-Neural2-A") - Voice ID

**Response** (201):
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Front Desk",
  "type": "receptionist",
  "system_prompt": "You are a professional receptionist...",
  "voice": "en-US-Neural2-A",
  "created_at": "2024-12-21T10:31:00"
}
```

### Get Agent

```http
GET /agents/{agent_id}
```

**Response** (200): Agent object

### Update Agent

```http
PATCH /agents/{agent_id}
Content-Type: application/json

{
  "system_prompt": "Updated prompt",
  "voice": "en-US-Neural2-C"
}
```

**Response** (200): Updated agent

### Delete Agent

```http
DELETE /agents/{agent_id}
```

**Response** (204): No content

---

## Chat

### Send Message

```http
POST /chat/message
Content-Type: application/json

{
  "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
  "agent_id": "660e8400-e29b-41d4-a716-446655440001",
  "conversation_id": "770e8400-e29b-41d4-a716-446655440002",
  "message": "I want to book a table for 4 people tonight"
}
```

**Parameters**:
- `tenant_id` (UUID, required) - Tenant ID
- `agent_id` (UUID, required) - Agent ID
- `conversation_id` (UUID, optional) - Continue existing conversation
- `message` (string, required) - User message

**Response** (200):
```json
{
  "conversation_id": "770e8400-e29b-41d4-a716-446655440002",
  "reply": "Sure! For how many people and what time would you prefer?",
  "message_id": "880e8400-e29b-41d4-a716-446655440003"
}
```

**Features**:
- Creates conversation if `conversation_id` not provided
- Uses RAG to retrieve relevant context
- Caches responses for identical queries
- Stores message history

---

## Voice Streaming (WebSocket)

### Connect

```javascript
const ws = new WebSocket('ws://localhost:8000/voice/stream');
```

### Initialize Session

Send after connection:

```javascript
ws.send(JSON.stringify({
  "event": "init",
  "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
  "agent_id": "660e8400-e29b-41d4-a716-446655440001",
  "conversation_id": "optional-uuid",
  "language": "en"
}));
```

### Send Audio Chunk

```javascript
// Encode audio bytes to base64
const audioB64 = btoa(String.fromCharCode(...audioBytes));

ws.send(JSON.stringify({
  "event": "audio_chunk",
  "data": audioB64
}));
```

### Receive Transcript

```javascript
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  if (message.event === "transcript_partial") {
    console.log("Partial transcript:", message.text);
  }
};
```

### Receive Audio Response

```javascript
if (message.event === "audio_response") {
  // Decode base64 to audio bytes
  const audioBytes = Uint8Array.from(
    atob(message.data),
    c => c.charCodeAt(0)
  );
  // Play audio
}
```

### End Stream

```javascript
ws.send(JSON.stringify({
  "event": "end_stream"
}));
```

---

## Knowledge Base (RAG)

### Upload Document

```http
POST /knowledge/upload
Content-Type: multipart/form-data

tenant_id: 550e8400-e29b-41d4-a716-446655440000
source: menu
title: Restaurant Menu 2024
file: <binary-file>
```

**Parameters**:
- `tenant_id` (UUID, required) - Tenant ID
- `source` (string, required) - pdf | menu | listing | policy
- `title` (string, required) - Document title
- `file` (file, required) - Document file (PDF, TXT, etc.)

**Response** (200):
```json
{
  "id": "990e8400-e29b-41d4-a716-446655440004",
  "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
  "source": "menu",
  "title": "Restaurant Menu 2024",
  "content": "First 500 chars of content...",
  "created_at": "2024-12-21T10:32:00"
}
```

### Ingest Text Document

```http
POST /knowledge/ingest
Content-Type: application/json

{
  "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
  "source": "menu",
  "title": "Restaurant Menu",
  "content": "Appetizers: ...\nMain Courses: ..."
}
```

**Parameters**:
- `tenant_id` (UUID, required)
- `source` (string, required)
- `title` (string, optional)
- `content` (string, required) - Text content

**Response** (200): Document object

### Search Knowledge Base

```http
GET /knowledge/search?tenant_id=550e8400-e29b-41d4-a716-446655440000&query=main+courses&top_k=3&source=menu
```

**Parameters** (query):
- `tenant_id` (UUID, required) - Tenant ID
- `query` (string, required) - Search query
- `top_k` (int, default: 3) - Number of results
- `source` (string, optional) - Filter by source (pdf, menu, listing, policy)

**Response** (200):
```json
[
  {
    "id": "990e8400-e29b-41d4-a716-446655440004",
    "title": "Restaurant Menu 2024",
    "source": "menu",
    "content": "First 500 characters..."
  },
  ...
]
```

**Features**:
- Vector similarity search (pgvector)
- Fallback to keyword search
- Returns top-k most relevant documents
- Documents automatically used as context in chat

### List Documents

```http
GET /knowledge/list?tenant_id=550e8400-e29b-41d4-a716-446655440000&source=menu&limit=50
```

**Parameters** (query):
- `tenant_id` (UUID, required)
- `source` (string, optional) - Filter by source
- `limit` (int, default: 50) - Max results

**Response** (200):
```json
[
  {
    "id": "990e8400-e29b-41d4-a716-446655440004",
    "title": "Restaurant Menu 2024",
    "source": "menu",
    "created_at": "2024-12-21T10:32:00"
  },
  ...
]
```

---

## Response Formats

### Standard Paginated Response

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 50
}
```

### Error Response

```json
{
  "detail": "Descriptive error message"
}
```

### Validation Error Response

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "Field validation error",
      "type": "value_error"
    }
  ]
}
```

---

## Rate Limiting

Not implemented yet, but recommended for production:
- 100 requests/minute per IP
- 1000 requests/hour per tenant
- WebSocket: 10 concurrent connections per tenant

---

## Async Considerations

All endpoints are fully async and non-blocking:
- Database queries are async
- Groq API calls are async
- WebSocket handling is async
- Supports high concurrency (100+ simultaneous connections)

---

## CORS Configuration

Allowed origins (configurable in .env):
```
http://localhost:3000
http://localhost:8080
http://127.0.0.1:3000
```

Add your frontend URL to `CORS_ORIGINS` in `.env`.

---

## Example Workflows

### Create Full Conversation

```bash
# 1. Create tenant
curl -X POST http://localhost:8000/tenants \
  -H "Content-Type: application/json" \
  -d '{"name":"My Restaurant","industry":"hospitality"}'

# Store tenant_id from response

# 2. Create agent
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id":"550e8400...",
    "name":"Receptionist",
    "type":"receptionist"
  }'

# Store agent_id from response

# 3. Ingest menu
curl -X POST http://localhost:8000/knowledge/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id":"550e8400...",
    "source":"menu",
    "title":"Menu",
    "content":"..."
  }'

# 4. Send message
curl -X POST http://localhost:8000/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id":"550e8400...",
    "agent_id":"660e8400...",
    "message":"Book a table"
  }'
```

### Voice Conversation (JavaScript)

```javascript
// Connect
const ws = new WebSocket('ws://localhost:8000/voice/stream');

ws.onopen = () => {
  // Init
  ws.send(JSON.stringify({
    event: 'init',
    tenant_id: '550e8400...',
    agent_id: '660e8400...'
  }));
  
  // Send audio
  const audioChunk = btoa(String.fromCharCode(...bytes));
  ws.send(JSON.stringify({
    event: 'audio_chunk',
    data: audioChunk
  }));
};

ws.onmessage = (e) => {
  const msg = JSON.parse(e.data);
  if (msg.event === 'audio_response') {
    // Play audio
  }
};
```

---

For full documentation, see README.md, ARCHITECTURE.md, and QUICK_START.md.
