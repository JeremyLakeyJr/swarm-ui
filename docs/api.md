# API Reference

Base URL: `http://localhost:8000`

All endpoints (except `/api/health`) require a Bearer token when `APP_SECRET_KEY` is set to a non-default value.

---

## Health

### `GET /api/health`

Returns connectivity status for all integrated services.

**Response:**

```json
{
  "status": "ok",
  "services": {
    "ollama": "connected",
    "homeassistant": "unavailable",
    "openclaw": "unavailable",
    "agent_framework": "available"
  }
}
```

---

## Chat (Ollama)

### `GET /api/chat/models`

List models available on the Ollama server.

### `POST /api/chat/completions`

Non-streaming chat completion.

**Request:**

```json
{
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "model": "llama3"
}
```

**Response:**

```json
{
  "message": {"role": "assistant", "content": "Hi there!"},
  "model": "llama3",
  "done": true
}
```

### `POST /api/chat/stream`

Streaming chat via Server-Sent Events.

---

## Agents (Autogen)

### `POST /api/agents/run`

Execute a multi-agent task.

**Request:**

```json
{
  "prompt": "Summarise the latest news",
  "max_rounds": 10,
  "timeout": 120
}
```

**Response:**

```json
{
  "success": true,
  "messages": [...],
  "summary": "Here is a summary…",
  "error": null
}
```

---

## Home Assistant

### `GET /api/homeassistant/states`

Fetch all entity states.

### `GET /api/homeassistant/states/{entity_id}`

Fetch a single entity state.

### `POST /api/homeassistant/services/call`

Call a Home Assistant service.

**Request:**

```json
{
  "domain": "light",
  "service": "turn_on",
  "entity_id": "light.living_room",
  "data": {"brightness": 255}
}
```

### `GET /api/homeassistant/services`

List all available services.

---

## OpenClaw

### `GET /api/openclaw/pipelines`

List available pipelines.

### `POST /api/openclaw/pipelines/run`

Trigger a pipeline.

**Request:**

```json
{
  "pipeline_id": "etl-daily",
  "params": {"date": "2025-01-01"}
}
```

### `GET /api/openclaw/pipelines/runs/{run_id}`

Check pipeline run status.

### `POST /api/openclaw/data`

Send data to an OpenClaw module.

**Request:**

```json
{
  "endpoint": "ingest",
  "data": {"key": "value"}
}
```

---

## Agent Framework

### `POST /api/agent-framework/run`

Run an AI agent using the Microsoft Agent Framework.

**Request:**

```json
{
  "prompt": "Summarize the latest news",
  "agent_name": "news_agent",
  "instructions": "You are a news summarization specialist.",
  "model": "",
  "metadata": {}
}
```

**Response:**

```json
{
  "success": true,
  "messages": [
    {"role": "user", "content": "Summarize the latest news"},
    {"role": "assistant", "content": "Here is a summary…"}
  ],
  "summary": "Here is a summary…",
  "error": null
}
```
