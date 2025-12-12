# APEX Engine - Local Deployment Reference

Comprehensive guide for downloading and running APEX Engine on your local machine.

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation Guide](#installation-guide)
   - [Windows](#windows-installation)
   - [macOS](#macos-installation)
   - [Linux](#linux-installation)
3. [API Configuration](#api-configuration)
   - [OpenAI Setup](#openai-api-setup)
   - [Fal.ai/Sonauto Setup](#falai-sonauto-setup)
4. [Running the Application](#running-the-application)
5. [Configuration Options](#configuration-options)
6. [Project Architecture](#project-architecture)
7. [Feature Reference](#feature-reference)
8. [Troubleshooting](#troubleshooting)
9. [Development Guide](#development-guide)

---

## System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| **Operating System** | Windows 10+, macOS 10.15+, Linux (Ubuntu 20.04+) |
| **Python** | 3.11 or higher |
| **RAM** | 4 GB minimum (8 GB recommended for audio analysis) |
| **Storage** | 2 GB for installation + space for projects |
| **Network** | Internet connection for API calls |

### Recommended Requirements

- **Python 3.12** for best performance
- **8+ GB RAM** for smooth audio processing with librosa
- **SSD storage** for faster project loading
- Modern browser (Chrome, Firefox, Safari, Edge)

---

## Installation Guide

### Windows Installation

#### Step 1: Install Python

1. Download Python 3.11+ from [python.org/downloads](https://python.org/downloads)
2. **IMPORTANT**: Check "Add Python to PATH" during installation
3. Verify installation:
   ```cmd
   python --version
   ```

#### Step 2: Download APEX Engine

Option A - Git Clone:
```cmd
git clone <repository-url>
cd apex-engine
```

Option B - Download ZIP:
1. Download the repository as ZIP
2. Extract to your desired location
3. Open Command Prompt in that folder

#### Step 3: Create Virtual Environment

```cmd
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your command prompt.

#### Step 4: Install Dependencies

```cmd
pip install -r requirements.txt
```

This may take 2-5 minutes depending on your connection.

#### Step 5: Configure Environment

```cmd
copy .env.example .env
notepad .env
```

Add your API keys (see [API Configuration](#api-configuration)).

#### Step 6: Run the Application

```cmd
run.bat
```

Or manually:
```cmd
cd apex_engine
python -m web.app
```

Open http://localhost:5000 in your browser.

---

### macOS Installation

#### Step 1: Install Python

**Using Homebrew (recommended):**
```bash
brew install python@3.12
```

**Or download from python.org:**
1. Download the macOS installer from [python.org/downloads](https://python.org/downloads)
2. Run the installer

Verify:
```bash
python3 --version
```

#### Step 2: Download APEX Engine

```bash
git clone <repository-url>
cd apex-engine
```

#### Step 3: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: On macOS, you may need Xcode Command Line Tools for some packages:
```bash
xcode-select --install
```

#### Step 5: Configure Environment

```bash
cp .env.example .env
nano .env  # or use any text editor
```

#### Step 6: Run the Application

```bash
./run.sh
```

---

### Linux Installation

#### Step 1: Install Python and Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip libsndfile1
```

**Fedora:**
```bash
sudo dnf install python3.11 python3-pip libsndfile
```

**Arch Linux:**
```bash
sudo pacman -S python python-pip libsndfile
```

#### Step 2: Download and Setup

```bash
git clone <repository-url>
cd apex-engine
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Step 3: Configure and Run

```bash
cp .env.example .env
nano .env  # Add your API keys
./run.sh
```

---

## API Configuration

APEX Engine uses two external APIs for full functionality. Both are optional - the application works in "Simulation Mode" without them.

### OpenAI API Setup

OpenAI provides GPT-4o for intelligent lyric generation and optimization.

#### Getting Your API Key

1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up or log in
3. Navigate to **API Keys** section
4. Click **"Create new secret key"**
5. Copy the key immediately (it won't be shown again)

#### Adding to APEX Engine

Edit your `.env` file:
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxx
```

#### Pricing

- GPT-4o: ~$0.01-0.05 per lyric generation (varies by length)
- GPT-4o-mini: ~$0.001-0.01 per generation (if configured)

### Fal.ai/Sonauto Setup

Fal.ai provides the Sonauto API for AI-powered music generation.

#### Getting Your API Key

1. Go to [sonauto.ai](https://sonauto.ai)
2. Sign up for an account
3. Go to **Dashboard** → **API Keys**
4. Create a new key and copy it

#### Adding to APEX Engine

Edit your `.env` file:
```
SONAUTO_API_KEY=your_sonauto_api_key_here
```

#### Pricing

- Audio generation: **$0.075 per generation**
- Inpainting/extending: **$0.075 per operation**

---

## Running the Application

### Quick Start Commands

| Platform | Command | Description |
|----------|---------|-------------|
| Windows | `run.bat` | Start web UI |
| Windows | `run.bat --cli` | Interactive CLI |
| Windows | `run.bat --demo` | Run demo mode |
| Linux/Mac | `./run.sh` | Start web UI |
| Linux/Mac | `./run.sh --cli` | Interactive CLI |
| Linux/Mac | `./run.sh --demo` | Run demo mode |

### Manual Start (All Platforms)

```bash
# Activate virtual environment first
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Start web UI
cd apex_engine
python -m web.app

# OR start CLI
python apex_engine/main.py --interactive
```

### Accessing the Web UI

After starting, open your browser to:
- **http://localhost:5000**

The interface will show:
- Dashboard with existing projects
- "+ New Project" button to create a song
- Project workspaces for composing and analyzing

---

## Configuration Options

### Environment Variables

Create a `.env` file in the project root with these options:

```bash
# Required for full functionality
SONAUTO_API_KEY=your_sonauto_api_key
OPENAI_API_KEY=your_openai_api_key

# Optional configuration
SECRET_KEY=your_flask_secret_key    # For session security
FLASK_DEBUG=1                        # Enable debug mode (0 for production)
HOST=0.0.0.0                         # Server bind address
PORT=5000                            # Server port
```

### Command Line Options

```bash
python apex_engine/main.py [OPTIONS]

Options:
  --demo, -d          Run demonstration mode
  --interactive, -i   Start interactive prompt mode
  --analyze FILE      Analyze lyrics from a file
  --prompt "TEXT"     Run single generation with prompt
  --quiet, -q         Suppress banner output
  --help, -h          Show help message
```

---

## Project Architecture

### Directory Structure

```
apex-engine/
├── apex_engine/               # Main application package
│   ├── config/                # Configuration files
│   │   ├── genres.json        # Genre definitions
│   │   ├── sonauto_tags.json  # Tag taxonomy
│   │   ├── knowledge_base.py  # Documentation excerpts
│   │   └── ui_text_config.py  # Help text configuration
│   │
│   ├── src/                   # Source code
│   │   ├── agents/            # Analysis agents
│   │   │   ├── lyrical/       # Bars, Flow, Vowel analyzers
│   │   │   ├── cultural/      # Meme analyzer
│   │   │   └── audio/         # Spectral analysis
│   │   │
│   │   ├── core/              # Core functionality
│   │   │   ├── llm_client.py  # OpenAI integration
│   │   │   ├── orchestrator.py # Workflow management
│   │   │   ├── predictor.py   # Virality prediction
│   │   │   └── project_manager.py # Project CRUD
│   │   │
│   │   └── utils/             # Utilities
│   │
│   ├── web/                   # Flask web application
│   │   ├── app.py             # Main Flask app
│   │   ├── templates/         # Jinja2 HTML templates
│   │   └── static/            # CSS, JS, assets
│   │
│   ├── projects/              # Saved song projects
│   └── main.py                # CLI entry point
│
├── requirements.txt           # Python dependencies
├── .env.example               # Environment template
├── run.sh                     # Linux/Mac startup script
├── run.bat                    # Windows startup script
└── README.md                  # Quick start guide
```

### Agent Architecture

APEX Engine uses a hierarchical multi-agent system:

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR                              │
│  (Manages workflow: Plan → Generate → Analyze → Iterate)    │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ LYRICAL       │    │ AUDIO         │    │ CULTURAL      │
│ AGENTS        │    │ AGENTS        │    │ AGENTS        │
├───────────────┤    ├───────────────┤    ├───────────────┤
│ BarsAnalyzer  │    │ FlowSupervisor│    │ MemeAnalyzer  │
│ FlowAnalyzer  │    │ SpectralAgent │    │ TrendAnalyzer │
│ VowelAnalyzer │    │ FrissonDetect │    └───────────────┘
└───────────────┘    └───────────────┘
```

### Key Algorithms

| Algorithm | Purpose | Key Metrics |
|-----------|---------|-------------|
| **Raplyzer Protocol** | Phonetic analysis | Rhyme Factor, Multis, Assonance |
| **Flow Analysis** | Rhythmic consistency | PDI, Syllable Velocity, Consistency |
| **Vowel Analysis** | Sound patterns | Entropy, Earworm Score, Euphony |
| **Frisson Detection** | Emotional impact | Dynamic Surge, Spectral Expansion |
| **Syncopation Index** | Groove quality | Target: 15-30 (Goldilocks Zone) |

---

## Feature Reference

### Web UI Features

#### Seed Composition
Five-component input system for song configuration:

1. **Prompt/Description** - Production texture, instrumentation, atmosphere
2. **Lyrics** - Song structure with [Verse], [Chorus] tags
3. **Neuropsychological Effects** - Frisson triggers, tension/release
4. **Neurochemical Effects** - Syncopation, groove, dopamine optimization
5. **Musical Effects** - Balance/prompt strength, tag ordering

#### Tools Panel
- **Rhyme Analysis** - BarsAnalyzer metrics
- **Flow Analysis** - Rhythmic consistency scoring
- **Quotability** - MemeAnalyzer for viral potential
- **Trend Analysis** - Cultural relevance scoring
- **Full Analysis** - Run all agents with comprehensive logging

#### Song Health Dashboard
- Visual progress bars for key metrics
- Color-coded scores (green/yellow/red)
- Tier badges: Gold, Platinum, Diamond, Viral

#### Per-Field AI Optimization
Each input field has an "AI" button that:
- Pulls current agent analysis as context
- Injects relevant knowledge base documentation
- Provides targeted improvements for that specific field

#### Help System
- "?" buttons on each field for comprehensive help
- Tag Explorer for browsing Sonauto taxonomy
- Examples and best practices from documentation

### CLI Features

```bash
# Interactive mode - continuous prompt/response
python apex_engine/main.py --interactive

# Demo mode - showcase engine capabilities
python apex_engine/main.py --demo

# Analyze existing lyrics file
python apex_engine/main.py --analyze lyrics.txt

# Single prompt generation
python apex_engine/main.py --prompt "aggressive trap 140bpm"
```

---

## Troubleshooting

### Common Issues

#### "ModuleNotFoundError: No module named 'flask'"

**Cause**: Dependencies not installed or virtual environment not activated.

**Solution**:
```bash
# Make sure venv is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

#### "Error: Python not found"

**Cause**: Python not in system PATH.

**Solution**:
- Windows: Reinstall Python with "Add to PATH" checked
- Mac/Linux: Use `python3` instead of `python`

#### "Connection refused" or "Address already in use"

**Cause**: Port 5000 is already in use.

**Solution**:
```bash
# Use a different port
PORT=5001 ./run.sh
# OR
set PORT=5001 && run.bat
```

#### API Errors: "Invalid API key"

**Cause**: Incorrect or missing API key.

**Solution**:
1. Verify key in `.env` file has no extra spaces
2. Check the key is valid at the provider's dashboard
3. Ensure you have credits/billing set up

#### "librosa" Installation Fails

**Cause**: Missing system dependencies.

**Solution**:
```bash
# Ubuntu/Debian
sudo apt install libsndfile1 ffmpeg

# macOS
brew install libsndfile ffmpeg

# Windows - usually works out of the box
# If not, install Visual C++ Build Tools
```

#### Page shows blank or doesn't load

**Cause**: JavaScript errors or caching issues.

**Solution**:
1. Open browser developer tools (F12)
2. Check Console tab for errors
3. Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
4. Clear browser cache if needed

### Simulation Mode

If you see "Simulation Mode Active", API keys are not configured:

- **Lyric generation**: Uses template-based simulation
- **Audio generation**: Disabled (button won't function)
- **All other features**: Work normally

This is useful for:
- Development and testing
- Exploring the UI without API costs
- Offline usage

### Getting Help

1. Check this troubleshooting section first
2. Review the console output for specific error messages
3. Check logs in the terminal where the app is running
4. For API issues, check the respective provider's status page

---

## Development Guide

### Running in Development Mode

```bash
# Enable debug mode for auto-reload
export FLASK_DEBUG=1  # Linux/Mac
set FLASK_DEBUG=1     # Windows

cd apex_engine
python -m web.app
```

### Running Tests

```bash
pytest apex_engine/tests/
```

### Project Structure for Modifications

- **Add new agents**: Create in `apex_engine/src/agents/`
- **Modify UI**: Edit templates in `apex_engine/web/templates/`
- **Add API endpoints**: Modify `apex_engine/web/app.py`
- **Adjust analysis**: Edit agent classes in respective folders

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests to ensure nothing is broken
5. Submit a pull request

---

## Appendix

### Supported Genres

| Genre | BPM Range | Characteristics |
|-------|-----------|-----------------|
| Trap | 130-160 | Fast hi-hats, heavy 808s, dark melodies |
| Boom Bap | 85-100 | Swing drums, jazz samples, vinyl warmth |
| Drill | 140-150 | Sliding 808s, minimal production |
| Phonk | 120-140 | Distorted bass, cowbells, Memphis style |
| Lo-Fi Hip Hop | 70-90 | Relaxed, nostalgic, vinyl crackle |
| Pop Rap | 100-130 | Melodic, radio-friendly |

### Metric Thresholds

| Metric | Poor | Average | Good | Excellent |
|--------|------|---------|------|-----------|
| Rhyme Factor | <0.3 | 0.3-0.5 | 0.5-0.7 | >0.7 |
| Flow Consistency | <0.5 | 0.5-0.7 | 0.7-0.85 | >0.85 |
| Syncopation Index | <10 | 10-15 | 15-25 | 25-35 |
| Earworm Score | <0.4 | 0.4-0.6 | 0.6-0.8 | >0.8 |
| PVS (Virality) | <40 | 40-60 | 60-80 | >80 |

### Sonauto Parameter Reference

| Parameter | Range | Description |
|-----------|-------|-------------|
| `prompt_strength` | 1.5-4.0 | CFG scale. Higher = more aggressive |
| `balance_strength` | 0.0-1.0 | Vocal/instrumental mix. 0.7 recommended |
| `duration` | 30-180s | Output audio length |
| `output_format` | wav/mp3 | Use WAV for analysis accuracy |

---

*Last updated: December 2025*
