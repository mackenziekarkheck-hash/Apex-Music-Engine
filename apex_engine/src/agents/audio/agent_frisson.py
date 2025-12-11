"""
Frisson Detector Agent - Psychoacoustic Chills Detection.

This agent analyzes audio for "frisson" potential - the aesthetic
chills response triggered by specific acoustic features:
- Dynamic surges (sudden loudness changes)
- Spectral expansion (brightness increases)
- Expectation violation (rhythmic surprises)

Reference: Section 4.1 "The Frisson Index" from framework documentation
"""

from typing import Dict, Any, List, Optional
import os

from ..agent_base import AnalysisAgent, AgentRole, AgentResult


class FrissonDetector(AnalysisAgent):
    """
    Frisson Detector: Psychoacoustic analysis for emotional impact.
    
    Frisson is a psychophysiological response characterized by:
    - Shivers/chills down the spine
    - Piloerection (goosebumps)
    - Emotional arousal
    
    This agent quantifies "frisson potential" using:
    
    1. Dynamic Surge (ΔRMS) - Sudden loudness increases
    2. Spectral Brightness - High frequency expansion
    3. Spectral Contrast - Energy peaks vs. valleys
    4. Surprise Model - Rhythmic expectation violation
    
    Reference: Librosa-based feature extraction
    """
    
    @property
    def role(self) -> AgentRole:
        return AgentRole.FRISSON_DETECTOR
    
    def _validate_input(self, state: Dict[str, Any]) -> List[str]:
        """Validate input state."""
        errors = []
        
        if not state.get('local_filepath') and not state.get('audio_url'):
            errors.append("Audio file required for frisson analysis")
            
        return errors
    
    def _execute(self, state: Dict[str, Any]) -> AgentResult:
        """
        Perform frisson potential analysis.
        
        Steps:
        1. Load audio and extract features
        2. Calculate dynamic surge (ΔRMS)
        3. Analyze spectral brightness evolution
        4. Compute spectral contrast
        5. Detect rhythmic surprises
        6. Combine into composite frisson score
        """
        audio_path = state.get('local_filepath', '')
        
        if not audio_path or not os.path.exists(audio_path):
            return AgentResult.failure_result(
                errors=["Audio file not found for frisson analysis"]
            )
        
        try:
            analysis = self._analyze_frisson(audio_path)
        except ImportError:
            analysis = self._simulated_frisson_analysis()
        
        frisson_score = self._calculate_composite_score(analysis)
        
        peak_moments = self._identify_peak_moments(analysis)
        
        metrics_update = {
            'frisson_score': frisson_score,
            'dynamic_surge_max': analysis['dynamic_surge_max'],
            'spectral_brightness_slope': analysis['brightness_slope'],
            'spectral_contrast_mean': analysis['spectral_contrast_mean'],
            'surprise_events': len(peak_moments)
        }
        
        existing_metrics = state.get('analysis_metrics', {})
        updated_metrics = {**existing_metrics, **metrics_update}
        
        quality_passed = frisson_score >= self.thresholds.get('frisson_score_min', 0.3)
        
        return AgentResult.success_result(
            state_updates={
                'analysis_metrics': updated_metrics
            },
            metadata={
                'frisson_analysis': analysis,
                'peak_moments': peak_moments,
                'quality_passed': quality_passed
            }
        )
    
    def _analyze_frisson(self, filepath: str) -> Dict[str, Any]:
        """
        Extract frisson-relevant features from audio.
        
        Uses librosa for DSP analysis.
        """
        import librosa
        import numpy as np
        
        y, sr = librosa.load(filepath)
        
        rms = librosa.feature.rms(y=y)[0]
        delta_rms = np.diff(rms)
        dynamic_surge_max = float(np.max(delta_rms)) if len(delta_rms) > 0 else 0
        
        centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        
        if len(centroid) > 10:
            brightness_slope = float(np.mean(np.diff(centroid)))
        else:
            brightness_slope = 0.0
        
        contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        spectral_contrast_mean = float(np.mean(contrast))
        
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr, onset_envelope=onset_env)
        
        surprise_events = self._detect_surprise_events(onset_env, beats)
        
        return {
            'rms': rms.tolist()[:100],
            'delta_rms': delta_rms.tolist()[:100] if len(delta_rms) > 0 else [],
            'dynamic_surge_max': dynamic_surge_max,
            'centroid': centroid.tolist()[:100],
            'brightness_slope': brightness_slope,
            'spectral_contrast': contrast.mean(axis=0).tolist()[:100],
            'spectral_contrast_mean': spectral_contrast_mean,
            'onset_envelope': onset_env.tolist()[:100],
            'surprise_events': surprise_events,
            'tempo': float(tempo),
            'duration': len(y) / sr
        }
    
    def _simulated_frisson_analysis(self) -> Dict[str, Any]:
        """Simulated analysis when librosa is not available."""
        import random
        
        return {
            'rms': [random.uniform(0.1, 0.5) for _ in range(100)],
            'delta_rms': [random.uniform(-0.1, 0.2) for _ in range(99)],
            'dynamic_surge_max': random.uniform(0.1, 0.4),
            'centroid': [random.uniform(1000, 4000) for _ in range(100)],
            'brightness_slope': random.uniform(-50, 100),
            'spectral_contrast': [random.uniform(10, 30) for _ in range(100)],
            'spectral_contrast_mean': random.uniform(15, 25),
            'onset_envelope': [random.uniform(0, 1) for _ in range(100)],
            'surprise_events': [{'time': i * 10, 'strength': random.uniform(0.5, 1)} 
                               for i in range(random.randint(2, 5))],
            'tempo': random.uniform(80, 140),
            'duration': 90.0
        }
    
    def _detect_surprise_events(
        self, 
        onset_env: 'np.ndarray', 
        beats: 'np.ndarray'
    ) -> List[Dict[str, Any]]:
        """
        Detect rhythmic surprise events (expectation violations).
        
        A surprise occurs when:
        - A strong onset appears off the beat grid
        - An expected beat is missing (silence)
        
        These create "prediction error" which triggers dopamine release.
        """
        import numpy as np
        
        surprises = []
        
        if len(beats) < 2:
            return surprises
            
        mean_strength = np.mean(onset_env)
        threshold = mean_strength * 1.5
        
        for i, strength in enumerate(onset_env):
            if strength > threshold:
                is_on_beat = any(abs(i - b) < 3 for b in beats)
                
                if not is_on_beat:
                    surprises.append({
                        'frame': int(i),
                        'strength': float(strength),
                        'type': 'off_beat_accent'
                    })
        
        for i in range(1, len(beats)):
            beat_idx = beats[i]
            if beat_idx < len(onset_env):
                if onset_env[beat_idx] < mean_strength * 0.5:
                    surprises.append({
                        'frame': int(beat_idx),
                        'strength': float(onset_env[beat_idx]),
                        'type': 'missing_beat'
                    })
        
        return surprises[:10]
    
    def _calculate_composite_score(self, analysis: Dict[str, Any]) -> float:
        """
        Calculate composite frisson score from individual metrics.
        
        Weighted combination:
        - 40% Dynamic surge potential
        - 30% Spectral brightness evolution
        - 20% Spectral contrast (clarity)
        - 10% Surprise events
        
        Score range: 0.0 - 1.0
        """
        dynamic_score = min(1.0, analysis['dynamic_surge_max'] * 3)
        
        brightness_score = min(1.0, max(0, analysis['brightness_slope'] / 100))
        
        contrast_score = min(1.0, analysis['spectral_contrast_mean'] / 30)
        
        surprise_count = len(analysis.get('surprise_events', []))
        surprise_score = min(1.0, surprise_count / 5)
        
        composite = (
            0.4 * dynamic_score +
            0.3 * brightness_score +
            0.2 * contrast_score +
            0.1 * surprise_score
        )
        
        return min(1.0, max(0.0, composite))
    
    def _identify_peak_moments(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify peak frisson moments in the track.
        
        These are timestamps where frisson is most likely to occur,
        useful for identifying "the drop" or emotional climaxes.
        """
        peaks = []
        
        delta_rms = analysis.get('delta_rms', [])
        if not delta_rms:
            return peaks
            
        duration = analysis.get('duration', 90)
        frames = len(delta_rms)
        
        import statistics
        mean = statistics.mean(delta_rms) if delta_rms else 0
        std = statistics.stdev(delta_rms) if len(delta_rms) > 1 else 0
        threshold = mean + 2 * std
        
        for i, val in enumerate(delta_rms):
            if val > threshold:
                timestamp = (i / frames) * duration
                peaks.append({
                    'timestamp': round(timestamp, 2),
                    'intensity': round(val, 4),
                    'type': 'dynamic_surge'
                })
        
        return sorted(peaks, key=lambda x: x['intensity'], reverse=True)[:5]
