# APEX Engine

## Overview
APEX Engine (Autonomous Aural Architectures) is a sophisticated multi-agent framework for algorithmic rap composition using the Sonauto API via fal.ai endpoints. The system employs LangGraph-style orchestration to coordinate specialized AI agents that generate, analyze, and iteratively refine rap music.

The framework optimizes for:
- **Technical Metrics**: Rhyme density, flow complexity, syllable velocity
- **Psychoacoustic Responses**: Frisson (chills), syncopation, groove quality
- **Commercial Viability**: Earworm potential, quotability, trend alignment

## Project Structure
```
apex_engine/
├── config/               # Configuration files
│   ├── genres.json               # Genre-specific parameters (BPM, CFG scale, etc.)
│   ├── sonauto_tags.json         # Validated Tag Explorer taxonomy (200+ tags)
│   ├── personas.json             # Artist persona configurations
│   ├── weights.json              # Metric weighting configurations
│   └── frisson_triggers.json     # Psychoacoustic trigger patterns
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
│   │   ├── suno_interface.py         # Fal.ai Sonauto API client
│   │   ├── fal_models.py             # Pydantic validation models
│   │   ├── mix_engineer.py           # Post-processing & mastering
│   │   ├── feedback_logic.py         # Iterative refinement
│   │   └── predictor.py              # Virality prediction (PVS)
│   └── utils/            # Shared utilities
│       ├── logger.py                 # Hierarchical logging
│       ├── audio_tools.py            # Librosa wrappers
│       ├── api_client.py             # HTTP client utilities
│       └── report_generator.py       # Analysis reports
├── tests/                # Test suite
├── web/                  # Flask Web UI
│   ├── app.py                    # Flask application
│   ├── templates/                # Jinja2 templates
│   │   ├── index.html            # Project list
│   │   ├── new_project.html      # Project creation form
│   │   ├── workspace.html        # Main editing workspace
│   │   └── error.html            # Error page
│   └── static/css/style.css      # Styling
├── main.py               # CLI entry point
└── requirements.txt      # Dependencies

projects/                 # Song project directories (created at runtime)
└── <project-id>/
    ├── config.json               # Project settings
    ├── seed.txt                  # Creative brief
    ├── iterations/               # Versioned lyrics with scoring
    │   └── v1/, v2/, v3/...
    ├── approved/                 # Final approved lyrics + API payload
    └── output/                   # Generated audio files
```

## Key Components

### Agent Hierarchy
1. **Lyrical Architect** - Structure-first lyric generation with phonetic validation
2. **Sonauto Operator** - Fal.ai API interface with CFG scale control (prompt_strength)
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

## Sonauto/Fal.ai API Integration

### Endpoint Architecture
- **Base URL**: `https://fal.run/fal-ai/sonauto/v2`
- **Queue URL**: `https://queue.fal.run/fal-ai/sonauto/v2` (async with webhooks)
- **Authentication**: `Key <FAL_KEY>` header format (NOT Bearer token)

### Endpoints
| Endpoint | Purpose |
|----------|---------|
| `/text-to-music` | Primary generation from prompt + lyrics |
| `/inpaint` | Surgical section regeneration |
| `/extend` | Track extension (left/right with crop_duration) |

### Key Parameters

#### prompt_strength (CFG Scale 0-5)
Controls adherence to prompt vs model creativity:
- **1.5-2.0**: Natural genres (pop rap, melodic, acoustic, jazz rap)
- **2.0-2.5**: Balanced genres (trap, hip hop, boom bap, conscious rap)
- **2.5-4.0**: Aggressive genres (phonk, drill, industrial) - artifacts become aesthetic

#### balance_strength (0.0-1.0)
Mix between instrumental (0.0) and vocals (1.0). Default: 0.7

#### output_format
- **WAV**: Required for stem analysis (no spectral artifacts)
- **MP3/OGG**: For web playback only

#### Inpainting Sections Format
```json
{
  "sections": [[10.5, 15.0], [30.0, 35.5]]  // [[start, end]] nested arrays
}
```
**Critical**: Use nested array format `[[start, end]]`, NOT object format `[{start, end}]`

### Cost Model (USD)
| Operation | Cost |
|-----------|------|
| Generation | $0.075 |
| Inpainting | $0.075 |
| Extension | $0.075 |

### Tag System
Tags validated against `config/sonauto_tags.json` (200+ verified tags from Tag Explorer).
Tag order matters - anchor genre first, then subgenre, mood, era, production.

### Pydantic Models
Located in `apex_engine/src/core/fal_models.py`:
- `SonautoGenerationRequest` - Full generation validation
- `SonautoInpaintRequest` - Inpainting with section validation
- `SonautoExtendRequest` - Extension with side/crop_duration

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
- `FAL_KEY` - Fal.ai API key for Sonauto audio generation (preferred)
- `SONAUTO_API_KEY` - Alternative name for FAL_KEY (legacy compatibility)
- `OPENAI_API_KEY` - OpenAI key for LLM-based lyric generation

Without API keys, the system runs in simulation mode for development.

### Cost Budget Configuration
State schema supports both legacy credits and USD cost tracking:
```python
state = create_initial_state(
    user_prompt="...",
    cost_budget_usd=5.0,    # Maximum USD spend per session
    max_iterations=3         # Maximum refinement loops
)
```

### Optional Dependencies
For full audio analysis capabilities:
- `librosa` - Audio DSP (beat tracking, spectral analysis)
- `numpy` - Numerical operations
- `soundfile` - Audio file I/O
- `pydantic` - API payload validation

## Testing

### Run Tests
```bash
cd apex_engine && python -m pytest tests/test_fal_models.py tests/test_master.py tests/test_lyrical.py -v
```

### Test Coverage (55 tests)
- **Pydantic Models (30 tests)**: Tag validation, payload format, cost estimation, section format
- **Workflow Integration**: Orchestrator creation, simulation mode, iteration limits
- **PVS Calculation**: Formula accuracy, tier assignment, recommendations
- **State Management**: Initial state creation, validation, USD cost tracking
- **Agent Base**: Success/failure result patterns
- **Lyrical Analysis**: Rhyme detection, syllable counting, flow consistency

## Recent Changes

### December 11, 2025: Flask Web UI & Project Management
- Added Flask web application for project-based song creation workflow
- Created ProjectManager class for file-based project organization
- Implemented GPT-4o client wrapper (LLMClient) for lyric generation and iteration
- Built project workspace UI with:
  - Creative brief/seed input
  - GPT-4o lyric generation and iteration
  - Scoring dashboard (rhyme density, flow consistency, PVS)
  - Recommendations for improvement
  - API payload preview before generation
  - Explicit approval gate before Sonauto calls
- Projects stored in `projects/<project-id>/` with versioned iterations
- Fixed main.py to recognize FAL_KEY as valid Sonauto API key

### December 11, 2025: fal_client SDK Migration
- **MAJOR**: Migrated from raw HTTP requests to official `fal_client` SDK
- Uses `fal_client.subscribe()` for sync polling, `fal_client.subscribe_async()` for async
- Uses `fal_client.submit_async()` for webhook-based async pattern
- Fixed O(n²) tag validation bug - now uses O(1) cached frozenset lookup
- Added `SonautoModel` enum with canonical endpoints (TEXT_TO_MUSIC, INPAINT, EXTEND)
- Inpaint sections format uses `{"start": x, "end": y}` objects for fal_client SDK
- Genre CFG defaults now support both formats: 'boom_bap' AND 'boom bap'
- Added cost estimation methods: `estimate_cost()` on all Pydantic request models
- Fixed simulated generation to write proper binary WAV files (not text with .wav extension)
- Added 30 new unit tests for Pydantic models (55 total tests, all passing)
- Removed unused imports (wait_chain, wait_fixed)
- Added async support: `_call_fal_async()` for production webhook pattern

### December 11, 2025: Neo-Apex API Refactoring (Phase 1)
- **BREAKING**: Migrated from api.sonauto.ai/v1 to fal.ai/models/sonauto/v2 endpoints
- **BREAKING**: Authentication changed from Bearer token to `Key <FAL_KEY>` format
- Added Pydantic models for rigorous payload validation (fal_models.py)
- Implemented prompt_strength (CFG scale) with genre-based defaults
- Created sonauto_tags.json with 200+ validated Tag Explorer tags
- Removed deprecated BLACK_MAGIC_TAGS (autoregressive-model superstition)
- Updated cost tracking from credits to USD ($0.075/generation)
- Added state fields: cost_usd, cost_budget_usd, request_id, extend_request
- Added /extend endpoint support with side and crop_duration parameters
- Added HMAC webhook signature verification method
- Output format changed from OGG to WAV for stem analysis

### December 2025: Initial Framework
- Implemented full agent hierarchy (15+ specialized agents)
- Built LangGraph-style orchestrator with conditional routing
- Added Raplyzer protocol for phonetic analysis using CMU Dictionary
- Implemented frisson detection and virality prediction (PVS)
- Created comprehensive CLI with demo/interactive modes
- Added simulation mode for development without API keys
- Created comprehensive test suite (25 unit/integration tests)

## Architecture Notes
- **API Client**: Uses official `fal_client` SDK (not raw HTTP requests)
- **State Management**: TypedDict-based RapGenerationState for type-safe agent communication
- **Error Handling**: AgentResult pattern with standardized success/failure returns
- **Budget Enforcement**: Both legacy credits_budget and new cost_budget_usd supported
- **Graceful Degradation**: Simulated responses when optional libraries unavailable
- **Tag Validation**: O(1) lookup using cached frozenset at module load
- **Async Patterns**: 
  - Development: `fal_client.subscribe()` (blocking poll)
  - Production: `fal_client.submit_async()` with webhooks

## User Preferences
- Framework targets rap/hip-hop specifically due to genre's unique requirements
- Designed for iterative refinement: lyrics → audio → analysis → inpainting → mastering
- Uses Sonauto via fal.ai (latent diffusion with inpainting/extension capabilities)
- WAV format required for accurate spectral analysis (compressed formats cause artifacts)
