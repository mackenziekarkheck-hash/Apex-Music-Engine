"""
Audio Analysis Agents for APEX Engine.

This module contains agents for Digital Signal Processing (DSP):
- Flow Supervisor: Beat tracking, onset detection
- Frisson Detector: Psychoacoustic chills detection
- Groove Analyzer: Micro-timing and swing analysis
- Spectral Analyzer: Frequency masking and clarity
- Timbre Analyzer: Vocal texture classification
- Audio Splitter: Stem separation

Reference: Sections 3.3 and 4 from framework documentation
"""

from .flow_supervisor import FlowSupervisorAgent
from .agent_frisson import FrissonDetector
from .agent_groove import GrooveAnalyzer
from .agent_spectral import SpectralAnalyzer
from .agent_timbre import TimbreAnalyzer
from .agent_split import AudioSplitter

__all__ = [
    'FlowSupervisorAgent',
    'FrissonDetector',
    'GrooveAnalyzer',
    'SpectralAnalyzer',
    'TimbreAnalyzer',
    'AudioSplitter'
]
