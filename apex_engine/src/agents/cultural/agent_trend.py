"""
Trend Analyzer Agent - BPM Inflation Index & Derivative Rate.

This agent analyzes how well the track aligns with current trends:
- BPM trend matching
- Style derivative detection
- Trend adherence scoring
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from ..agent_base import AnalysisAgent, AgentRole, AgentResult


@dataclass
class TrendData:
    """Current trend benchmarks."""
    avg_bpm_trap: float = 145.0
    avg_bpm_drill: float = 140.0
    avg_bpm_boombap: float = 90.0
    trending_tags: List[str] = None
    
    def __post_init__(self):
        if self.trending_tags is None:
            self.trending_tags = ['trap', 'drill', 'dark', 'melodic']


class TrendAnalyzer(AnalysisAgent):
    """
    Trend Analyzer: Market alignment analysis.
    
    Evaluates how well the track aligns with current trends:
    - BPM positioning relative to genre averages
    - Style derivative rate (originality vs. trend-following)
    - Tag trend alignment
    
    Helps balance between trend-following and originality.
    """
    
    @property
    def role(self) -> AgentRole:
        return AgentRole.EXECUTIVE
    
    def _validate_input(self, state: Dict[str, Any]) -> List[str]:
        """Validate input state."""
        errors = []
        if not state.get('structured_plan'):
            errors.append("Structured plan required for trend analysis")
        return errors
    
    def _execute(self, state: Dict[str, Any]) -> AgentResult:
        """
        Analyze trend alignment.
        """
        plan = state.get('structured_plan', {})
        audio = state.get('analysis_metrics', {})
        
        trend_data = TrendData()
        
        bpm_analysis = self._analyze_bpm_positioning(plan, audio, trend_data)
        
        derivative_rate = self._calculate_derivative_rate(plan, state.get('tags', []))
        
        trend_score = self._calculate_trend_score(bpm_analysis, derivative_rate, plan)
        
        return AgentResult.success_result(
            state_updates={
                'trend_score': trend_score,
                'bpm_positioning': bpm_analysis['positioning'],
                'derivative_rate': derivative_rate
            },
            metadata={
                'bpm_analysis': bpm_analysis,
                'derivative_rate': derivative_rate,
                'trend_score': trend_score
            }
        )
    
    def _analyze_bpm_positioning(
        self, 
        plan: Dict[str, Any], 
        audio: Dict[str, Any],
        trends: TrendData
    ) -> Dict[str, Any]:
        """
        Analyze BPM positioning relative to genre trends.
        
        Returns position analysis: ahead, on-trend, or behind.
        """
        target_bpm = plan.get('bpm', 100)
        detected_bpm = audio.get('detected_bpm', target_bpm)
        subgenre = plan.get('subgenre', 'trap')
        
        genre_avg = {
            'trap': trends.avg_bpm_trap,
            'drill': trends.avg_bpm_drill,
            'boom bap': trends.avg_bpm_boombap,
            'pop rap': 105.0,
            'cloud rap': 75.0
        }.get(subgenre, 110.0)
        
        deviation = (detected_bpm - genre_avg) / genre_avg
        
        if deviation > 0.05:
            positioning = 'ahead'
        elif deviation < -0.05:
            positioning = 'behind'
        else:
            positioning = 'on_trend'
        
        return {
            'target_bpm': target_bpm,
            'detected_bpm': detected_bpm,
            'genre_avg': genre_avg,
            'deviation': deviation,
            'positioning': positioning
        }
    
    def _calculate_derivative_rate(
        self, 
        plan: Dict[str, Any], 
        tags: List[str]
    ) -> float:
        """
        Calculate derivative rate (trend-following vs. originality).
        
        High derivative = closely following trends
        Low derivative = more original/experimental
        """
        trend_data = TrendData()
        
        if not tags:
            tags = plan.get('tags', [])
        
        if not tags:
            return 0.5
        
        overlap = len(set(tags) & set(trend_data.trending_tags))
        derivative = overlap / len(trend_data.trending_tags)
        
        return min(1.0, derivative)
    
    def _calculate_trend_score(
        self, 
        bpm_analysis: Dict[str, Any],
        derivative_rate: float,
        plan: Dict[str, Any]
    ) -> float:
        """
        Calculate overall trend alignment score.
        
        Balances:
        - Being on-trend (commercial viability)
        - Some originality (differentiation)
        """
        positioning = bpm_analysis['positioning']
        position_scores = {
            'on_trend': 0.9,
            'ahead': 0.8,
            'behind': 0.6
        }
        position_score = position_scores.get(positioning, 0.7)
        
        optimal_derivative = 0.6
        derivative_score = 1.0 - abs(derivative_rate - optimal_derivative)
        
        trend_score = (0.6 * position_score) + (0.4 * derivative_score)
        
        return min(1.0, max(0.0, trend_score))
