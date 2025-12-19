# APEX Engine - Architecture

## Part A: File Tree

```
apex_engine/
├── __init__.py
├── main.py                          # CLI entry point
├── requirements.txt                 # Python dependencies
│
├── config/                          # Configuration files
│   ├── __init__.py
│   ├── frisson_triggers.json        # Psychoacoustic trigger patterns
│   ├── genres.json                  # Genre definitions
│   ├── knowledge_base.py            # Comprehensive music production knowledge
│   ├── personas.json                # AI persona configurations
│   ├── sonauto_tags.json            # Validated API tags
│   ├── suno_constants.py            # Legacy Suno constants
│   ├── ui_text_config.py            # UI help text and tooltips
│   └── weights.json                 # Metric weighting
│
├── context/                         # AI prompt context files
│   ├── lyrics_validator.md          # Lyrics validation rules
│   ├── neurochemical_translator.md  # Neuro effects translation
│   ├── payload_system.md            # Payload construction rules
│   └── prompt_analyzer.md           # Style prompt validation
│
├── data/                            # Data directories (mostly empty)
│   ├── __init__.py
│   ├── processing/
│   ├── raw_input/
│   ├── stems/
│   └── suno_downloads/
│
├── output/                          # Generated audio files
│   └── mastered/                    # Post-mastering output
│
├── projects/                        # Song project directories
│   └── <project_id>/
│       ├── config.json
│       ├── seed.txt
│       ├── iterations/
│       ├── approved/
│       └── output/
│
├── src/                             # Source code
│   ├── __init__.py
│   │
│   ├── agents/                      # AI agents
│   │   ├── __init__.py
│   │   ├── agent_base.py            # Base agent class
│   │   │
│   │   ├── lyrical/                 # Text analysis agents
│   │   │   ├── __init__.py
│   │   │   ├── agent_bars.py        # Rhyme/phonetic analysis
│   │   │   ├── agent_context.py     # Narrative consistency
│   │   │   ├── agent_flow.py        # Syllable flow analysis
│   │   │   ├── agent_vowel.py       # Vowel/assonance analysis
│   │   │   └── lyrical_architect.py # Lyric generation
│   │   │
│   │   ├── audio/                   # Audio analysis agents
│   │   │   ├── __init__.py
│   │   │   ├── agent_frisson.py     # Emotional impact
│   │   │   ├── agent_groove.py      # Groove/timing
│   │   │   ├── agent_spectral.py    # Frequency analysis
│   │   │   ├── agent_split.py       # Stem separation
│   │   │   ├── agent_timbre.py      # Vocal texture
│   │   │   └── flow_supervisor.py   # Beat tracking
│   │   │
│   │   └── cultural/                # Market analysis agents
│   │       ├── __init__.py
│   │       ├── agent_meme.py        # Quotability
│   │       └── agent_trend.py       # Trend alignment
│   │
│   ├── core/                        # Core business logic
│   │   ├── __init__.py
│   │   ├── fal_models.py            # Pydantic models for Fal.ai
│   │   ├── feedback_logic.py        # Iterative refinement
│   │   ├── llm_client.py            # OpenAI integration
│   │   ├── mix_engineer.py          # Audio mastering
│   │   ├── orchestrator.py          # Workflow state machine
│   │   ├── predictor.py             # Virality prediction
│   │   ├── project_manager.py       # Project CRUD
│   │   ├── state_schema.py          # TypedDict state definition
│   │   └── suno_interface.py        # Sonauto API client
│   │
│   ├── services/                    # External service integrations
│   │   ├── __init__.py
│   │   ├── fal_client.py            # Fal.ai MiniMax client
│   │   ├── optimizer.py             # Field optimization
│   │   ├── payload_factory.py       # Payload construction
│   │   └── validators.py            # Input validation
│   │
│   └── utils/                       # Utilities
│       ├── __init__.py
│       ├── api_client.py            # API client base classes
│       ├── audio_tools.py           # Audio processing helpers
│       ├── logger.py                # Logging configuration
│       └── report_generator.py      # Report generation
│
├── tests/                           # Test suite
│   ├── __init__.py
│   ├── test_fal_models.py
│   ├── test_harness_synth.py
│   ├── test_lyrical.py
│   └── test_master.py
│
└── web/                             # Flask web application
    ├── app.py                       # Main Flask app (~1000 lines)
    ├── static/
    │   └── css/
    │       └── style.css            # UI styling
    └── templates/
        ├── error.html
        ├── index.html               # Project dashboard
        ├── new_project.html         # Project creation form
        └── workspace.html           # Main editing workspace
```

---

## Part B: Detailed Component Analysis

### B1. Small Files (<200 lines)

#### `apex_engine/main.py`
- **Purpose:** CLI entry point for running APEX Engine outside web UI
- **Dependencies:** `orchestrator`, `project_manager`, `llm_client`, `suno_interface`
- **Dependents:** None (entry point)

#### `apex_engine/src/agents/agent_base.py`
- **Purpose:** Abstract base class `GenerativeAgent` defining the agent interface
- **Dependencies:** `typing`, `dataclasses`
- **Dependents:** All agent implementations inherit from this

#### `apex_engine/src/core/state_schema.py`
- **Purpose:** TypedDict definitions for `RapGenerationState` and sub-schemas
- **Dependencies:** `typing`, `typing_extensions`
- **Dependents:** `orchestrator`, all agents, `project_manager`

#### `apex_engine/src/core/predictor.py`
- **Purpose:** `ViralityPredictor` calculates PVS (Predicted Virality Score)
- **Dependencies:** `state_schema`, `dataclasses`
- **Dependents:** `orchestrator`, `feedback_logic`

#### `apex_engine/src/core/feedback_logic.py`
- **Purpose:** `FeedbackController` manages iterative refinement loops
- **Dependencies:** `state_schema`, `predictor`
- **Dependents:** `orchestrator`

#### `apex_engine/src/services/validators.py`
- **Purpose:** Input validation for Double Hash and Breath protocols
- **Dependencies:** `re`, `typing`
- **Dependents:** `payload_factory`, `app.py`

#### `apex_engine/src/utils/logger.py`
- **Purpose:** Structured logging with color-coded output and trace IDs
- **Dependencies:** `logging`, `colorama`
- **Dependents:** All modules use `get_logger()`

#### `apex_engine/src/utils/report_generator.py`
- **Purpose:** Generate analysis reports from agent results
- **Dependencies:** `state_schema`, `json`
- **Dependents:** `orchestrator`, `app.py`

### B2. Large Files (>200 lines) - Breakdown

---

#### `apex_engine/web/app.py` (~1007 lines)

**Top 5 Key Functions/Classes:**

| Function/Class | Lines | Role |
|----------------|-------|------|
| `api_generate_audio()` | 383-430 | Generates music via Fal.ai. Validates approval, constructs payload, polls for result. Critical revenue path. |
| `api_analyze_song()` | 200-280 | Runs all lyrical agents (Bars, Flow, Vowel, Meme) and aggregates metrics. Returns comprehensive analysis JSON. |
| `api_magic_fill()` | 433-463 | GPT-4o powered auto-population of form fields from concept/theme. High OpenAI API usage. |
| `api_optimize_field()` | 574-602 | Per-field AI optimization using `FieldOptimizer`. Returns optimized text with reasoning. |
| `workspace()` | 150-180 | Loads project and renders main editing template. Passes all config data to frontend. |

---

#### `apex_engine/src/core/llm_client.py` (~400 lines)

**Top 5 Key Functions/Classes:**

| Function/Class | Lines | Role |
|----------------|-------|------|
| `LLMClient.__init__()` | 125-145 | Initializes OpenAI client with Replit AI integration support. Checks for API keys. |
| `generate_lyrics()` | 260-320 | Generates rap lyrics using GPT-4o with comprehensive system prompt. |
| `iterate_lyrics()` | 320-380 | Improves existing lyrics based on agent feedback scores. |
| `magic_fill()` | 380-420 | Auto-populates all form fields from partial inputs. |
| `_get_knowledge_context()` | 163-264 | Loads field-specific context from knowledge base for AI prompts. |

---

#### `apex_engine/config/knowledge_base.py` (~640 lines)

**Top 5 Key Data Structures:**

| Constant | Lines | Role |
|----------|-------|------|
| `SONAUTO_TAG_TAXONOMY` | 14-64 | Complete taxonomy of validated Sonauto tags by category |
| `PROMPT_ENGINEERING` | 65-145 | Best practices for style prompt construction |
| `LYRICS_STRUCTURE` | 146-203 | Structural tags, syllable guidelines, formatting rules |
| `RAPLYZER_PROTOCOL` | 374-412 | Rhyme factor calculation, phonetic analysis specs |
| `MEME_QUOTABILITY` | 454-501 | Quotability scoring criteria, punchline detection |

---

#### `apex_engine/src/core/suno_interface.py` (~350 lines)

**Top 5 Key Functions/Classes:**

| Function/Class | Lines | Role |
|----------------|-------|------|
| `SonautoOperator.__init__()` | 60-90 | Initializes Sonauto API client with authentication |
| `generate()` | 100-160 | Submits generation request to Sonauto API |
| `inpaint()` | 160-220 | Surgical audio fixes via inpainting endpoint |
| `extend()` | 220-280 | Extends existing audio track |
| `_poll_for_completion()` | 280-330 | Polls API with exponential backoff for async results |

---

#### `apex_engine/src/services/fal_client.py` (~294 lines)

**Top 5 Key Functions/Classes:**

| Function/Class | Lines | Role |
|----------------|-------|------|
| `FalMusicClient.__init__()` | 43-56 | Initializes with API key, sets simulation mode if missing |
| `submit_generation()` | 66-111 | Submits generation to Fal.ai queue, returns request_id |
| `poll_status()` | 113-180 | Polls with exponential backoff (2-10s delay) |
| `get_result()` | 180-220 | Retrieves completed generation result |
| `generate_music()` | 220-280 | Full generation flow: submit → poll → get result |

---

#### `apex_engine/src/agents/lyrical/agent_flow.py` (~280 lines)

**Top 5 Key Functions/Classes:**

| Function/Class | Lines | Role |
|----------------|-------|------|
| `FlowAnalyzer.analyze()` | 60-100 | Main entry point, runs all flow metrics |
| `_calculate_syllable_velocity()` | 100-140 | Syllables per beat calculation |
| `_calculate_pdi()` | 140-180 | Plosive Density Index for percussive feel |
| `_detect_breath_markers()` | 180-220 | Finds natural pause points in lyrics |
| `_analyze_stress_patterns()` | 220-260 | Stress pattern analysis for rhythmic consistency |

---

## Part C: Dependency Graph

### C1. System Binaries Required

| Python Package | System Requirement | Notes |
|----------------|-------------------|-------|
| `librosa` | FFmpeg | Required for audio format conversion and some DSP operations |
| `soundfile` | libsndfile | Audio file I/O |
| `matchering` | FFmpeg | Reference-based mastering requires audio processing |
| `pydub` | FFmpeg | Audio format conversion |

**Installation Command:**
```bash
# Debian/Ubuntu
apt-get install ffmpeg libsndfile1

# macOS
brew install ffmpeg libsndfile

# Nix (Replit)
# Already available in the Nix environment
```

### C2. Python Package Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `pronouncing` | >=0.2.0 | CMU Pronouncing Dictionary for phonetic analysis |
| `syllables` | >=1.0.0 | Syllable counting for flow analysis |
| `librosa` | >=0.10.1 | Beat tracking, spectral analysis, onset detection |
| `numpy` | >=1.24.0 | Numerical operations |
| `soundfile` | >=0.12.0 | Audio file I/O |
| `pydub` | >=0.25.0 | Audio format conversion |
| `matchering` | >=2.0.6 | Reference-based automated mastering |
| `requests` | >=2.28.0 | HTTP client for API calls |
| `tenacity` | >=8.2.0 | Retry logic with exponential backoff |
| `colorama` | >=0.4.6 | Terminal colors for CLI |
| `python-dotenv` | >=1.0.0 | Environment variable management |
| `flask` | (implicit) | Web framework (not in requirements.txt but used) |
| `openai` | (implicit) | OpenAI API client |
| `pydantic` | (implicit) | API payload validation |

### C3. Optional Dependencies

| Package | Purpose |
|---------|---------|
| `langchain` | LLM orchestration (commented out) |
| `langchain-openai` | OpenAI integration for LangChain |
| `langgraph` | Graph-based agent orchestration |
| `demucs` | Audio source separation |
| `pytest` | Testing framework |

---

## Part D: Global Constants (Tunables)

### D1. API Configuration

| Constant | File | Default | Description |
|----------|------|---------|-------------|
| `FAL_API_BASE` | `services/fal_client.py` | `"https://queue.fal.run"` | Fal.ai API base URL |
| `FAL_MODEL` | `services/fal_client.py` | `"fal-ai/minimax-music/v2"` | Model identifier |
| `SONAUTO_API_BASE` | `core/suno_interface.py` | `"https://api.sonauto.ai/v1"` | Sonauto API base URL |
| `SONAUTO_API_AVAILABLE` | `core/suno_interface.py` | `True` | API availability flag |

### D2. Cost Configuration

| Constant | File | Default | Description |
|----------|------|---------|-------------|
| `COST_PER_GENERATION_USD` | `core/fal_models.py` | `0.075` | Cost per audio generation |
| `COST_PER_INPAINT_USD` | `core/fal_models.py` | `0.075` | Cost per inpainting operation |
| `COST_PER_EXTEND_USD` | `core/fal_models.py` | `0.075` | Cost per track extension |

### D3. Lyrical Analysis Constants

| Constant | File | Default | Description |
|----------|------|---------|-------------|
| `VOWEL_PHONEMES` | `agents/lyrical/agent_bars.py` | Set of 15 phonemes | Valid vowel sounds for rhyme detection |
| `GENRE_SYLLABLE_CONSTRAINTS` | `agents/lyrical/agent_flow.py` | Dict by genre | Target syllables per bar by genre |
| `MAX_PHRASE_SYLLABLES` | `agents/lyrical/agent_flow.py` | `16` | Maximum syllables before breath marker |
| `BREATH_TOKEN` | `agents/lyrical/agent_flow.py` | `'(breath)'` | Breath marker token |
| `PLOSIVE_CONSONANTS` | `agents/lyrical/agent_flow.py` | `set('bpdtgk')` | Consonants for PDI calculation |
| `FRICATIVE_CONSONANTS` | `agents/lyrical/agent_flow.py` | `set('fvszh')` | Fricative consonants |
| `NASAL_CONSONANTS` | `agents/lyrical/agent_flow.py` | `set('mn')` | Nasal consonants |

### D4. Audio Analysis Constants

| Constant | File | Default | Description |
|----------|------|---------|-------------|
| `METRIC_WEIGHTS_16TH` | `agents/audio/flow_supervisor.py` | Array of 16 weights | Beat position emphasis weights |

### D5. Validation Constants

| Constant | File | Description |
|----------|------|-------------|
| `INSTRUMENTAL_TOKENS` | `services/validators.py` | Valid instrumental section markers |
| `KEEP_BRACKET_TAGS` | `services/validators.py` | Tags that should use `[]` format |
| `TAG_STANDARDIZATION` | `services/validators.py` | Map of variant tags to standard format |
| `TECHNICAL_PATTERNS` | `services/validators.py` | Regex patterns for technical metadata |

### D6. UI/UX Configuration

| Constant | File | Description |
|----------|------|-------------|
| `FIELD_HELP` | `config/ui_text_config.py` | Tooltip text for all form fields |
| `AGENT_DESCRIPTIONS` | `config/ui_text_config.py` | Human-readable agent descriptions |
| `CONSOLE_MESSAGES` | `config/ui_text_config.py` | Pre-defined console log messages |
| `MAGIC_FILL_PROMPT` | `config/ui_text_config.py` | System prompt for Magic Fill feature |

### D7. Project Management

| Constant | File | Default | Description |
|----------|------|---------|-------------|
| `PROJECTS_DIR` | `core/project_manager.py` | `Path("projects")` | Base directory for project storage |

### D8. Genre Defaults

| Constant | File | Description |
|----------|------|-------------|
| `GENRE_CFG_DEFAULTS` | `core/fal_models.py` | Default CFG scale by genre (trap: 2.5, boom_bap: 1.8, etc.) |
