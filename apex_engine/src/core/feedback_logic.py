"""
Feedback Logic - The "Auto-Corrector" with Tradeoff Mechanism.

This module implements the feedback loop that determines:
- When to retry generation vs. accept current output
- How to adjust parameters between iterations
- Tradeoff balancing between competing quality metrics

Reference: Section 6.1 "Cost Management and Credit Optimization"
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class FeedbackAction(Enum):
    """Actions the feedback system can recommend."""
    ACCEPT = "accept"
    RETRY_GENERATION = "retry_generation"
    INPAINT_SECTION = "inpaint_section"
    ADJUST_LYRICS = "adjust_lyrics"
    CHANGE_STYLE = "change_style"
    ABORT = "abort"


@dataclass
class FeedbackDecision:
    """Result of feedback analysis."""
    action: FeedbackAction
    confidence: float
    adjustments: Dict[str, Any]
    reasoning: str


class FeedbackController:
    """
    Feedback Controller: The decision-making engine for iterative refinement.
    
    Analyzes quality metrics and determines:
    1. Whether current output is acceptable
    2. What action to take if not acceptable
    3. How to adjust parameters for the next iteration
    
    Implements tradeoff balancing between:
    - Rhyme density vs. flow consistency
    - BPM accuracy vs. natural feel
    - Frisson potential vs. stability
    - Cost (credits) vs. quality
    """
    
    QUALITY_WEIGHTS = {
        'rhyme_factor': 0.15,
        'flow_consistency': 0.15,
        'onset_confidence': 0.20,
        'bpm_accuracy': 0.15,
        'frisson_score': 0.15,
        'syncopation_score': 0.10,
        'spectral_clarity': 0.10
    }
    
    ACCEPTANCE_THRESHOLD = 0.65
    EXCELLENT_THRESHOLD = 0.85
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the feedback controller."""
        self.config = config or {}
        self.iteration_history = []
        
    def analyze(self, state: Dict[str, Any]) -> FeedbackDecision:
        """
        Analyze current state and recommend an action.
        
        Args:
            state: Current RapGenerationState
            
        Returns:
            FeedbackDecision with recommended action and adjustments
        """
        lyrical_metrics = state.get('lyrical_metrics', {})
        audio_metrics = state.get('analysis_metrics', {})
        iteration = state.get('iteration_count', 0)
        max_iterations = state.get('max_iterations', 3)
        
        overall_score, component_scores = self._calculate_quality_score(
            lyrical_metrics, 
            audio_metrics
        )
        
        self.iteration_history.append({
            'iteration': iteration,
            'overall_score': overall_score,
            'component_scores': component_scores
        })
        
        if iteration >= max_iterations:
            return FeedbackDecision(
                action=FeedbackAction.ACCEPT,
                confidence=0.5,
                adjustments={},
                reasoning=f"Maximum iterations ({max_iterations}) reached. Accepting current output."
            )
        
        if overall_score >= self.EXCELLENT_THRESHOLD:
            return FeedbackDecision(
                action=FeedbackAction.ACCEPT,
                confidence=0.95,
                adjustments={},
                reasoning=f"Excellent quality score ({overall_score:.2f}). No further iterations needed."
            )
        
        if overall_score >= self.ACCEPTANCE_THRESHOLD:
            improvement_potential = self._estimate_improvement_potential(component_scores)
            
            if improvement_potential < 0.1:
                return FeedbackDecision(
                    action=FeedbackAction.ACCEPT,
                    confidence=0.8,
                    adjustments={},
                    reasoning=f"Acceptable quality ({overall_score:.2f}) with low improvement potential."
                )
        
        return self._recommend_improvement(state, component_scores)
    
    def _calculate_quality_score(
        self, 
        lyrical: Dict[str, Any], 
        audio: Dict[str, Any]
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculate weighted quality score from component metrics.
        
        Returns:
            Tuple of (overall_score, component_scores_dict)
        """
        components = {}
        
        components['rhyme_factor'] = min(1.0, lyrical.get('rhyme_factor', 0) / 1.0)
        components['flow_consistency'] = lyrical.get('flow_consistency', 0.5)
        
        components['onset_confidence'] = audio.get('onset_confidence', 0.5)
        
        detected_bpm = audio.get('detected_bpm', 0)
        target_bpm = 100
        if detected_bpm > 0 and target_bpm > 0:
            deviation = abs(detected_bpm - target_bpm) / target_bpm
            components['bpm_accuracy'] = max(0, 1 - deviation * 2)
        else:
            components['bpm_accuracy'] = 0.5
        
        components['frisson_score'] = audio.get('frisson_score', 0.5)
        
        sync_idx = audio.get('syncopation_index', 22.5)
        optimal = 22.5
        components['syncopation_score'] = max(0, 1 - abs(sync_idx - optimal) / optimal)
        
        components['spectral_clarity'] = 1 - audio.get('mud_ratio', 0.15) * 3
        
        overall = 0.0
        for metric, weight in self.QUALITY_WEIGHTS.items():
            overall += weight * components.get(metric, 0.5)
        
        return overall, components
    
    def _estimate_improvement_potential(self, components: Dict[str, float]) -> float:
        """
        Estimate how much improvement is possible with another iteration.
        
        Low-scoring components that are easily adjustable indicate
        high improvement potential.
        """
        improvable = ['onset_confidence', 'frisson_score', 'spectral_clarity']
        
        potential = 0.0
        for comp in improvable:
            if comp in components:
                gap = 1.0 - components[comp]
                potential += gap * 0.5
        
        return min(1.0, potential / len(improvable))
    
    def _recommend_improvement(
        self, 
        state: Dict[str, Any], 
        components: Dict[str, float]
    ) -> FeedbackDecision:
        """
        Recommend specific improvements based on weakest components.
        """
        weakest = min(components.items(), key=lambda x: x[1])
        metric, score = weakest
        
        if metric in ('rhyme_factor', 'flow_consistency'):
            return FeedbackDecision(
                action=FeedbackAction.ADJUST_LYRICS,
                confidence=0.7,
                adjustments={
                    'focus': 'improve_rhymes' if metric == 'rhyme_factor' else 'smooth_flow',
                    'target_improvement': 0.2
                },
                reasoning=f"Weak {metric} ({score:.2f}). Recommending lyrical adjustment."
            )
        
        elif metric in ('onset_confidence', 'bpm_accuracy'):
            fix_segments = state.get('fix_segments', [])
            if fix_segments:
                return FeedbackDecision(
                    action=FeedbackAction.INPAINT_SECTION,
                    confidence=0.8,
                    adjustments={
                        'segments': fix_segments,
                        'prompt_emphasis': 'tighter flow, clearer vocals'
                    },
                    reasoning=f"Poor rhythmic alignment ({metric}: {score:.2f}). Inpainting weak sections."
                )
            else:
                return FeedbackDecision(
                    action=FeedbackAction.RETRY_GENERATION,
                    confidence=0.6,
                    adjustments={
                        'prompt_strength': 0.8,
                        'balance_strength': 0.75
                    },
                    reasoning=f"Rhythmic issues ({metric}: {score:.2f}). Full regeneration recommended."
                )
        
        else:
            return FeedbackDecision(
                action=FeedbackAction.RETRY_GENERATION,
                confidence=0.5,
                adjustments={},
                reasoning=f"General quality issues ({metric}: {score:.2f}). Trying another generation."
            )
    
    def get_trend(self) -> Dict[str, Any]:
        """Analyze the trend across iterations."""
        if len(self.iteration_history) < 2:
            return {'trend': 'insufficient_data', 'iterations': len(self.iteration_history)}
        
        scores = [h['overall_score'] for h in self.iteration_history]
        
        improvement = scores[-1] - scores[0]
        recent_improvement = scores[-1] - scores[-2]
        
        if improvement > 0.1 and recent_improvement > 0.02:
            trend = 'improving'
        elif improvement < -0.1:
            trend = 'degrading'
        elif abs(recent_improvement) < 0.01:
            trend = 'plateaued'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'total_improvement': improvement,
            'recent_improvement': recent_improvement,
            'iterations': len(self.iteration_history)
        }
