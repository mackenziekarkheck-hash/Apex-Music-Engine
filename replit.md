# APEX Engine

## Overview
APEX Engine (Autonomous Aural Architectures) is a multi-agent framework for algorithmic rap composition using the Sonauto API via fal.ai endpoints. It uses LangGraph-style orchestration to generate, analyze, and iteratively refine rap music. The system optimizes for technical metrics (rhyme density, flow complexity), psychoacoustic responses (frisson, syncopation, groove), and commercial viability (earworm potential, quotability, trend alignment).

The project aims to create commercially viable rap tracks by leveraging advanced AI agents for lyrical composition, audio generation, and post-production, focusing on quantifiable metrics and psychoacoustic impact.

## User Preferences
- Framework targets rap/hip-hop specifically due to genre's unique requirements
- Designed for iterative refinement: lyrics → audio → analysis → inpainting → mastering
- Uses Sonauto via fal.ai (latent diffusion with inpainting/extension capabilities)
- WAV format required for accurate spectral analysis (compressed formats cause artifacts)

## System Architecture

### Core Design
APEX Engine employs a hierarchical agent system orchestrated by a LangGraph-style workflow. The system state is managed via a TypedDict for type-safe communication between agents. Key algorithms include the Raplyzer Protocol for phonetic analysis, Longuet-Higgins Model for syncopation, a Frisson Index for emotional impact, and a Predicted Virality Score (PVS).

### Agent Hierarchy
1.  **Lyrical Architect**: Generates lyrics with phonetic validation.
2.  **Sonauto Operator**: Interfaces with the Fal.ai API for audio generation.
3.  **Flow Supervisor**: Audits audio quality and performs beat tracking.
4.  **Mix Engineer**: Manages mastering and loudness normalization.
5.  **Frisson Detector**: Analyzes psychoacoustic elements for emotional impact.
6.  **Cultural Analysts**: Scores trend alignment and meme potential.

### Core Workflow
The system follows a `PLAN → LYRICAL_ARCHITECT → SONAUTO_GENERATE → FLOW_SUPERVISOR` sequence. The `FLOW_SUPERVISOR` can trigger an `INPAINT` loop for quality issues or proceed to `MIX_ENGINEER` for completion.

### UI/UX Decisions
The system includes a Flask Web UI for project management, featuring a redesigned project creation and workspace with component-based seed input (Prompt, Lyrics, Neuropsychological Effects, Neurochemical Targets, Musical Effects). It includes character/word counters, help modals with Sonauto Tag Explorer taxonomy, and an AI-powered seed optimization endpoint.

**Recent Enhancements (Dec 2025):**
- **Tools Panel**: On-demand agent invocation with buttons for Rhyme, Flow, Quotability, Trend, and Full Analysis
- **Pre-Production Console**: Embedded log panel with color-coded output (green=pass, yellow=warning, red=error, blue=info, purple=tips)
- **Magic Fill**: GPT-4o powered auto-population of all form fields from a concept/theme
- **Song Health Dashboard**: Visual progress bars, color-coded scores, and tier badges (Gold/Platinum/Diamond/Viral)
- **Help Icons**: Contextual help buttons (?) on all input fields with tooltips loaded from ui_text_config.py
- **Per-Field AI Optimization**: Individual "AI" buttons on each form field (Prompt, Lyrics, Neuro Effects, Neurochemical Effects, Musical Effects) for targeted improvements based on agent analysis context
- **Comprehensive Agent Logging**: Detailed console output showing all metrics from BarsAnalyzer (RF, multis, assonance), FlowAnalyzer (PDI, velocity, consistency), VowelAnalyzer (entropy, earworm, euphony), MemeAnalyzer (quotables, punchlines)
- **Agent-to-Field Mapping**: `FIELD_AGENT_MAPPING` config links each form field to relevant analysis agents for context-aware optimization
- **Replit AI Integrations**: LLMClient now uses `AI_INTEGRATIONS_OPENAI_BASE_URL` and `AI_INTEGRATIONS_OPENAI_API_KEY` environment variables for OpenAI access without user API key (billed to Replit credits)

### Technical Implementations
-   **API Client**: Uses the official `fal_client` SDK for Fal.ai integration, supporting both synchronous polling and asynchronous webhook patterns.
-   **State Management**: `RapGenerationState` (TypedDict) ensures type safety.
-   **Error Handling**: Standardized `AgentResult` pattern for agent communication.
-   **Budget Enforcement**: Supports USD cost tracking and budget limits.
-   **Tag Validation**: Efficient O(1) lookup using cached frozensets.

## External Dependencies

-   **Fal.ai Sonauto API**: Primary audio generation service.
    -   **Endpoints**: `/text-to-music`, `/inpaint`, `/extend`.
    -   **Authentication**: `Key <FAL_KEY>` header.
    -   **Key Parameters**: `prompt_strength` (CFG scale), `balance_strength`, `output_format` (WAV for analysis).
    -   **Cost Model**: $0.075 per generation, inpainting, or extension.
-   **OpenAI API**: Used for LLM-based lyric generation and iteration (e.g., GPT-4o via `LLMClient`).
-   **`fal_client` SDK**: Official Python client for Fal.ai.
-   **`librosa`**: For audio DSP, beat tracking, and spectral analysis.
-   **`numpy`**: Numerical operations.
-   **`soundfile`**: Audio file I/O.
-   **`pydantic`**: API payload validation for Sonauto requests.
-   **Flask**: Web framework for the UI.