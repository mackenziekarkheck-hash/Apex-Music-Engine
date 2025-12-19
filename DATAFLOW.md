# APEX Engine - Data Flow

## Step 1: Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/mackenziekarkheck-hash/Apex-Music-Engine.git
cd Apex-Music-Engine

# Create virtual environment (optional but recommended for local dev)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Additional system requirements (if not on Replit)
# Debian/Ubuntu: apt-get install ffmpeg libsndfile1
# macOS: brew install ffmpeg libsndfile
```

### Running the Application

**Web UI (Recommended):**
```bash
cd apex_engine && python -m web.app
# Access at: http://localhost:5000
```

**CLI Mode:**
```bash
cd apex_engine && python main.py --cli
```

**Demo Mode (Simulation):**
```bash
cd apex_engine && python main.py --demo
```

**Using Startup Scripts:**
```bash
# Linux/macOS
./run.sh

# Windows
run.bat

# With options
./run.sh --cli
./run.sh --demo
./run.sh --help
```

---

## Step 2: Environment Variable Cheat Sheet

| Variable Name | Default Value | Purpose | Required |
|--------------|---------------|---------|----------|
| `FAL_KEY` | `None` | Fal.ai API key for MiniMax Music v2 audio generation | Yes (for real generation) |
| `OPENAI_API_KEY` | `None` | OpenAI API key for GPT-4o (lyrics, optimization, Magic Fill) | Yes (for AI features) |
| `AI_INTEGRATIONS_OPENAI_API_KEY` | `None` | Replit AI integration OpenAI key (preferred over OPENAI_API_KEY) | Optional |
| `AI_INTEGRATIONS_OPENAI_BASE_URL` | `None` | Replit AI integration base URL | Optional |
| `SONAUTO_API_KEY` | `None` | Sonauto API key (legacy, for direct Sonauto API access) | Optional |
| `SECRET_KEY` | `'apex-dev-key-change-in-prod'` | Flask session secret key | Yes (change in production!) |

### Environment Variable Resolution Order

**For OpenAI:**
1. `AI_INTEGRATIONS_OPENAI_API_KEY` (Replit integration - preferred)
2. `OPENAI_API_KEY` (direct key)
3. Falls back to simulation mode if neither set

**For Audio Generation:**
1. `FAL_KEY` (Fal.ai - current implementation)
2. Falls back to simulation mode if not set

### Setting Environment Variables

**Replit:**
1. Open the Secrets panel (Tools → Secrets)
2. Add key-value pairs

**Local Development:**
```bash
# Create .env file
cp .env.example .env

# Edit with your keys
FAL_KEY=your_fal_ai_key
OPENAI_API_KEY=your_openai_key
SECRET_KEY=your_secure_random_string
```

---

## Step 3: Input/Output Schemas

### Input Files

#### Project Configuration (`config.json`)

**Location:** `apex_engine/projects/<project_id>/config.json`

**Raw Example:**
```json
{
  "id": "2025-12-12_004807_test-project",
  "name": "Test Project",
  "created_at": "2025-12-12T00:48:07.123456",
  "updated_at": "2025-12-12T01:30:22.654321",
  "genre": "trap",
  "bpm": 140,
  "tags": ["trap", "hip hop", "rap", "dark", "aggressive"],
  "mood": "aggressive",
  "prompt_strength": 2.0,
  "balance_strength": 0.7,
  "current_iteration": 2,
  "status": "approved",
  "approved_version": 2,
  "prompt_text": "Dark trap with heavy 808s, ominous piano, and aggressive delivery",
  "lyrics_text": "[Verse]\nLines in the night, shadows creep\nBass so heavy it don't let you sleep\n\n[Chorus]\nWe rise up, never fall down\nKing of the city, wear the crown",
  "neuro_effects": "Frisson on chorus drop, tension build in verse",
  "neurochemical_effects": "Dopamine hooks, adrenaline verses",
  "musical_effects": "Heavy bass, reverb vocals, ## Drop ## after chorus",
  "state": {
    "approval": {
      "lyrics": {
        "approved": true,
        "timestamp": "2025-12-12T01:30:22.654321"
      }
    }
  }
}
```

#### Seed Text (`seed.txt`)

**Location:** `apex_engine/projects/<project_id>/seed.txt`

**Raw Example:**
```
Dark trap banger about rising from nothing.
Theme: underdog story, street success
Vibe: aggressive but triumphant
Key lines to include: "started from the bottom", "crown on my head"
```

#### Approved Lyrics (`approved/final_lyrics.txt`)

**Location:** `apex_engine/projects/<project_id>/approved/final_lyrics.txt`

**Raw Example:**
```
[Verse 1]
Started from the bottom, now I'm here
Every doubt I had, disappeared
Grind so hard, they thought I was insane
Now they watch me shine through the pain

[Pre-Chorus]
Can't nobody stop this momentum
When you at the top, they resent 'em

[Chorus]
Crown on my head, yeah I earned it
Every lesson learned, I discerned it
Rise up, never fall down
King of this city, hold it down

[Verse 2]
//
Late nights, early mornings, no sleep
Stacking wins while they counting sheep
//
Every setback was a setup
For the comeback that would never let up

[Bridge]
## Instrumental Break ##

[Outro]
Remember where you came from
But never forget where you're going
```

#### API Payload (`approved/api_payload.json`)

**Location:** `apex_engine/projects/<project_id>/approved/api_payload.json`

**Raw Example (Fal.ai format):**
```json
{
  "input": {
    "prompt": "Dark trap, heavy 808s, ominous piano, aggressive delivery, soaring dynamics, catchy hooks",
    "lyrics_prompt": "[Verse 1]\nStarted from the bottom, now I'm here\nEvery doubt I had, disappeared\n\n[Chorus]\nCrown on my head, yeah I earned it\n\n## Drop ##\n\n[Verse 2]\nLate nights, early mornings, no sleep",
    "song_duration": 120
  }
}
```

### Output Files

| Output | Location | Mode | Description |
|--------|----------|------|-------------|
| Generated Audio | `apex_engine/output/*.wav` | Overwrite | Raw audio from Fal.ai/Sonauto |
| Mastered Audio | `apex_engine/output/mastered/*_mastered.wav` | Overwrite | Post-mastering output |
| Iteration Lyrics | `apex_engine/projects/<id>/iterations/v<n>_lyrics.txt` | Append (new file per version) | Version history of lyrics |
| Project Config | `apex_engine/projects/<id>/config.json` | Overwrite | Project metadata (updated on save) |
| Approved Seed | `apex_engine/projects/<id>/approved/seed_composition.json` | Overwrite | Final approved seed data |

### Simulated Output Files

When running without API keys, the system generates simulated files:

```
apex_engine/output/
├── simulated_sim_1765490310_8518.ogg       # Simulated audio
├── simulated_sim_1765490311_4633.ogg
└── mastered/
    ├── simulated_sim_1765490310_8518.ogg_mastered.wav
    └── simulated_sim_1765490311_4633.ogg_mastered.wav
```

---

## Step 4: Mermaid Flowchart (Logic & State)

### Main Application Flow

```mermaid
flowchart TD
    subgraph User Interface
        A[Start: User Opens App] --> B[Project Dashboard]
        B --> C{Create New or Open Existing?}
        C -->|New| D[New Project Form]
        C -->|Existing| E[Load Project Workspace]
        D --> E
    end

    subgraph Seed Composition
        E --> F[Edit Seed Fields]
        F --> G{Use AI Assistance?}
        G -->|Magic Fill| H[GPT-4o: Auto-populate All Fields]
        G -->|Per-Field AI| I[GPT-4o: Optimize Single Field]
        G -->|Manual| J[User Edits Directly]
        H --> F
        I --> F
        J --> K[Save Project]
    end

    subgraph Analysis Pipeline
        K --> L{Run Analysis?}
        L -->|Yes| M[Lyrical Agents Execute]
        M --> N[BarsAnalyzer: Rhyme Metrics]
        M --> O[FlowAnalyzer: Syllable Velocity]
        M --> P[VowelAnalyzer: Euphony Score]
        M --> Q[MemeAnalyzer: Quotability]
        N & O & P & Q --> R[Aggregate Metrics]
        R --> S[Update Health Dashboard]
        S --> T{Metrics Acceptable?}
        T -->|No| F
        T -->|Yes| U[Approve Lyrics]
        L -->|No| U
    end

    subgraph Audio Generation
        U --> V{Generate Audio?}
        V -->|Yes| W[PayloadFactory: Build Fal.ai Payload]
        W --> X[Validators: Double Hash & Breath Check]
        X --> Y{Validation Passed?}
        Y -->|No| Z[Show Validation Issues]
        Z --> F
        Y -->|Yes| AA[FalMusicClient: Submit to Queue]
    end

    subgraph Fal.ai Integration
        AA --> AB[Poll Status with Backoff]
        AB --> AC{Status?}
        AC -->|IN_QUEUE| AB
        AC -->|IN_PROGRESS| AB
        AC -->|COMPLETED| AD[Download Audio URL]
        AC -->|FAILED| AE[Error Handler]
        AE --> AF{Retry?}
        AF -->|Yes, < 3 attempts| AA
        AF -->|No| AG[Show Error to User]
        AG --> F
    end

    subgraph Post-Processing
        AD --> AH[MixEngineer: Master Audio]
        AH --> AI[Save to output/mastered/]
        AI --> AJ[Update Project Status]
        AJ --> AK[Complete: Audio Ready]
    end

    subgraph Data Storage
        DB[(File System)]
        K -.->|Write| DB
        E -.->|Read| DB
        AI -.->|Write| DB
    end
```

### Orchestrator State Machine

```mermaid
stateDiagram-v2
    [*] --> PLAN: User submits prompt

    PLAN --> LYRICAL_ARCHITECT: Plan approved
    PLAN --> ERROR: Planning failed

    LYRICAL_ARCHITECT --> SONAUTO_GENERATE: Lyrics validated
    LYRICAL_ARCHITECT --> LYRICAL_ARCHITECT: Iteration needed
    LYRICAL_ARCHITECT --> ERROR: Max iterations exceeded

    SONAUTO_GENERATE --> FLOW_SUPERVISOR: Audio generated
    SONAUTO_GENERATE --> ERROR: Generation failed

    FLOW_SUPERVISOR --> FRISSON_ANALYSIS: Quality check passed
    FLOW_SUPERVISOR --> INPAINT: Quality issues detected
    FLOW_SUPERVISOR --> ERROR: Critical issues

    INPAINT --> FLOW_SUPERVISOR: Re-evaluate after fix
    INPAINT --> ERROR: Inpainting failed

    FRISSON_ANALYSIS --> MIX_ENGINEER: Psychoacoustic check passed
    FRISSON_ANALYSIS --> INPAINT: Issues need fixing

    MIX_ENGINEER --> HUMAN_REVIEW: Mastering complete
    MIX_ENGINEER --> ERROR: Mastering failed

    HUMAN_REVIEW --> COMPLETE: User approves
    HUMAN_REVIEW --> LYRICAL_ARCHITECT: User requests changes

    COMPLETE --> [*]
    ERROR --> [*]
```

### API Request Flow

```mermaid
sequenceDiagram
    participant User
    participant Flask as Flask App
    participant PF as PayloadFactory
    participant Val as Validators
    participant Fal as FalMusicClient
    participant API as Fal.ai API

    User->>Flask: POST /api/project/{id}/generate-audio
    Flask->>Flask: Load project, check approval
    
    alt Not Approved
        Flask-->>User: 400 Error: Lyrics must be approved
    end

    Flask->>PF: construct_payload(ui_data)
    
    alt Has OpenAI Key
        PF->>PF: GPT-4o translation
    else Simulation Mode
        PF->>PF: Basic field mapping
    end
    
    PF-->>Flask: fal_payload

    Flask->>Val: validate_full_payload(prompt, lyrics)
    Val->>Val: Double Hash validation
    Val->>Val: Breath protocol check
    Val-->>Flask: validated_prompt, validated_lyrics, issues

    Flask->>Fal: generate_music(payload)
    
    alt Has FAL_KEY
        Fal->>API: POST /fal-ai/minimax-music/v2
        API-->>Fal: {request_id, status: IN_QUEUE}
        
        loop Poll until complete
            Fal->>API: GET /status/{request_id}
            API-->>Fal: {status}
        end
        
        Fal->>API: GET /result/{request_id}
        API-->>Fal: {audio_url, duration}
    else Simulation Mode
        Fal->>Fal: Generate simulated response
    end
    
    Fal-->>Flask: FalGenerationResult
    
    alt Success
        Flask-->>User: {success: true, audio_url, duration}
    else Failure
        Flask-->>User: {success: false, error}
    end
```

### Error Handling & Retry Logic

```mermaid
flowchart TD
    subgraph Retry Logic
        A[API Call] --> B{Success?}
        B -->|Yes| C[Return Result]
        B -->|No| D{Attempt < Max?}
        D -->|Yes| E[Exponential Backoff]
        E --> F[Wait: 2^attempt seconds]
        F --> A
        D -->|No| G[Raise Exception]
    end

    subgraph Backoff Schedule
        H[Attempt 1] --> I[Wait 2s]
        I --> J[Attempt 2] --> K[Wait 4s]
        K --> L[Attempt 3] --> M[Wait 8s]
        M --> N[Max 10s cap]
    end

    subgraph Error Categories
        O[Network Error] --> P[Retry]
        Q[Rate Limit 429] --> R[Retry with longer wait]
        S[Auth Error 401] --> T[Fail immediately]
        U[Server Error 5xx] --> V[Retry]
        W[Client Error 4xx] --> X[Fail immediately]
    end
```
