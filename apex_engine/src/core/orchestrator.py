"""
APEX Orchestrator - Main Loop with Evolutionary Tree & Branching Logic.

This module implements the LangGraph-based state machine that coordinates
all agents in the hierarchical agentic framework.

Key Features:
- Finite state machine workflow (Draft -> Generate -> Analyze -> Fix -> Master)
- Conditional routing based on quality metrics
- Iteration limits and credit budget enforcement
- Human-in-the-loop interrupt support

Reference: Section 5 "Detailed Planning Documentation" from framework documentation
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import logging

from .state_schema import (
    RapGenerationState, 
    create_initial_state, 
    GenerationStatus,
    validate_state
)
from ..agents.agent_base import AgentResult


class WorkflowNode(Enum):
    """Nodes in the APEX workflow graph."""
    PLAN = "plan"
    LYRICAL_ARCHITECT = "lyrical_architect"
    SONAUTO_GENERATE = "sonauto_generate"
    FLOW_SUPERVISOR = "flow_supervisor"
    FRISSON_ANALYSIS = "frisson_analysis"
    MIX_ENGINEER = "mix_engineer"
    HUMAN_REVIEW = "human_review"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class TransitionRule:
    """Rule for conditional state transitions."""
    condition: Callable[[RapGenerationState], bool]
    target_node: WorkflowNode
    priority: int = 0


class APEXOrchestrator:
    """
    APEX Orchestrator: Coordinates the multi-agent workflow.
    
    Implements a LangGraph-style state machine where:
    - Each node represents an agent or decision point
    - Edges define transitions between nodes
    - Conditional edges enable quality-based routing
    
    Workflow:
    1. PLAN: Parse user prompt into structured plan
    2. LYRICAL_ARCHITECT: Generate and validate lyrics
    3. SONAUTO_GENERATE: Generate audio via API
    4. FLOW_SUPERVISOR: Analyze rhythmic quality
    5. (Conditional) Loop back to SONAUTO for inpainting OR
    6. MIX_ENGINEER: Apply final mastering
    7. COMPLETE: Finalize and export
    
    Reference: LangGraph StateGraph pattern
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the orchestrator.
        
        Args:
            config: Optional configuration for the workflow
        """
        self.config = config or {}
        self.logger = logging.getLogger("apex.orchestrator")
        
        self.agents = {}
        self._initialize_agents()
        
        self.transition_rules = self._define_transitions()
        
        self.execution_history = []
    
    def _initialize_agents(self):
        """Initialize all agents in the hierarchy."""
        try:
            from ..agents.lyrical.lyrical_architect import LyricalArchitectAgent
            from .suno_interface import SonautoOperator
            from ..agents.audio.flow_supervisor import FlowSupervisorAgent
            from ..agents.audio.agent_frisson import FrissonDetector
            from .mix_engineer import MixEngineerAgent
            
            self.agents = {
                WorkflowNode.LYRICAL_ARCHITECT: LyricalArchitectAgent(self.config),
                WorkflowNode.SONAUTO_GENERATE: SonautoOperator(self.config),
                WorkflowNode.FLOW_SUPERVISOR: FlowSupervisorAgent(self.config),
                WorkflowNode.FRISSON_ANALYSIS: FrissonDetector(self.config),
                WorkflowNode.MIX_ENGINEER: MixEngineerAgent(self.config)
            }
            self.logger.info(f"Initialized {len(self.agents)} agents")
            
        except ImportError as e:
            self.logger.warning(f"Some agents could not be initialized: {e}")
            self.agents = {}
    
    def _define_transitions(self) -> Dict[WorkflowNode, List[TransitionRule]]:
        """
        Define transition rules for the state machine.
        
        Each node has a list of conditional transitions evaluated
        in priority order. First matching rule determines next node.
        """
        return {
            WorkflowNode.PLAN: [
                TransitionRule(
                    condition=lambda s: bool(s.get('structured_plan')),
                    target_node=WorkflowNode.LYRICAL_ARCHITECT,
                    priority=0
                ),
                TransitionRule(
                    condition=lambda s: True,
                    target_node=WorkflowNode.ERROR,
                    priority=100
                )
            ],
            
            WorkflowNode.LYRICAL_ARCHITECT: [
                TransitionRule(
                    condition=lambda s: bool(s.get('lyrics_validated')),
                    target_node=WorkflowNode.SONAUTO_GENERATE,
                    priority=0
                ),
                TransitionRule(
                    condition=lambda s: len(s.get('errors', [])) > 0,
                    target_node=WorkflowNode.ERROR,
                    priority=1
                ),
                TransitionRule(
                    condition=lambda s: True,
                    target_node=WorkflowNode.LYRICAL_ARCHITECT,
                    priority=100
                )
            ],
            
            WorkflowNode.SONAUTO_GENERATE: [
                TransitionRule(
                    condition=lambda s: bool(s.get('local_filepath')),
                    target_node=WorkflowNode.FLOW_SUPERVISOR,
                    priority=0
                ),
                TransitionRule(
                    condition=lambda s: True,
                    target_node=WorkflowNode.ERROR,
                    priority=100
                )
            ],
            
            WorkflowNode.FLOW_SUPERVISOR: [
                TransitionRule(
                    condition=lambda s: (
                        bool(s.get('fix_segments')) and 
                        s.get('iteration_count', 0) < s.get('max_iterations', 3)
                    ),
                    target_node=WorkflowNode.SONAUTO_GENERATE,
                    priority=0
                ),
                TransitionRule(
                    condition=lambda s: s.get('is_complete', False),
                    target_node=WorkflowNode.MIX_ENGINEER,
                    priority=1
                ),
                TransitionRule(
                    condition=lambda s: s.get('iteration_count', 0) >= s.get('max_iterations', 3),
                    target_node=WorkflowNode.MIX_ENGINEER,
                    priority=2
                ),
                TransitionRule(
                    condition=lambda s: True,
                    target_node=WorkflowNode.ERROR,
                    priority=100
                )
            ],
            
            WorkflowNode.MIX_ENGINEER: [
                TransitionRule(
                    condition=lambda s: bool(s.get('mastered_filepath')),
                    target_node=WorkflowNode.COMPLETE,
                    priority=0
                ),
                TransitionRule(
                    condition=lambda s: True,
                    target_node=WorkflowNode.ERROR,
                    priority=100
                )
            ]
        }
    
    def run(self, user_prompt: str, **kwargs) -> RapGenerationState:
        """
        Execute the full generation workflow.
        
        Args:
            user_prompt: The user's raw request
            **kwargs: Additional parameters for the initial state
            
        Returns:
            The final RapGenerationState with all results
        """
        state = create_initial_state(user_prompt, **kwargs)
        
        state = self._plan_node(state)
        
        current_node = WorkflowNode.PLAN
        
        while current_node not in (WorkflowNode.COMPLETE, WorkflowNode.ERROR):
            next_node = self._get_next_node(current_node, state)
            
            self.execution_history.append({
                'from': current_node.value,
                'to': next_node.value,
                'iteration': state.get('iteration_count', 0)
            })
            
            self.logger.info(f"Transition: {current_node.value} -> {next_node.value}")
            
            if next_node in self.agents:
                result = self.agents[next_node].execute(state)
                state = self._apply_result(state, result)
            
            current_node = next_node
            
            if state.get('credits_used', 0) > state.get('credits_budget', 500):
                self.logger.warning("Credits budget exceeded")
                state['errors'] = state.get('errors', []) + ['Credits budget exceeded']
                current_node = WorkflowNode.ERROR
        
        state['status'] = GenerationStatus.COMPLETED.value if current_node == WorkflowNode.COMPLETE else GenerationStatus.FAILED.value
        
        return state
    
    def _plan_node(self, state: RapGenerationState) -> RapGenerationState:
        """
        Execute the planning phase.
        
        Parses the user prompt into a structured plan with:
        - Target BPM
        - Subgenre classification
        - Mood/atmosphere
        - Song structure
        """
        prompt = state.get('user_prompt', '').lower()
        
        plan = {
            'bpm': self._extract_bpm(prompt),
            'subgenre': self._extract_subgenre(prompt),
            'mood': self._extract_mood(prompt),
            'era': self._extract_era(prompt),
            'instrumentation': self._extract_instrumentation(prompt),
            'song_structure': {
                'intro_bars': 4,
                'verse_bars': 16,
                'chorus_bars': 8,
                'outro_bars': 4
            }
        }
        
        state['structured_plan'] = plan
        state['status'] = GenerationStatus.DRAFTING.value
        
        self.logger.info(f"Created plan: {plan}")
        
        return state
    
    def _extract_bpm(self, prompt: str) -> int:
        """Extract target BPM from prompt or infer from subgenre."""
        import re
        
        bpm_match = re.search(r'(\d{2,3})\s*bpm', prompt)
        if bpm_match:
            return int(bpm_match.group(1))
        
        if 'trap' in prompt or 'drill' in prompt:
            return 140
        elif 'boom bap' in prompt or 'old school' in prompt:
            return 90
        elif 'pop' in prompt:
            return 110
        else:
            return 100
    
    def _extract_subgenre(self, prompt: str) -> str:
        """Extract subgenre from prompt."""
        subgenres = ['trap', 'drill', 'boom bap', 'pop rap', 'cloud rap', 'emo rap']
        
        for sg in subgenres:
            if sg.replace(' ', '') in prompt.replace(' ', ''):
                return sg
        
        return 'trap'
    
    def _extract_mood(self, prompt: str) -> str:
        """Extract mood from prompt."""
        mood_map = {
            'aggressive': ['aggressive', 'angry', 'hard', 'intense'],
            'chill': ['chill', 'relaxed', 'mellow', 'smooth'],
            'dark': ['dark', 'ominous', 'moody', 'sinister'],
            'energetic': ['energetic', 'hype', 'upbeat', 'party'],
            'emotional': ['emotional', 'sad', 'melancholic', 'deep']
        }
        
        for mood, keywords in mood_map.items():
            for kw in keywords:
                if kw in prompt:
                    return mood
        
        return 'energetic'
    
    def _extract_era(self, prompt: str) -> Optional[str]:
        """Extract era preference from prompt."""
        eras = ['90s', '2000s', 'old school', 'modern', 'classic']
        
        for era in eras:
            if era in prompt:
                return era
        
        return None
    
    def _extract_instrumentation(self, prompt: str) -> List[str]:
        """Extract instrumentation preferences from prompt."""
        instruments = {
            '808': ['808', 'bass'],
            'piano': ['piano', 'keys'],
            'guitar': ['guitar'],
            'synth': ['synth', 'synthesizer'],
            'strings': ['strings', 'orchestral', 'violin'],
            'sample': ['sample', 'chopped']
        }
        
        found = []
        for inst, keywords in instruments.items():
            for kw in keywords:
                if kw in prompt:
                    found.append(inst)
                    break
        
        return found or ['808', 'synth']
    
    def _get_next_node(self, current: WorkflowNode, state: RapGenerationState) -> WorkflowNode:
        """Determine the next node based on current state and transition rules."""
        rules = self.transition_rules.get(current, [])
        
        sorted_rules = sorted(rules, key=lambda r: r.priority)
        
        for rule in sorted_rules:
            if rule.condition(state):
                return rule.target_node
        
        return WorkflowNode.ERROR
    
    def _apply_result(self, state: RapGenerationState, result: AgentResult) -> RapGenerationState:
        """Apply an agent's result to the state."""
        for key, value in result.state_updates.items():
            state[key] = value
        
        if result.errors:
            state['errors'] = state.get('errors', []) + result.errors
            
        if result.warnings:
            state['warnings'] = state.get('warnings', []) + result.warnings
        
        return state
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """Get a summary of the workflow execution."""
        return {
            'total_transitions': len(self.execution_history),
            'execution_history': self.execution_history,
            'agents_available': list(self.agents.keys())
        }
    
    def reset(self):
        """Reset the orchestrator state for a new run."""
        self.execution_history = []


def create_workflow(config: Optional[Dict[str, Any]] = None) -> APEXOrchestrator:
    """
    Factory function to create a configured APEX workflow.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured APEXOrchestrator instance
    """
    return APEXOrchestrator(config)
