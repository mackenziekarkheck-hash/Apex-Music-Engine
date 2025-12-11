"""
APEX Engine Agents - Hierarchical AI Agent System.

This module contains all specialized agents in the framework:

Lyrical Agents:
- LyricalArchitectAgent: Text generation and validation
- BarsAnalyzer: Rhyme density and multi-syllabic analysis
- FlowAnalyzer: Syllabic velocity and rhythm dynamics
- VowelAnalyzer: Assonance and earworm detection
- ContextAnalyzer: Narrative coherence

Audio Agents:
- FlowSupervisorAgent: Beat tracking and onset alignment
- FrissonDetector: Psychoacoustic chills detection
- GrooveAnalyzer: Micro-timing and swing analysis
- SpectralAnalyzer: Frequency masking and clarity
- TimbreAnalyzer: Vocal texture classification
- AudioSplitter: Stem separation

Cultural Agents:
- MemeAnalyzer: Quotability and shareability
- TrendAnalyzer: Market trend alignment
"""

from .agent_base import (
    BaseAgent,
    AnalysisAgent,
    GenerativeAgent,
    AgentRole,
    AgentResult
)

from .lyrical import (
    LyricalArchitectAgent,
    BarsAnalyzer,
    FlowAnalyzer,
    VowelAnalyzer,
    ContextAnalyzer
)

from .audio import (
    FlowSupervisorAgent,
    FrissonDetector,
    GrooveAnalyzer,
    SpectralAnalyzer,
    TimbreAnalyzer,
    AudioSplitter
)

from .cultural import (
    MemeAnalyzer,
    TrendAnalyzer
)

__all__ = [
    'BaseAgent',
    'AnalysisAgent',
    'GenerativeAgent',
    'AgentRole',
    'AgentResult',
    'LyricalArchitectAgent',
    'BarsAnalyzer',
    'FlowAnalyzer',
    'VowelAnalyzer',
    'ContextAnalyzer',
    'FlowSupervisorAgent',
    'FrissonDetector',
    'GrooveAnalyzer',
    'SpectralAnalyzer',
    'TimbreAnalyzer',
    'AudioSplitter',
    'MemeAnalyzer',
    'TrendAnalyzer'
]
