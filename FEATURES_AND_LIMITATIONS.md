# APEX Engine - Features and Limitations

## Section A: Features

### A1. Web UI & API Features

| Feature | File | Route/Function | Description |
|---------|------|----------------|-------------|
| Project Dashboard | `apex_engine/web/app.py` | `GET /` → `index()` | Lists all song projects with status badges (DRAFT/APPROVED) |
| Project Creation | `apex_engine/web/app.py` | `GET/POST /project/new` → `new_project()` | Create new song projects with genre, BPM, mood settings |
| Project Workspace | `apex_engine/web/app.py` | `GET /project/<id>` → `workspace()` | Main editing interface for seed composition |
| List Projects API | `apex_engine/web/app.py` | `GET /api/projects` → `api_list_projects()` | JSON list of all projects |
| Project CRUD API | `apex_engine/web/app.py` | `GET/PUT/DELETE /api/project/<id>` → `api_project()` | Read, update, delete project |
| Save Seed | `apex_engine/web/app.py` | `POST /api/project/<id>/seed` → `api_save_seed()` | Save seed composition text |
| Generate Lyrics | `apex_engine/web/app.py` | `POST /api/project/<id>/generate-lyrics` → `api_generate_lyrics()` | GPT-4o lyric generation from seed |
| Iterate Lyrics | `apex_engine/web/app.py` | `POST /api/project/<id>/iterate` → `api_iterate_lyrics()` | Improve lyrics based on agent feedback |
| Score Lyrics | `apex_engine/web/app.py` | `POST /api/project/<id>/score` → `api_score()` | Run lyrical agents and return metrics |
| Approve Lyrics | `apex_engine/web/app.py` | `POST /api/project/<id>/approve` → `api_approve()` | Mark lyrics as approved for generation |
| Preview Payload | `apex_engine/web/app.py` | `POST /api/project/<id>/preview-payload` → `api_preview_payload()` | Preview Fal.ai API payload before generation |
| Optimize Seed | `apex_engine/web/app.py` | `POST /api/optimize-seed` → `api_optimize_seed()` | Batch optimization of all seed fields |
| Generate Audio | `apex_engine/web/app.py` | `POST /api/project/<id>/generate-audio` → `api_generate_audio()` | Generate music via Fal.ai MiniMax Music v2 |
| Magic Fill | `apex_engine/web/app.py` | `POST /api/magic-fill` → `api_magic_fill()` | GPT-4o auto-population of all form fields |
| Single Analysis | `apex_engine/web/app.py` | `POST /api/project/<id>/analyze/<type>` → `api_analyze()` | Run single agent analysis (rhyme/flow/vowel/meme) |
| Field Help | `apex_engine/web/app.py` | `GET /api/field-help/<name>` → `api_field_help()` | Get tooltip text for form field |
| Tag Explorer | `apex_engine/web/app.py` | `GET /api/tag-explorer` → `api_tag_explorer()` | Get Sonauto tag taxonomy |
| Field Context | `apex_engine/web/app.py` | `GET /api/field-context/<name>` → `api_field_context()` | Get knowledge base context for field |
| Optimize Field | `apex_engine/web/app.py` | `POST /api/optimize-field` → `api_optimize_field()` | Per-field AI optimization |
| Full Analysis | `apex_engine/web/app.py` | `POST /api/run-full-analysis` → `api_run_full_analysis()` | Run all lyrical agents |
| Tools Panel | `apex_engine/web/templates/workspace.html` | JavaScript handlers | On-demand agent invocation (Rhyme, Flow, Quotability, Trend) |
| Pre-Production Console | `apex_engine/web/templates/workspace.html` | `updateConsole()` | Color-coded log panel (green=pass, yellow=warning, red=error) |
| Song Health Dashboard | `apex_engine/web/templates/workspace.html` | `updateHealthDashboard()` | Visual progress bars, tier badges (Gold/Platinum/Diamond/Viral) |
| Help Icons | `apex_engine/config/ui_text_config.py` | `FIELD_HELP` | Contextual tooltips for all input fields |

### A2. Lyrical Analysis Agents

| Agent | File | Class | Purpose |
|-------|------|-------|---------|
| Lyrical Architect | `apex_engine/src/agents/lyrical/lyrical_architect.py` | `LyricalArchitectAgent` | Generates lyrics with phonetic validation and rhyme schemes |
| Bars Analyzer | `apex_engine/src/agents/lyrical/agent_bars.py` | `BarsAnalyzer` | Phonetic analysis: rhyme density (RF), multisyllabic rhymes, assonance chains |
| Flow Analyzer | `apex_engine/src/agents/lyrical/agent_flow.py` | `FlowAnalyzer` | Syllable velocity, PDI (Plosive Density Index), breath markers, stress patterns |
| Vowel Analyzer | `apex_engine/src/agents/lyrical/agent_vowel.py` | `VowelAnalyzer` | Vowel entropy, assonance detection, earworm potential, euphony scoring |
| Context Analyzer | `apex_engine/src/agents/lyrical/agent_context.py` | `ContextAnalyzer` | Narrative consistency, persona tracking, theme coherence |

### A3. Audio Analysis Agents

| Agent | File | Class | Purpose |
|-------|------|-------|---------|
| Flow Supervisor | `apex_engine/src/agents/audio/flow_supervisor.py` | `FlowSupervisorAgent` | Beat tracking, onset alignment, syncopation scoring, quality audits |
| Frisson Detector | `apex_engine/src/agents/audio/agent_frisson.py` | `FrissonDetector` | Psychoacoustic analysis for emotional impact (chills detection) |
| Groove Analyzer | `apex_engine/src/agents/audio/agent_groove.py` | `GrooveAnalyzer` | Micro-timing analysis, swing detection, groove metrics |
| Spectral Analyzer | `apex_engine/src/agents/audio/agent_spectral.py` | `SpectralAnalyzer` | Frequency masking, clarity analysis, spectral balance |
| Timbre Analyzer | `apex_engine/src/agents/audio/agent_timbre.py` | `TimbreAnalyzer` | Vocal texture classification, processing detection |
| Audio Splitter | `apex_engine/src/agents/audio/agent_split.py` | `AudioSplitter` | Stem separation (vocals, drums, bass, other) |

### A4. Cultural Analysis Agents

| Agent | File | Class | Purpose |
|-------|------|-------|---------|
| Meme Analyzer | `apex_engine/src/agents/cultural/agent_meme.py` | `MemeAnalyzer` | Quotability scoring, punchline detection, meme potential |
| Trend Analyzer | `apex_engine/src/agents/cultural/agent_trend.py` | `TrendAnalyzer` | BPM/style alignment with current trends, market analysis |

### A5. Core Services

| Service | File | Class | Purpose |
|---------|------|-------|---------|
| Fal.ai Client | `apex_engine/src/services/fal_client.py` | `FalMusicClient` | MiniMax Music v2 API integration with async queue pattern |
| Payload Factory | `apex_engine/src/services/payload_factory.py` | `PayloadFactory` | GPT-4o translation of UI fields to Fal.ai payload format |
| Validators | `apex_engine/src/services/validators.py` | `validate_double_hash()`, `validate_breath_protocol()` | Double Hash (`## Tag ##`) and Breath (`//`) protocol enforcement |
| Field Optimizer | `apex_engine/src/services/optimizer.py` | `FieldOptimizer` | Per-field GPT-4o optimization with context awareness |

### A6. Core Orchestration

| Component | File | Class/Function | Purpose |
|-----------|------|----------------|---------|
| Orchestrator | `apex_engine/src/core/orchestrator.py` | `APEXOrchestrator` | State machine workflow coordination (PLAN → LYRICAL → GENERATE → SUPERVISE) |
| State Schema | `apex_engine/src/core/state_schema.py` | `RapGenerationState` | TypedDict defining shared state across all agents |
| Project Manager | `apex_engine/src/core/project_manager.py` | `ProjectManager` | File-based project CRUD operations |
| Mix Engineer | `apex_engine/src/core/mix_engineer.py` | `MixEngineerAgent` | Audio mastering and loudness normalization |
| Virality Predictor | `apex_engine/src/core/predictor.py` | `ViralityPredictor` | PVS (Predicted Virality Score) calculation |
| Feedback Controller | `apex_engine/src/core/feedback_logic.py` | `FeedbackController` | Iterative refinement based on quality metrics |
| Sonauto Operator | `apex_engine/src/core/suno_interface.py` | `SonautoOperator` | Legacy Sonauto API interface (generation, inpainting, extension) |
| LLM Client | `apex_engine/src/core/llm_client.py` | `LLMClient` | OpenAI GPT-4o integration for lyric generation/iteration |
| Fal Models | `apex_engine/src/core/fal_models.py` | `FalMusicPayload`, `validate_tags()` | Pydantic models for API payloads, tag validation |

### A7. Utilities

| Utility | File | Class/Function | Purpose |
|---------|------|----------------|---------|
| Logger | `apex_engine/src/utils/logger.py` | `APEXLogger`, `get_logger()` | Structured logging with trace IDs, color-coded output |
| Audio Tools | `apex_engine/src/utils/audio_tools.py` | Various functions | Librosa wrappers for audio processing |
| API Client | `apex_engine/src/utils/api_client.py` | `OpenAIClient`, `SonautoClient` | Unified API client implementations |
| Report Generator | `apex_engine/src/utils/report_generator.py` | `ReportGenerator` | Analysis report generation |

---

## Section B: Database & Schema Audit

### B1. Storage Type

**In-Memory or File-Based Storage only.**

APEX Engine does NOT use SQL databases or ORMs. All data persistence is file-based:

### B2. Project Data Schema

**Location:** `apex_engine/projects/<project_id>/`

**Directory Structure per Project:**
```
<timestamp>_<project-name>/
├── config.json          # Project metadata and settings
├── seed.txt             # Initial seed composition text
├── iterations/          # Version history of lyrics
│   ├── v1_lyrics.txt
│   └── v2_lyrics.txt
├── approved/            # Finalized content
│   ├── final_lyrics.txt
│   ├── api_payload.json
│   └── seed_composition.json
└── output/              # Generated audio files
    └── *.wav
```

**config.json Schema:**
```json
{
  "id": "string - Unique project ID (timestamp_name)",
  "name": "string - Human-readable project name",
  "created_at": "string - ISO timestamp",
  "updated_at": "string - ISO timestamp",
  "genre": "string - trap|boom_bap|phonk|drill|melodic|conscious",
  "bpm": "integer - 60-180",
  "tags": "array[string] - Sonauto-compatible tags",
  "mood": "string - aggressive|melancholic|hype|dark|confident|introspective",
  "prompt_strength": "float - CFG scale (1.0-5.0)",
  "balance_strength": "float - Balance between prompt/audio (0.0-1.0)",
  "current_iteration": "integer - Version counter",
  "status": "string - draft|approved|generating|completed|error",
  "approved_version": "integer|null - Which iteration is approved",
  "prompt_text": "string - Style/description prompt",
  "lyrics_text": "string - Song lyrics",
  "neuro_effects": "string - Neuropsychological effects",
  "neurochemical_effects": "string - Neurochemical targets",
  "musical_effects": "string - Production effects",
  "state": {
    "approval": {
      "lyrics": {
        "approved": "boolean",
        "timestamp": "string"
      }
    }
  }
}
```

### B3. Configuration Files

| File | Purpose | Format |
|------|---------|--------|
| `apex_engine/config/sonauto_tags.json` | Validated Sonauto API tags | JSON array |
| `apex_engine/config/genres.json` | Genre definitions and defaults | JSON object |
| `apex_engine/config/frisson_triggers.json` | Psychoacoustic trigger patterns | JSON object |
| `apex_engine/config/weights.json` | Metric weighting for PVS calculation | JSON object |
| `apex_engine/config/personas.json` | AI persona configurations | JSON object |

---

## Section C: Operational Risks

### C1. Financial Risk 💰

| Risk | Location | Details |
|------|----------|---------|
| **Fal.ai API Costs** | `apex_engine/src/services/fal_client.py` | Each generation costs ~$0.075. No budget cap in current implementation. |
| **OpenAI API Costs** | `apex_engine/src/core/llm_client.py`, `apex_engine/src/services/payload_factory.py`, `apex_engine/src/services/optimizer.py` | GPT-4o calls for: lyric generation, field optimization, payload translation, Magic Fill. Multiple API calls per user action. |
| **Sonauto API Costs** | `apex_engine/src/core/suno_interface.py` | Legacy endpoint: $0.075 per generation/inpaint/extend (`COST_PER_GENERATION_USD` constant in `fal_models.py`). |
| **No Rate Limiting** | `apex_engine/web/app.py` | No throttling on API endpoints. Users can trigger unlimited generations. |

### C2. Ban Risk ⚠️

| Risk | Location | Details |
|------|----------|---------|
| **API Rate Limits** | `apex_engine/src/services/fal_client.py` | Polling loop with exponential backoff (2-10s). Risk of hitting Fal.ai rate limits with concurrent requests. |
| **OpenAI Terms of Service** | `apex_engine/src/core/llm_client.py` | AI-generated lyrics may violate content policies if prompts contain explicit content. |

### C3. Data Loss Risk 📁

| Risk | Location | Details |
|------|----------|---------|
| **File Overwriting** | `apex_engine/src/core/project_manager.py`: `_save_json()` | Projects are overwritten on save. No backup/versioning. |
| **No Backup Mechanism** | `apex_engine/projects/` | Project directories can be manually deleted. No automated backups. |
| **Output Directory Cleanup** | `apex_engine/output/` | Simulated audio files accumulate. No automatic cleanup. |

### C4. PII Handling 🔒

| Risk | Location | Details |
|------|----------|---------|
| **Lyrics Content** | `apex_engine/projects/*/` | User-provided lyrics may contain personal information. Stored as plain text. |
| **API Keys in Environment** | `apex_engine/web/app.py` | `SECRET_KEY` has insecure default: `'apex-dev-key-change-in-prod'` |
| **No User Authentication** | `apex_engine/web/app.py` | No login system. All projects visible to anyone with access. |

---

## Section D: Code Health & Debt

### D1. Technical Debt Markers

**Grep Results for TODO, FIXME, BUG, HACK:**

```
No instances found in apex_engine/ source code.
```

The codebase is clean of explicit debt markers.

### D2. Test Suite Availability

**Test Suite Present: Yes**

**Location:** `apex_engine/tests/`

**Test Files:**
| File | Purpose |
|------|---------|
| `test_fal_models.py` | Fal.ai payload validation tests |
| `test_harness_synth.py` | Synthetic test harness for agents |
| `test_lyrical.py` | Lyrical agent unit tests |
| `test_master.py` | Mastering pipeline tests |

**Run Command:**
```bash
cd apex_engine && python -m pytest tests/ -v
```

### D3. Code Quality Observations

| Observation | Location | Impact |
|-------------|----------|--------|
| **Simulation Mode Fallbacks** | All API clients | Graceful degradation when API keys missing, but may mask integration issues |
| **Large Monolithic Files** | `apex_engine/web/app.py` (~1000 lines), `apex_engine/config/knowledge_base.py` (~640 lines) | Could benefit from refactoring |
| **Hardcoded Defaults** | `apex_engine/web/app.py:45` | `SECRET_KEY` default is insecure |
| **Mixed Concerns** | `apex_engine/src/core/llm_client.py` | Combines LLM client with prompt templates |
| **Duplicate Output Dirs** | `apex_engine/output/` and `output/` | Two separate output directories at different levels |

### D4. Dependency Health

All dependencies have version floors specified in `requirements.txt`. No pinned versions that could cause conflicts. Optional dependencies (langchain, demucs, pytest) are commented out.
