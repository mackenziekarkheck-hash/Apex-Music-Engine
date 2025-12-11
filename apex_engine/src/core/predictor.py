"""
Predictor - PVS (Predicted Virality Score) Calculator.

This module calculates a predicted virality score based on:
PVS = (W_Ly * S_Ly) + (W_Au * S_Au) + (W_Cul * S_Cul) + epsilon

Where:
- W_Ly, S_Ly = Lyrical weight (0.40) and score
- W_Au, S_Au = Audio weight (0.35) and score  
- W_Cul, S_Cul = Cultural weight (0.25) and score
- epsilon = Chaos factor (0-5% random for "happy accidents")

Reference: Neuro-Acoustic Optimization framework, weights.json
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import random
import json
import os


@dataclass
class ViralityPrediction:
    """Result of virality score prediction."""
    pvs_score: float
    confidence: float
    component_scores: Dict[str, float]
    category_scores: Dict[str, float]
    recommendations: List[str]
    tier: str
    epsilon_applied: float


class ViralityPredictor:
    """
    Virality Predictor: Estimates song's viral potential using PVS formula.
    
    PVS = (W_Ly * S_Ly) + (W_Au * S_Au) + (W_Cul * S_Cul) + epsilon
    
    Category Weights:
    - Lyrical: 0.40 (rhyme factor, flow, quotability, PDI)
    - Audio: 0.35 (frisson, syncopation, pocket, spectral clarity)
    - Cultural: 0.25 (trend alignment, meme potential, originality)
    
    Epsilon is a 0-5% chaos factor representing "happy accidents"
    that can push borderline tracks into virality.
    """
    
    CATEGORY_WEIGHTS = {
        'lyrical': 0.40,
        'audio': 0.35,
        'cultural': 0.25
    }
    
    LYRICAL_WEIGHTS = {
        'rhyme_factor': 0.30,
        'multisyllabic_density': 0.20,
        'flow_consistency': 0.20,
        'quotability': 0.15,
        'plosive_density_index': 0.15
    }
    
    AUDIO_WEIGHTS = {
        'frisson_score': 0.30,
        'syncopation_index': 0.25,
        'pocket_alignment': 0.20,
        'spectral_clarity': 0.15,
        'dynamic_range': 0.10
    }
    
    CULTURAL_WEIGHTS = {
        'trend_alignment': 0.40,
        'meme_potential': 0.35,
        'originality': 0.25
    }
    
    TIER_THRESHOLDS = {
        'viral_potential': 0.85,
        'high': 0.70,
        'moderate': 0.50,
        'low': 0.30
    }
    
    EPSILON_RANGE = (0.0, 0.05)
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the predictor with optional config."""
        self.config = config or {}
        self._load_weights()
    
    def _load_weights(self):
        """Load weights from configuration file if available."""
        try:
            weights_path = os.path.join(
                os.path.dirname(__file__), 
                '..', '..', 'config', 'weights.json'
            )
            if os.path.exists(weights_path):
                with open(weights_path, 'r') as f:
                    weights_config = json.load(f)
                    if 'category_weights' in weights_config:
                        self.CATEGORY_WEIGHTS = weights_config['category_weights']
                    if 'lyrical_weights' in weights_config:
                        for k, v in weights_config['lyrical_weights'].items():
                            if isinstance(v, dict) and 'weight' in v:
                                self.LYRICAL_WEIGHTS[k] = v['weight']
                    if 'audio_weights' in weights_config:
                        for k, v in weights_config['audio_weights'].items():
                            if isinstance(v, dict) and 'weight' in v:
                                self.AUDIO_WEIGHTS[k] = v['weight']
        except Exception:
            pass
    
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
        
        lyrical_score, lyrical_components = self._calculate_lyrical_score(lyrical)
        audio_score, audio_components = self._calculate_audio_score(audio)
        cultural_score, cultural_components = self._calculate_cultural_score(lyrical, audio)
        
        category_scores = {
            'lyrical': lyrical_score,
            'audio': audio_score,
            'cultural': cultural_score
        }
        
        base_pvs = (
            self.CATEGORY_WEIGHTS['lyrical'] * lyrical_score +
            self.CATEGORY_WEIGHTS['audio'] * audio_score +
            self.CATEGORY_WEIGHTS['cultural'] * cultural_score
        )
        
        epsilon = random.uniform(*self.EPSILON_RANGE)
        pvs = min(1.0, base_pvs + epsilon)
        
        confidence = self._estimate_confidence(lyrical, audio)
        
        tier = self._determine_tier(pvs)
        
        all_components = {
            **{f'lyrical_{k}': v for k, v in lyrical_components.items()},
            **{f'audio_{k}': v for k, v in audio_components.items()},
            **{f'cultural_{k}': v for k, v in cultural_components.items()}
        }
        
        recommendations = self._generate_recommendations(
            lyrical_score, audio_score, cultural_score,
            lyrical_components, audio_components, cultural_components,
            tier
        )
        
        return ViralityPrediction(
            pvs_score=pvs,
            confidence=confidence,
            component_scores=all_components,
            category_scores=category_scores,
            recommendations=recommendations,
            tier=tier,
            epsilon_applied=epsilon
        )
    
    def _calculate_lyrical_score(
        self, 
        lyrical: Dict[str, Any]
    ) -> Tuple[float, Dict[str, float]]:
        """Calculate the lyrical category score."""
        components = {}
        
        rf = lyrical.get('rhyme_factor', 0.3)
        if rf > 1.0:
            components['rhyme_factor'] = 1.0
        elif rf > 0.4:
            components['rhyme_factor'] = 0.6 + (rf - 0.4) * 0.67
        elif rf > 0.2:
            components['rhyme_factor'] = 0.3 + (rf - 0.2) * 1.5
        else:
            components['rhyme_factor'] = rf * 1.5
        
        multis = lyrical.get('multisyllabic_rhymes', 0)
        perfect = lyrical.get('perfect_rhymes', 0)
        total_rhymes = multis + perfect
        if total_rhymes > 0:
            multi_ratio = multis / max(1, total_rhymes)
            if 0.3 <= multi_ratio <= 0.6:
                components['multisyllabic_density'] = 0.8 + (multi_ratio - 0.3) * 0.67
            else:
                components['multisyllabic_density'] = min(1.0, multi_ratio * 1.5)
        else:
            components['multisyllabic_density'] = 0.3
        
        consistency = lyrical.get('flow_consistency', 0.5)
        components['flow_consistency'] = min(1.0, consistency * 1.2)
        
        coherence = lyrical.get('semantic_coherence', 0.5)
        word_coverage = lyrical.get('word_coverage_pct', 50) / 100
        components['quotability'] = (coherence * 0.5 + word_coverage * 0.5)
        
        pdi = lyrical.get('plosive_density_index', 0.12)
        if 0.12 <= pdi <= 0.18:
            components['plosive_density_index'] = 0.9
        elif pdi < 0.12:
            components['plosive_density_index'] = 0.5 + pdi * 3.3
        else:
            components['plosive_density_index'] = max(0.3, 1.0 - (pdi - 0.18) * 5)
        
        score = sum(
            self.LYRICAL_WEIGHTS.get(k, 0.2) * v 
            for k, v in components.items()
        )
        
        return min(1.0, score), components
    
    def _calculate_audio_score(
        self, 
        audio: Dict[str, Any]
    ) -> Tuple[float, Dict[str, float]]:
        """Calculate the audio category score."""
        components = {}
        
        frisson = audio.get('frisson_score', 0.5)
        components['frisson_score'] = min(1.0, frisson)
        
        sync_idx = audio.get('syncopation_index', 22.5)
        if 15 <= sync_idx <= 30:
            optimal_dist = min(abs(sync_idx - 15), abs(sync_idx - 30))
            components['syncopation_index'] = 0.8 + optimal_dist * 0.013
        elif sync_idx < 5:
            components['syncopation_index'] = 0.2
        elif sync_idx > 50:
            components['syncopation_index'] = 0.3
        else:
            components['syncopation_index'] = 0.5
        
        pocket = audio.get('pocket_alignment', 0.75)
        components['pocket_alignment'] = min(1.0, pocket * 1.2) if pocket >= 0.5 else pocket
        
        mud = audio.get('mud_ratio', 0.15)
        components['spectral_clarity'] = max(0.2, 1.0 - mud * 4)
        
        dr = audio.get('dynamic_range', 0.25)
        if 0.15 <= dr <= 0.35:
            components['dynamic_range'] = 0.9
        else:
            components['dynamic_range'] = 0.5
        
        score = sum(
            self.AUDIO_WEIGHTS.get(k, 0.2) * v 
            for k, v in components.items()
        )
        
        return min(1.0, score), components
    
    def _calculate_cultural_score(
        self, 
        lyrical: Dict[str, Any], 
        audio: Dict[str, Any]
    ) -> Tuple[float, Dict[str, float]]:
        """Calculate the cultural category score."""
        components = {}
        
        bpm = audio.get('detected_bpm', 100)
        current_trend_bpm = 142
        bpm_diff = abs(bpm - current_trend_bpm)
        if bpm_diff <= 10:
            components['trend_alignment'] = 0.9
        elif bpm_diff <= 20:
            components['trend_alignment'] = 0.7
        else:
            components['trend_alignment'] = max(0.3, 1.0 - bpm_diff * 0.01)
        
        quotability = lyrical.get('word_coverage_pct', 40) / 100
        rhyme_factor = lyrical.get('rhyme_factor', 0.3)
        components['meme_potential'] = min(1.0, quotability * 0.5 + rhyme_factor * 0.5)
        
        flow_class = lyrical.get('flow_classification', 'standard')
        if flow_class in ('syncopated_flow', 'complex'):
            components['originality'] = 0.8
        elif flow_class in ('broken_flow',):
            components['originality'] = 0.9
        else:
            components['originality'] = 0.5
        
        score = sum(
            self.CULTURAL_WEIGHTS.get(k, 0.33) * v 
            for k, v in components.items()
        )
        
        return min(1.0, score), components
    
    def _estimate_confidence(
        self, 
        lyrical: Dict[str, Any], 
        audio: Dict[str, Any]
    ) -> float:
        """
        Estimate prediction confidence.
        
        Higher confidence when more metrics are available.
        """
        key_lyrical = ['rhyme_factor', 'flow_consistency', 'plosive_density_index']
        key_audio = ['frisson_score', 'syncopation_index', 'onset_confidence', 'pocket_alignment']
        
        available = sum(1 for k in key_lyrical if k in lyrical)
        available += sum(1 for k in key_audio if k in audio)
        total = len(key_lyrical) + len(key_audio)
        
        return 0.3 + (0.7 * available / total)
    
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
        lyrical_score: float,
        audio_score: float,
        cultural_score: float,
        lyrical_comp: Dict[str, float],
        audio_comp: Dict[str, float],
        cultural_comp: Dict[str, float],
        tier: str
    ) -> List[str]:
        """Generate actionable recommendations for improvement."""
        recommendations = []
        
        categories = [
            ('Lyrical', lyrical_score, lyrical_comp),
            ('Audio', audio_score, audio_comp),
            ('Cultural', cultural_score, cultural_comp)
        ]
        
        weakest_cat = min(categories, key=lambda x: x[1])
        cat_name, _, components = weakest_cat
        
        if components:
            weakest_comp = min(components.items(), key=lambda x: x[1])
            comp_name, comp_score = weakest_comp
            
            recommendation_map = {
                'rhyme_factor': "Increase rhyme density - add more internal rhymes and perfect end rhymes",
                'multisyllabic_density': "Add more multi-syllabic rhyme chains for technical impact",
                'flow_consistency': "Even out syllable counts per bar for more consistent flow",
                'quotability': "Add more memorable punchlines and quotable one-liners",
                'plosive_density_index': "Increase hard consonants (b, d, g, k, p, t) for rhythmic punch",
                'frisson_score': "Add dynamic builds with brightness increases before the drop",
                'syncopation_index': "Adjust syncopation - aim for groove zone (15-30 index)",
                'pocket_alignment': "Tighten vocal delivery to the beat grid",
                'spectral_clarity': "Reduce mud (200-400Hz) and improve vocal clarity",
                'dynamic_range': "Add more dynamic contrast between sections",
                'trend_alignment': "Consider adjusting BPM toward current trends (~142 BPM)",
                'meme_potential': "Add more shareable/quotable moments",
                'originality': "Experiment with more unique flow patterns"
            }
            
            if comp_score < 0.6:
                rec = recommendation_map.get(comp_name, f"Improve {comp_name}")
                recommendations.append(f"Priority ({cat_name}): {rec}")
        
        if tier in ('MODERATE', 'LOW', 'VERY_LOW'):
            for comp_name, comp_score in sorted(
                {**lyrical_comp, **audio_comp, **cultural_comp}.items(),
                key=lambda x: x[1]
            )[:3]:
                if comp_score < 0.5:
                    rec = recommendation_map.get(comp_name, f"Improve {comp_name}")
                    if rec not in recommendations:
                        recommendations.append(rec)
        
        if tier == 'VIRAL_POTENTIAL':
            recommendations.append("Track shows strong viral potential! Consider A/B testing hooks.")
        elif tier == 'HIGH':
            recommendations.append("Solid track with high engagement potential.")
        
        return recommendations[:5]
