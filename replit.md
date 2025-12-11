# APEX Engine

## Overview
APEX Engine (Autonomous Aural Architectures) is a sophisticated multi-agent framework for algorithmic rap composition using the Sonauto API. The system employs LangGraph-style orchestration to coordinate specialized AI agents that generate, analyze, and iteratively refine rap music.

The framework optimizes for:
- **Technical Metrics**: Rhyme density, flow complexity, syllable velocity
- **Psychoacoustic Responses**: Frisson (chills), syncopation, groove quality
- **Commercial Viability**: Earworm potential, quotability, trend alignment

## Project Structure
```
apex_engine/
├── config/               # Configuration files
│   ├── genre_definitions.json
│   ├── personas.json
│   └── weights.json
├── data/                 # Data directories
│   ├── processing/
│   ├── raw_input/
│   ├── stems/
│   └── suno_downloads/
├── src/
│   ├── agents/           # Hierarchical Agent System
│   │   ├── agent_base.py # Abstract base classes
│   │   ├── audio/        # Audio DSP agents
│   │   │   ├── flow_supervisor.py    # Beat tracking & onset alignment
│   │   │   ├── agent_frisson.py      # Psychoacoustic chills detection
│   │   │   ├── agent_groove.py       # Micro-timing & swing analysis
│   │   │   ├── agent_spectral.py     # Frequency masking & clarity
│   │   │   ├── agent_timbre.py       # Vocal texture classification
│   │   │   └── agent_split.py        # Stem separation
│   │   ├── cultural/     # Cultural analysis agents
│   │   │   ├── agent_meme.py         # Quotability scoring
│   │   │   └── agent_trend.py        # Trend alignment analysis
│   │   └── lyrical/      # Text & phonetics agents
│   │       ├── lyrical_architect.py  # Main lyric generation
│   │       ├── agent_bars.py         # Rhyme density (Raplyzer)
│   │       ├── agent_flow.py         # Syllabic velocity
│   │       ├── agent_vowel.py        # Assonance & earworm detection
│   │       └── agent_context.py      # Narrative coherence
│   ├── core/             # Orchestration & State Management
│   │   ├── state_schema.py           # RapGenerationState TypedDict
│   │   ├── orchestrator.py           # LangGraph-style workflow
│   │   ├── suno_interface.py         # Sonauto API client
│   │   ├── mix_engineer.py           # Post-processing & mastering
│   │   ├── feedback_logic.py         # Iterative refinement
│   │   └── predictor.py              # Virality prediction (PVS)
│   └── utils/            # Shared utilities
│       ├── logger.py                 # Hierarchical logging
│       ├── audio_tools.py            # Librosa wrappers
│       ├── api_client.py             # HTTP client utilities
│       └── report_generator.py       # Analysis reports
├── tests/                # Test suite
├── main.py               # CLI entry point
└── requirements.txt      # Dependencies
```

## Key Components

### Agent Hierarchy
1. **Lyrical Architect** - Structure-first lyric generation with phonetic validation
2. **Sonauto Operator** - API interface with "Black Magic" tag optimization
3. **Flow Supervisor** - Audio quality auditor with beat tracking
4. **Mix Engineer** - Reference-based mastering and loudness normalization
5. **Frisson Detector** - Psychoacoustic analysis for emotional impact
6. **Cultural Analysts** - Trend alignment and meme potential scoring

### Core Workflow (LangGraph Pattern)
```
PLAN → LYRICAL_ARCHITECT → SONAUTO_GENERATE → FLOW_SUPERVISOR
                                                    ↓
                                    [Quality Check] → INPAINT (loop) OR
                                                    ↓
                                             MIX_ENGINEER → COMPLETE
```

### Key Algorithms
- **Raplyzer Protocol**: Phonetic rhyme density using CMU Pronouncing Dictionary patterns
- **Longuet-Higgins Model**: Syncopation index calculation (optimal range: 15-30)
- **Frisson Index**: Composite score from dynamic surge, spectral brightness, surprise events
- **PVS (Predicted Virality Score)**: Multi-factor engagement prediction

## Running the Project

### Basic Usage
```bash
python apex_engine/main.py           # Show help and environment check
python apex_engine/main.py --demo    # Run demonstration
python apex_engine/main.py -i        # Interactive prompt mode
```

### With Prompt
```bash
python apex_engine/main.py --prompt "Create aggressive trap at 140 BPM"
```

### Analyze Existing Lyrics
```bash
python apex_engine/main.py --analyze lyrics.txt
```

## Configuration

### Environment Variables
- `SONAUTO_API_KEY` - Sonauto API key for audio generation
- `OPENAI_API_KEY` - OpenAI key for LLM-based lyric generation

Without API keys, the system runs in simulation mode for development.

### Optional Dependencies
For full audio analysis capabilities:
- `librosa` - Audio DSP (beat tracking, spectral analysis)
- `numpy` - Numerical operations
- `soundfile` - Audio file I/O

## Testing

### Run Tests
```bash
python apex_engine/tests/test_master.py    # Integration tests (12 tests)
python apex_engine/tests/test_lyrical.py   # Lyrical analysis tests (13 tests)
```

### Test Coverage
- **Workflow Integration**: Orchestrator creation, simulation mode, iteration limits
- **PVS Calculation**: Formula accuracy, tier assignment, recommendations
- **State Management**: Initial state creation, validation
- **Agent Base**: Success/failure result patterns
- **Lyrical Analysis**: Rhyme detection, syllable counting, flow consistency

## Recent Changes
- December 2025: Complete framework implementation
  - Implemented full agent hierarchy (15+ specialized agents)
  - Built LangGraph-style orchestrator with conditional routing
  - Added Raplyzer protocol for phonetic analysis
  - Implemented frisson detection and virality prediction
  - Created comprehensive CLI with demo/interactive modes
  - Added simulation mode for development without API keys
  - Created comprehensive test suite (25 unit/integration tests)

## Architecture Notes
- **State Management**: TypedDict-based RapGenerationState for type-safe agent communication
- **Error Handling**: AgentResult pattern with standardized success/failure returns
- **Iteration Limits**: Configurable max_iterations and credits_budget to prevent runaway loops
- **Graceful Degradation**: Simulated responses when optional libraries unavailable

## User Preferences
- Framework targets rap/hip-hop specifically due to genre's unique requirements
- Designed for iterative refinement: lyrics → audio → analysis → inpainting → mastering
- Uses Sonauto API (not Suno) - latent diffusion with inpainting capabilities
