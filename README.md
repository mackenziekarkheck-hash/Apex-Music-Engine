# APEX Engine

**Autonomous Aural Architectures for Algorithmic Rap Composition**

APEX Engine is a multi-agent AI framework that generates, analyzes, and iteratively refines rap music using advanced algorithmic techniques and the Sonauto API.

## Quick Start

### Prerequisites

- **Python 3.11+** - [Download Python](https://python.org/downloads)
- **API Keys** (optional, for full functionality):
  - [OpenAI API Key](https://platform.openai.com/api-keys) - For GPT-4o lyric generation
  - [Sonauto API Key](https://sonauto.ai/) - For Sonauto audio generation

### Installation

```bash
# 1. Clone or download this repository
git clone <repository-url>
cd apex-engine

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment (optional)
cp .env.example .env
# Edit .env and add your API keys
```

### Running the Application

**Linux/macOS:**
```bash
./run.sh
```

**Windows:**
```cmd
run.bat
```

**Manual Start:**
```bash
cd apex_engine
python -m web.app
```

Then open **http://localhost:5000** in your browser.

## Features

- **Web UI** - Project-based workspace for composing rap songs
- **Multi-Agent Analysis** - BarsAnalyzer, FlowAnalyzer, VowelAnalyzer, MemeAnalyzer
- **Rhyme Optimization** - Raplyzer Protocol for phonetic analysis
- **Psychoacoustic Metrics** - Frisson detection, syncopation index, earworm scoring
- **AI-Powered Generation** - GPT-4o for lyrics, Sonauto for audio
- **Per-Field AI Optimization** - Context-aware improvements based on agent analysis

## Modes

### Web UI (Default)
Full-featured browser interface for song project management.

### CLI Mode
```bash
./run.sh --cli           # Interactive prompt mode
./run.sh --demo          # Run demonstration
python apex_engine/main.py --help  # See all CLI options
```

### Simulation Mode
If API keys are not configured, the application runs in **Simulation Mode**:
- Lyrics are generated using template-based simulation
- Audio generation is disabled
- All UI features remain functional for development/testing

## Documentation

- **[LOCAL_DEPLOYMENT.md](LOCAL_DEPLOYMENT.md)** - Comprehensive deployment guide
- **[replit.md](replit.md)** - Technical architecture documentation

## Project Structure

```
apex_engine/
├── config/           # Configuration files (genres, tags, knowledge base)
├── src/
│   ├── agents/       # Analysis agents (lyrical, cultural, audio)
│   ├── core/         # Orchestration, LLM client, project manager
│   └── utils/        # Utilities and helpers
├── web/
│   ├── templates/    # HTML templates
│   ├── static/       # CSS and assets
│   └── app.py        # Flask application
├── projects/         # Saved song projects
└── main.py           # CLI entry point
```

## API Costs

| Service | Approximate Cost |
|---------|-----------------|
| GPT-4o (lyrics) | ~$0.01-0.05 per generation |
| Sonauto (audio) | $0.075 per generation |

## Troubleshooting

See [LOCAL_DEPLOYMENT.md](LOCAL_DEPLOYMENT.md#troubleshooting) for common issues and solutions.

## License

Copyright 2024-2025. All rights reserved.
