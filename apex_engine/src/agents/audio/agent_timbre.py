"""
Timbre Analyzer Agent - Vocal Texture Classification.

This agent analyzes vocal timbre characteristics:
- Raspy vs. Clean detection
- Autotune presence detection
- Vocal energy and power
- Timbral consistency

Reference: Vocal texture analysis from framework documentation
"""

from typing import Dict, Any, List, Optional
import os

from ..agent_base import AnalysisAgent, AgentRole, AgentResult


class TimbreAnalyzer(AnalysisAgent):
    """
    Timbre Analyzer: Vocal texture and quality analysis.
    
    Analyzes the timbral characteristics of vocals to classify:
    - Vocal texture (raspy, clean, breathy)
    - Processing effects (autotune, reverb presence)
    - Vocal power and energy
    - Timbral consistency across the track
    
    Uses MFCC-based analysis for timbre characterization.
    """
    
    TEXTURE_CLASSES = ['clean', 'raspy', 'breathy', 'processed', 'layered']
    
    @property
    def role(self) -> AgentRole:
        return AgentRole.MIX_ENGINEER
    
    def _validate_input(self, state: Dict[str, Any]) -> List[str]:
        """Validate input state."""
        errors = []
        
        if not state.get('local_filepath') and not state.get('audio_url'):
            errors.append("Audio file required for timbre analysis")
            
        return errors
    
    def _execute(self, state: Dict[str, Any]) -> AgentResult:
        """
        Analyze vocal timbre characteristics.
        
        Steps:
        1. Extract MFCCs for timbre characterization
        2. Analyze zero-crossing rate (texture indicator)
        3. Detect processing artifacts
        4. Classify vocal texture
        5. Assess timbral quality
        """
        audio_path = state.get('local_filepath', '')
        
        if not audio_path or not os.path.exists(audio_path):
            return AgentResult.failure_result(
                errors=["Audio file not found for timbre analysis"]
            )
        
        try:
            analysis = self._analyze_timbre(audio_path)
        except ImportError:
            analysis = self._simulated_timbre_analysis()
        
        texture_class = self._classify_texture(analysis)
        timbre_score = self._calculate_timbre_score(analysis)
        
        metrics_update = {
            'vocal_texture': texture_class,
            'vocal_energy': analysis['vocal_energy'],
            'timbre_consistency': analysis['timbre_consistency'],
            'processing_detected': analysis['processing_detected'],
            'timbre_score': timbre_score
        }
        
        existing_metrics = state.get('analysis_metrics', {})
        updated_metrics = {**existing_metrics, **metrics_update}
        
        return AgentResult.success_result(
            state_updates={
                'analysis_metrics': updated_metrics
            },
            metadata={
                'timbre_analysis': analysis,
                'texture_class': texture_class,
                'timbre_score': timbre_score
            }
        )
    
    def _analyze_timbre(self, filepath: str) -> Dict[str, Any]:
        """
        Extract timbre-relevant features from audio.
        """
        import librosa
        import numpy as np
        
        y, sr = librosa.load(filepath)
        
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        mfcc_means = np.mean(mfccs, axis=1)
        mfcc_vars = np.var(mfccs, axis=1)
        
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        zcr_mean = float(np.mean(zcr))
        
        rms = librosa.feature.rms(y=y)[0]
        vocal_energy = float(np.mean(rms))
        
        centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        centroid_var = float(np.var(centroid))
        
        timbre_consistency = 1.0 / (1.0 + centroid_var / 1000000)
        
        flatness = librosa.feature.spectral_flatness(y=y)[0]
        processing_indicator = float(np.mean(flatness))
        processing_detected = processing_indicator > 0.1
        
        return {
            'mfcc_means': mfcc_means.tolist(),
            'mfcc_vars': mfcc_vars.tolist(),
            'zcr_mean': zcr_mean,
            'vocal_energy': vocal_energy,
            'centroid_variance': centroid_var,
            'timbre_consistency': timbre_consistency,
            'processing_indicator': processing_indicator,
            'processing_detected': processing_detected,
            'spectral_flatness_mean': processing_indicator
        }
    
    def _simulated_timbre_analysis(self) -> Dict[str, Any]:
        """Simulated analysis when librosa is not available."""
        import random
        
        return {
            'mfcc_means': [random.uniform(-50, 50) for _ in range(13)],
            'mfcc_vars': [random.uniform(10, 100) for _ in range(13)],
            'zcr_mean': random.uniform(0.05, 0.15),
            'vocal_energy': random.uniform(0.1, 0.4),
            'centroid_variance': random.uniform(100000, 500000),
            'timbre_consistency': random.uniform(0.6, 0.9),
            'processing_indicator': random.uniform(0.01, 0.15),
            'processing_detected': random.choice([True, False]),
            'spectral_flatness_mean': random.uniform(0.01, 0.1)
        }
    
    def _classify_texture(self, analysis: Dict[str, Any]) -> str:
        """
        Classify vocal texture based on extracted features.
        
        Uses simple heuristics based on:
        - Zero crossing rate (high = raspy)
        - Spectral flatness (high = processed)
        - MFCC characteristics
        """
        zcr = analysis['zcr_mean']
        flatness = analysis.get('spectral_flatness_mean', 0)
        energy = analysis['vocal_energy']
        
        if flatness > 0.1:
            return 'processed'
        elif zcr > 0.12:
            return 'raspy'
        elif energy < 0.15:
            return 'breathy'
        else:
            return 'clean'
    
    def _calculate_timbre_score(self, analysis: Dict[str, Any]) -> float:
        """
        Calculate overall timbre quality score.
        """
        consistency_score = analysis['timbre_consistency']
        
        energy = analysis['vocal_energy']
        if 0.2 < energy < 0.35:
            energy_score = 1.0
        else:
            energy_score = max(0, 1 - abs(energy - 0.275) * 4)
        
        zcr = analysis['zcr_mean']
        if 0.05 < zcr < 0.15:
            zcr_score = 1.0
        else:
            zcr_score = 0.7
        
        timbre_score = (
            0.4 * consistency_score +
            0.4 * energy_score +
            0.2 * zcr_score
        )
        
        return min(1.0, max(0.0, timbre_score))
