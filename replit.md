# APEX Engine

## Overview
APEX Engine is a music production and analysis engine built in Python. It features a modular agent-based architecture for audio, cultural, and lyrical analysis.

## Project Structure
```
apex_engine/
├── config/           # Configuration files (genres, personas, weights)
├── data/             # Data directories for processing
│   ├── processing/
│   ├── raw_input/
│   ├── stems/
│   └── suno_downloads/
├── src/
│   ├── agents/       # Analysis agents
│   │   ├── audio/    # Audio analysis (frisson, groove, spectral, etc.)
│   │   ├── cultural/ # Cultural analysis (meme, trend)
│   │   └── lyrical/  # Lyrical analysis (bars, context, flow, vowel)
│   ├── core/         # Core engine (orchestrator, predictor, feedback)
│   └── utils/        # Utilities (API client, audio tools, logger)
├── tests/            # Test suite
├── main.py           # CLI entry point
└── requirements.txt  # Dependencies
```

## Running the Project
```bash
python apex_engine/main.py
```

## Current State
The project is a skeleton structure with placeholder files. Core functionality needs to be implemented.

## Recent Changes
- December 2025: Initial Replit environment setup
  - Added Python 3.11 runtime
  - Created working main.py entry point
  - Added .gitignore for Python
