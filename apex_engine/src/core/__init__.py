"""
Core module for APEX Engine orchestration and state management.

This module provides:
- State schema definitions (RapGenerationState)
- The main orchestrator (APEXOrchestrator)
- Sonauto API interface (SonautoOperator)
- Mix engineering agent (MixEngineerAgent)
- Feedback logic and virality prediction
"""

from .state_schema import (
    RapGenerationState, 
    AnalysisMetrics, 
    StructuredPlan,
    LyricalMetrics,
    InpaintSegment,
    AgentContext,
    GenerationStatus,
    create_initial_state,
    validate_state
)
from .orchestrator import APEXOrchestrator, create_workflow, WorkflowNode
from .suno_interface import SonautoOperator
from .mix_engineer import MixEngineerAgent
from .feedback_logic import FeedbackController, FeedbackAction, FeedbackDecision
from .predictor import ViralityPredictor, ViralityPrediction

__all__ = [
    'RapGenerationState',
    'AnalysisMetrics',
    'StructuredPlan',
    'LyricalMetrics',
    'InpaintSegment',
    'AgentContext',
    'GenerationStatus',
    'create_initial_state',
    'validate_state',
    'APEXOrchestrator',
    'create_workflow',
    'WorkflowNode',
    'SonautoOperator',
    'MixEngineerAgent',
    'FeedbackController',
    'FeedbackAction',
    'FeedbackDecision',
    'ViralityPredictor',
    'ViralityPrediction'
]
