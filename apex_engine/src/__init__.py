"""
APEX Engine - Autonomous Aural Architectures for Algorithmic Rap Composition.

A hierarchical agentic framework for generating high-quality rap music
using the Sonauto API, with advanced phonetic analysis, psychoacoustic
optimization, and iterative refinement.

Main Components:
- agents: Specialized AI agents for different aspects of music production
- core: Orchestration, state management, and API interfaces
- utils: Logging, audio tools, and report generation

Reference: "Autonomous Aural Architectures: A Hierarchical Agentic Framework
           for Algorithmic Rap Composition via the Sonauto API"
"""

from .core import (
    RapGenerationState,
    APEXOrchestrator,
    create_workflow,
    SonautoOperator,
    MixEngineerAgent,
    FeedbackController,
    ViralityPredictor
)

__version__ = "0.1.0"
__author__ = "APEX Engine Team"

__all__ = [
    'RapGenerationState',
    'APEXOrchestrator',
    'create_workflow',
    'SonautoOperator',
    'MixEngineerAgent',
    'FeedbackController',
    'ViralityPredictor',
    '__version__'
]
