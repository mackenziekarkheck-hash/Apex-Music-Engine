"""
Predictor - PVS (Predicted Virality Score) Calculator.

This module calculates a predicted virality score based on:
- Lyrical catchiness (earworm potential)
- Psychoacoustic impact (frisson score)
- Groove quality (danceability)
- Production quality metrics

Reference: Neuro-Acoustic Optimization framework
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class ViralityPrediction:
    """Result of virality score prediction."""
    pvs_score: float
    confidence: float
    component_scores: Dict[str, float]
    recommendations: List[str]
    tier: str


class ViralityPredictor:
    """
    Virality Predictor: Estimates song's viral potential.
    
    Calculates a Predicted Virality Score (PVS) based on
    psychoacoustic and lyrical features known to correlate
    with listener engagement and shareability.
    
    Components:
    - Earworm Score: Hook catchiness via vowel patterns
    - Frisson Index: Emotional impact moments
    - Groove Factor: Rhythmic engagement potential
    - Quotability: Memorable lyric density
    - Production Polish: Technical quality
    """
    
    COMPONENT_WEIGHTS = {
        'earworm': 0.25,
        'frisson': 0.20,
        'groove': 0.20,
        'quotability': 0.20,
        'production': 0.15
    }
    
    TIER_THRESHOLDS = {
        'viral_potential': 0.85,
        'high': 0.70,
        'moderate': 0.50,
        'low': 0.30
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the predictor."""
        self.config = config or {}
    
    def predict(self, state: Dict[str, Any]) -> ViralityPrediction:
        """
        Calculate predicted virality score from state.
        
        Args:
            state: RapGenerationState with metrics
            
        Returns:
            ViralityPrediction with score and analysis
        """
        lyrical = state.get('lyrical_metrics', {})
        audio = state.get('analysis_metrics', {})
        
        components = self._calculate_components(lyrical, audio)
        
        pvs = sum(
            self.COMPONENT_WEIGHTS[k] * components[k] 
            for k in self.COMPONENT_WEIGHTS
        )
        
        confidence = self._estimate_confidence(lyrical, audio)
        
        tier = self._determine_tier(pvs)
        
        recommendations = self._generate_recommendations(components, tier)
        
        return ViralityPrediction(
            pvs_score=pvs,
            confidence=confidence,
            component_scores=components,
            recommendations=recommendations,
            tier=tier
        )
    
    def _calculate_components(
        self, 
        lyrical: Dict[str, Any], 
        audio: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate individual component scores."""
        components = {}
        
        components['earworm'] = self._calculate_earworm_score(lyrical)
        
        components['frisson'] = audio.get('frisson_score', 0.5)
        
        components['groove'] = self._calculate_groove_score(audio)
        
        components['quotability'] = self._calculate_quotability(lyrical)
        
        components['production'] = self._calculate_production_score(audio)
        
        return components
    
    def _calculate_earworm_score(self, lyrical: Dict[str, Any]) -> float:
        """
        Calculate earworm potential.
        
        Based on:
        - Vowel pattern repetition
        - Hook simplicity
        - Rhythmic consistency
        """
        earworm = lyrical.get('earworm_score', 0.5)
        
        rhyme = lyrical.get('rhyme_factor', 0.5)
        if rhyme > 0:
            rhyme_bonus = min(0.2, rhyme * 0.15)
            earworm += rhyme_bonus
        
        variance = lyrical.get('syllable_variance', 5)
        if variance < 3:
            earworm += 0.1
        
        return min(1.0, max(0.0, earworm))
    
    def _calculate_groove_score(self, audio: Dict[str, Any]) -> float:
        """
        Calculate groove/danceability score.
        
        Based on syncopation index in the "groove zone".
        """
        sync_idx = audio.get('syncopation_index', 22.5)
        
        optimal = 22.5
        deviation = abs(sync_idx - optimal) / optimal
        sync_score = max(0, 1 - deviation)
        
        onset_conf = audio.get('onset_confidence', 0.5)
        
        return (sync_score * 0.6) + (onset_conf * 0.4)
    
    def _calculate_quotability(self, lyrical: Dict[str, Any]) -> float:
        """
        Calculate lyric quotability (meme potential).
        
        Based on:
        - Multi-syllabic rhymes (impressive wordplay)
        - Semantic coherence (makes sense out of context)
        - Punch line density
        """
        multis = lyrical.get('multisyllabic_rhymes', 0)
        multi_score = min(1.0, multis / 10)
        
        coherence = lyrical.get('semantic_coherence', 0.5)
        
        return (multi_score * 0.5) + (coherence * 0.5)
    
    def _calculate_production_score(self, audio: Dict[str, Any]) -> float:
        """
        Calculate production quality score.
        
        Based on spectral clarity and dynamic range.
        """
        mud_ratio = audio.get('mud_ratio', 0.15)
        clarity = max(0, 1 - mud_ratio * 4)
        
        dynamic_range = audio.get('dynamic_range', 0.3)
        dynamics = min(1.0, dynamic_range * 2)
        
        return (clarity * 0.6) + (dynamics * 0.4)
    
    def _estimate_confidence(
        self, 
        lyrical: Dict[str, Any], 
        audio: Dict[str, Any]
    ) -> float:
        """
        Estimate prediction confidence.
        
        Higher confidence when more metrics are available.
        """
        available_metrics = 0
        total_metrics = 10
        
        key_metrics = [
            'rhyme_factor', 'syllable_variance', 'earworm_score',
            'frisson_score', 'syncopation_index', 'onset_confidence',
            'mud_ratio', 'dynamic_range', 'semantic_coherence', 'flow_consistency'
        ]
        
        for m in key_metrics:
            if m in lyrical or m in audio:
                available_metrics += 1
        
        return 0.3 + (0.7 * available_metrics / total_metrics)
    
    def _determine_tier(self, pvs: float) -> str:
        """Determine virality tier from score."""
        if pvs >= self.TIER_THRESHOLDS['viral_potential']:
            return 'VIRAL_POTENTIAL'
        elif pvs >= self.TIER_THRESHOLDS['high']:
            return 'HIGH'
        elif pvs >= self.TIER_THRESHOLDS['moderate']:
            return 'MODERATE'
        elif pvs >= self.TIER_THRESHOLDS['low']:
            return 'LOW'
        else:
            return 'VERY_LOW'
    
    def _generate_recommendations(
        self, 
        components: Dict[str, float], 
        tier: str
    ) -> List[str]:
        """Generate actionable recommendations for improvement."""
        recommendations = []
        
        weakest = min(components.items(), key=lambda x: x[1])
        metric, score = weakest
        
        recommendation_map = {
            'earworm': "Add more vowel repetition in the hook for catchiness",
            'frisson': "Increase dynamic contrast, especially before the drop",
            'groove': "Tighten the beat alignment; consider more syncopation",
            'quotability': "Add more memorable punchlines with multi-syllabic rhymes",
            'production': "Improve mix clarity; reduce low-mid frequency buildup"
        }
        
        if score < 0.5:
            recommendations.append(f"Priority: {recommendation_map.get(metric, 'Improve ' + metric)}")
        
        if tier in ('MODERATE', 'LOW', 'VERY_LOW'):
            for comp, val in sorted(components.items(), key=lambda x: x[1]):
                if val < 0.6 and comp != metric:
                    recommendations.append(recommendation_map.get(comp, f"Improve {comp}"))
        
        if tier == 'VIRAL_POTENTIAL':
            recommendations.append("Track shows strong viral potential! Consider A/B testing hooks.")
        
        return recommendations[:5]
