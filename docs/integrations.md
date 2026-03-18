# Integration Guide

This document describes how each external system is integrated and how to extend the integrations.

---

## 1. Ollama (AI Backend)

**Module:** `backend/integrations/ollama_client.py`

The `OllamaClient` communicates with the Ollama HTTP API:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `list_models()` | `GET /api/tags` | List available models |
| `chat()` | `POST /api/chat` | Non-streaming completion |
| `chat_stream()` | `POST /api/chat` | Streaming completion |
| `health_check()` | `GET /api/tags` | Connectivity test |

### Configuration

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

---

## 2. Microsoft Autogen (Agent Orchestration)

**Module:** `backend/integrations/autogen_agent.py`

The `AutogenOrchestrator` creates a round-robin agent team using Autogen's `agentchat` API. It connects to Ollama's OpenAI-compatible endpoint at `{OLLAMA_BASE_URL}/v1`.

### Configuration

```env
AUTOGEN_DEFAULT_LLM_PROVIDER=ollama
AUTOGEN_MAX_ROUNDS=10
AUTOGEN_TIMEOUT=120
```

### Extending Agents

To add custom agents, modify `AutogenOrchestrator.run_task()`:

```python
from autogen_agentchat.agents import AssistantAgent

custom_agent = AssistantAgent(
    name="domain_expert",
    model_client=model_client,
    system_message="You are an expert in …",
)
team = RoundRobinGroupChat(
    participants=[assistant, custom_agent],
    termination_condition=termination,
)
```

---

## 3. Home Assistant (Smart Home)

**Module:** `backend/integrations/homeassistant.py`

The `HomeAssistantClient` uses the Home Assistant REST API with Bearer token auth.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `get_states()` | `GET /api/states` | All entity states |
| `get_entity_state()` | `GET /api/states/{id}` | Single entity state |
| `call_service()` | `POST /api/services/{domain}/{service}` | Invoke a service |
| `get_services()` | `GET /api/services` | List services |
| `health_check()` | `GET /api/` | Connectivity test |

### Configuration

```env
HOMEASSISTANT_URL=http://homeassistant.local:8123
HOMEASSISTANT_TOKEN=your-long-lived-access-token
```

### Generating a Token

In Home Assistant: **Profile → Long-Lived Access Tokens → Create Token**.

---

## 4. OpenClaw (Data Pipelines)

**Module:** `backend/integrations/openclaw.py`

The `OpenClawClient` interacts with OpenClaw's pipeline API.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `list_pipelines()` | `GET /api/pipelines` | Available pipelines |
| `run_pipeline()` | `POST /api/pipelines/run` | Start a pipeline |
| `get_pipeline_status()` | `GET /api/pipelines/runs/{id}` | Poll run status |
| `send_data()` | `POST /api/{endpoint}` | Send data to a module |
| `health_check()` | `GET /health` | Connectivity test |

### Configuration

```env
OPENCLAW_BASE_URL=http://localhost:9000
OPENCLAW_API_KEY=your-openclaw-api-key
```

---

## Adding a New Integration

1. Create `backend/integrations/my_service.py` with an async client class.
2. Add configuration fields to `backend/config.py` → `Settings`.
3. Create route handlers in `backend/routes/my_service.py`.
4. Register the router in `backend/app.py`.
5. Add a health-check call in `backend/routes/health.py`.
6. Write tests in `tests/test_my_service.py`.
