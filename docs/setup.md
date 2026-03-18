# Setup Guide

## Prerequisites

| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Backend runtime |
| Ollama | latest | LLM inference engine |
| Home Assistant | 2024.1+ | Smart home control (optional) |
| OpenClaw | latest | Pipeline integration (optional) |
| Docker | 24+ | Containerised deployment (optional) |

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/JeremyLakeyJr/swarm-ui.git
cd swarm-ui
```

### 2. Set Up Python Environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your values:

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_SECRET_KEY` | `change-me-to-a-random-secret` | JWT signing key – **change in production** |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server address |
| `OLLAMA_MODEL` | `llama3` | Default model for chat |
| `HOMEASSISTANT_URL` | `http://homeassistant.local:8123` | Home Assistant URL |
| `HOMEASSISTANT_TOKEN` | *(empty)* | Long-lived access token |
| `OPENCLAW_BASE_URL` | `http://localhost:9000` | OpenClaw server address |
| `OPENCLAW_API_KEY` | *(empty)* | OpenClaw API key |

### 4. Install Ollama

Follow [https://ollama.com/download](https://ollama.com/download) and then:

```bash
ollama pull llama3
```

### 5. Start the Application

```bash
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

Visit <http://localhost:8000>.

### 6. Docker Deployment

```bash
docker compose up -d
```

## Troubleshooting

- **Ollama connection refused**: Ensure Ollama is running (`ollama serve`).
- **Home Assistant 401**: Verify your long-lived access token is correct.
- **OpenClaw timeout**: Check that the OpenClaw service is reachable at the configured URL.
