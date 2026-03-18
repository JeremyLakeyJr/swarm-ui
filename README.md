# Swarm UI

AI-powered interface integrating **Ollama**, **Microsoft Autogen**, **Home Assistant**, and **OpenClaw** into a unified, responsive web application.

## Features

| Area | Description |
|------|-------------|
| **Chat** | Natural language conversation powered by Ollama LLMs |
| **Agent Orchestration** | Multi-agent workflows via Microsoft Autogen |
| **Smart Home** | Monitor and control devices through Home Assistant |
| **OpenClaw** | Pipeline management and data exchange with OpenClaw modules |
| **Security** | JWT-based authentication with configurable API keys |
| **Real-time Status** | Live health indicators for all connected services |

## Quick Start

### Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com) running locally (default `http://localhost:11434`)
- *(Optional)* Home Assistant instance with a long-lived access token
- *(Optional)* OpenClaw service

### Installation

```bash
# Clone the repository
git clone https://github.com/JeremyLakeyJr/swarm-ui.git
cd swarm-ui

# Create a virtual environment and install dependencies
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy and edit configuration
cp .env.example .env
# Edit .env with your settings
```

### Run the Server

```bash
uvicorn backend.app:app --reload
```

Open <http://localhost:8000> in your browser.

### Docker

```bash
docker compose up -d
```

This starts both the Swarm UI backend and an Ollama instance.

## Running Tests

```bash
pip install -r requirements.txt
pytest
```

## Project Structure

```
swarm-ui/
├── backend/
│   ├── app.py                  # FastAPI entry point
│   ├── config.py               # Environment-based configuration
│   ├── auth/security.py        # JWT authentication
│   ├── integrations/
│   │   ├── ollama_client.py    # Ollama chat & model API
│   │   ├── autogen_agent.py    # Autogen multi-agent orchestration
│   │   ├── homeassistant.py    # Home Assistant REST API client
│   │   └── openclaw.py         # OpenClaw pipeline & data API
│   ├── routes/                 # API endpoint handlers
│   └── models/schemas.py       # Pydantic request/response models
├── frontend/
│   ├── index.html              # Single-page application
│   ├── css/style.css           # Responsive dark theme
│   └── js/app.js               # Client-side logic
├── tests/                      # Pytest test suite
├── docs/                       # Extended documentation
├── docker-compose.yml          # Container orchestration
├── Dockerfile
├── requirements.txt
└── .env.example                # Configuration template
```

## Documentation

- [Setup Guide](docs/setup.md)
- [Architecture](docs/architecture.md)
- [Integration Guide](docs/integrations.md)
- [API Reference](docs/api.md)

## License

This project is provided as-is for educational and experimental purposes.
