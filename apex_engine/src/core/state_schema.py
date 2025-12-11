"""
State Schema for APEX Engine - Hierarchical Agentic Rap Composition Framework.

This module defines the core state management structures used throughout the
LangGraph-based orchestration system. The RapGenerationState serves as the
central "Session File" that all agents read from and write to.

Reference: Based on the architectural design from "Autonomous Aural Architectures"
"""

from typing import TypedDict, List, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class GenerationStatus(Enum):
    """Status of the rap generation pipeline."""
    PENDING = "pending"
    DRAFTING = "drafting"
    VALIDATING = "validating"
    GENERATING = "generating"
    ANALYZING = "analyzing"
    INPAINTING = "inpainting"
    MASTERING = "mastering"
    COMPLETED = "completed"
    FAILED = "failed"


class StructuredPlan(TypedDict, total=False):
    """
    Parsed intent from user prompt.
    
    The Executive agent parses the raw user request into structured
    parameters that other agents can use for precise control.
    """
    bpm: Optional[int]
    key: Optional[str]
    subgenre: str
    mood: str
    era: Optional[str]
    instrumentation: List[str]
    vocal_style: Optional[str]
    song_structure: Dict[str, int]


class AnalysisMetrics(TypedDict, total=False):
    """
    Results from the Flow Supervisor's DSP analysis.
    
    Contains both rhythmic and psychoacoustic measurements
    used to evaluate generation quality.
    """
    detected_bpm: float
    bpm_confidence: float
    onset_confidence: float
    beat_frames: List[int]
    syncopation_index: float
    frisson_score: float
    dynamic_range: float
    spectral_centroid_mean: float
    rms_energy: float
    quality_passed: bool


class LyricalMetrics(TypedDict, total=False):
    """
    Metrics from the Lyrical Architect's analysis.
    
    Captures rhyme density, syllable counts, and flow dynamics
    based on the Raplyzer protocol.
    """
    rhyme_factor: float
    syllable_counts: List[int]
    syllable_variance: float
    stress_pattern: List[int]
    phoneme_map: List[List[str]]
    assonance_chains: List[List[str]]
    multisyllabic_rhymes: int
    flow_consistency: float


class InpaintSegment(TypedDict):
    """A segment of audio marked for regeneration."""
    start: float
    end: float
    reason: str
    prompt_override: Optional[str]


class RapGenerationState(TypedDict, total=False):
    """
    The Global State Schema for the APEX Engine.
    
    This TypedDict serves as the central memory shared by all agents
    in the LangGraph workflow. It contains all data required to:
    - Plan the song structure
    - Generate and validate lyrics
    - Interface with the Sonauto API
    - Analyze audio quality
    - Perform iterative refinement
    
    Design Philosophy:
    - Each field has clear ownership (writer agent)
    - Data flows unidirectionally between phases
    - Immutable patterns preferred for debugging
    
    Reference: Table 1 from "Autonomous Aural Architectures"
    """
    
    user_prompt: str
    structured_plan: StructuredPlan
    
    lyrics_draft: str
    lyrics_validated: str
    lyrical_metrics: LyricalMetrics
    
    tags: List[str]
    sonauto_prompt: str
    task_id: str
    audio_url: str
    local_filepath: str
    seed: Optional[int]
    
    analysis_metrics: AnalysisMetrics
    fix_segments: List[InpaintSegment]
    
    mastered_filepath: str
    reference_track: Optional[str]
    
    status: str
    iteration_count: int
    max_iterations: int
    credits_used: int
    credits_budget: int
    cost_usd: float
    cost_budget_usd: float
    request_id: str
    extend_request: Optional[Dict[str, Any]]
    inpaint_prompt: Optional[str]
    errors: List[str]
    warnings: List[str]
    is_complete: bool


@dataclass
class AgentContext:
    """
    Runtime context provided to each agent during execution.
    
    Contains configuration, API credentials, and shared resources
    that agents may need during their operation.
    """
    api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    output_directory: str = "./output"
    temp_directory: str = "./temp"
    reference_tracks_directory: str = "./references"
    max_retries: int = 3
    polling_interval: int = 5
    polling_timeout: int = 300
    debug_mode: bool = False
    log_level: str = "INFO"
    

def create_initial_state(user_prompt: str, **kwargs) -> RapGenerationState:
    """
    Factory function to create a properly initialized RapGenerationState.
    
    Args:
        user_prompt: The raw user request for the rap generation
        **kwargs: Optional overrides for default values
        
    Returns:
        A fully initialized RapGenerationState ready for pipeline execution
    """
    default_state: RapGenerationState = {
        'user_prompt': user_prompt,
        'structured_plan': {},
        'lyrics_draft': '',
        'lyrics_validated': '',
        'lyrical_metrics': {},
        'tags': [],
        'sonauto_prompt': '',
        'task_id': '',
        'audio_url': '',
        'local_filepath': '',
        'seed': None,
        'analysis_metrics': {},
        'fix_segments': [],
        'mastered_filepath': '',
        'reference_track': None,
        'status': GenerationStatus.PENDING.value,
        'iteration_count': 0,
        'max_iterations': kwargs.get('max_iterations', 3),
        'credits_used': 0,
        'credits_budget': kwargs.get('credits_budget', 500),
        'cost_usd': 0.0,
        'cost_budget_usd': kwargs.get('cost_budget_usd', 5.0),
        'request_id': '',
        'extend_request': None,
        'inpaint_prompt': None,
        'errors': [],
        'warnings': [],
        'is_complete': False
    }
    
    for key, value in kwargs.items():
        if key in default_state:
            default_state[key] = value
            
    return default_state


def validate_state(state: RapGenerationState) -> List[str]:
    """
    Validate the current state for consistency and completeness.
    
    Args:
        state: The current RapGenerationState
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    if not state.get('user_prompt'):
        errors.append("user_prompt is required")
        
    if state.get('iteration_count', 0) > state.get('max_iterations', 3):
        errors.append("Maximum iterations exceeded")
        
    if state.get('credits_used', 0) > state.get('credits_budget', 500):
        errors.append("Credits budget exceeded")
        
    if state.get('cost_usd', 0.0) > state.get('cost_budget_usd', 5.0):
        errors.append("USD cost budget exceeded")
        
    return errors
