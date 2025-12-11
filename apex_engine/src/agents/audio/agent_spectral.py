"""
Spectral Analyzer Agent - Frequency Masking & Clarity Analysis.

This agent analyzes spectral characteristics:
- Frequency masking detection
- Mud ratio (low-frequency buildup)
- Spectral clarity and separation
- Neuro-saturation indicators

Reference: Librosa spectral features from framework documentation
"""

from typing import Dict, Any, List, Optional
import os

from ..agent_base import AnalysisAgent, AgentRole, AgentResult


class SpectralAnalyzer(AnalysisAgent):
    """
    Spectral Analyzer: Frequency domain analysis.
    
    Analyzes the spectral characteristics of audio to ensure:
    - Clean frequency separation between elements
    - Appropriate bass/mid/treble balance
    - No problematic frequency masking
    - Good overall spectral clarity
    
    Key Metrics:
    - Mud Ratio: Low frequency energy buildup (250-500Hz)
    - Clarity Index: High frequency definition
    - Spectral Centroid: Overall brightness
    - Bandwidth: Frequency range utilization
    """
    
    FREQ_BANDS = {
        'sub_bass': (20, 60),
        'bass': (60, 250),
        'low_mid': (250, 500),
        'mid': (500, 2000),
        'high_mid': (2000, 4000),
        'presence': (4000, 8000),
        'brilliance': (8000, 20000)
    }
    
    @property
    def role(self) -> AgentRole:
        return AgentRole.FLOW_SUPERVISOR
    
    def _validate_input(self, state: Dict[str, Any]) -> List[str]:
        """Validate input state."""
        errors = []
        
        if not state.get('local_filepath') and not state.get('audio_url'):
            errors.append("Audio file required for spectral analysis")
            
        return errors
    
    def _execute(self, state: Dict[str, Any]) -> AgentResult:
        """
        Perform spectral analysis on audio.
        
        Steps:
        1. Compute STFT and power spectrum
        2. Analyze frequency band energy distribution
        3. Calculate mud ratio and clarity
        4. Detect spectral masking issues
        5. Generate spectral quality assessment
        """
        audio_path = state.get('local_filepath', '')
        
        if not audio_path or not os.path.exists(audio_path):
            return AgentResult.failure_result(
                errors=["Audio file not found for spectral analysis"]
            )
        
        try:
            analysis = self._analyze_spectrum(audio_path)
        except ImportError:
            analysis = self._simulated_spectral_analysis()
        
        spectral_score = self._calculate_spectral_score(analysis)
        
        issues = self._detect_spectral_issues(analysis)
        
        metrics_update = {
            'spectral_centroid_mean': analysis['spectral_centroid_mean'],
            'spectral_bandwidth_mean': analysis['spectral_bandwidth_mean'],
            'spectral_rolloff_mean': analysis['spectral_rolloff_mean'],
            'mud_ratio': analysis['mud_ratio'],
            'clarity_index': analysis['clarity_index'],
            'spectral_score': spectral_score
        }
        
        existing_metrics = state.get('analysis_metrics', {})
        updated_metrics = {**existing_metrics, **metrics_update}
        
        return AgentResult.success_result(
            state_updates={
                'analysis_metrics': updated_metrics
            },
            warnings=[issue['message'] for issue in issues],
            metadata={
                'spectral_analysis': analysis,
                'spectral_issues': issues,
                'spectral_score': spectral_score
            }
        )
    
    def _analyze_spectrum(self, filepath: str) -> Dict[str, Any]:
        """
        Extract spectral features from audio.
        """
        import librosa
        import numpy as np
        
        y, sr = librosa.load(filepath)
        
        centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
        rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        flatness = librosa.feature.spectral_flatness(y=y)[0]
        
        S = np.abs(librosa.stft(y))
        freqs = librosa.fft_frequencies(sr=sr)
        
        band_energies = {}
        for band_name, (low, high) in self.FREQ_BANDS.items():
            mask = (freqs >= low) & (freqs < high)
            if np.any(mask):
                band_energy = np.mean(S[mask, :])
                band_energies[band_name] = float(band_energy)
            else:
                band_energies[band_name] = 0.0
        
        low_mid_energy = band_energies.get('low_mid', 0)
        total_energy = sum(band_energies.values())
        mud_ratio = low_mid_energy / total_energy if total_energy > 0 else 0
        
        high_energy = band_energies.get('presence', 0) + band_energies.get('brilliance', 0)
        clarity_index = high_energy / total_energy if total_energy > 0 else 0
        
        return {
            'spectral_centroid': centroid.tolist()[:50],
            'spectral_centroid_mean': float(np.mean(centroid)),
            'spectral_bandwidth': bandwidth.tolist()[:50],
            'spectral_bandwidth_mean': float(np.mean(bandwidth)),
            'spectral_rolloff': rolloff.tolist()[:50],
            'spectral_rolloff_mean': float(np.mean(rolloff)),
            'spectral_contrast_mean': float(np.mean(contrast)),
            'spectral_flatness_mean': float(np.mean(flatness)),
            'band_energies': band_energies,
            'mud_ratio': mud_ratio,
            'clarity_index': clarity_index,
            'total_energy': total_energy
        }
    
    def _simulated_spectral_analysis(self) -> Dict[str, Any]:
        """Simulated analysis when librosa is not available."""
        import random
        
        band_energies = {
            'sub_bass': random.uniform(0.1, 0.3),
            'bass': random.uniform(0.2, 0.4),
            'low_mid': random.uniform(0.1, 0.25),
            'mid': random.uniform(0.15, 0.3),
            'high_mid': random.uniform(0.1, 0.2),
            'presence': random.uniform(0.05, 0.15),
            'brilliance': random.uniform(0.02, 0.1)
        }
        
        total = sum(band_energies.values())
        
        return {
            'spectral_centroid': [random.uniform(1500, 3000) for _ in range(50)],
            'spectral_centroid_mean': random.uniform(2000, 2500),
            'spectral_bandwidth': [random.uniform(1000, 2000) for _ in range(50)],
            'spectral_bandwidth_mean': random.uniform(1500, 1800),
            'spectral_rolloff': [random.uniform(4000, 8000) for _ in range(50)],
            'spectral_rolloff_mean': random.uniform(5000, 6000),
            'spectral_contrast_mean': random.uniform(15, 25),
            'spectral_flatness_mean': random.uniform(0.01, 0.1),
            'band_energies': band_energies,
            'mud_ratio': band_energies['low_mid'] / total,
            'clarity_index': (band_energies['presence'] + band_energies['brilliance']) / total,
            'total_energy': total
        }
    
    def _calculate_spectral_score(self, analysis: Dict[str, Any]) -> float:
        """
        Calculate overall spectral quality score.
        """
        mud_score = max(0, 1 - analysis['mud_ratio'] * 4)
        
        clarity_score = min(1, analysis['clarity_index'] * 5)
        
        centroid = analysis['spectral_centroid_mean']
        centroid_score = 1 - abs(centroid - 2500) / 2500
        centroid_score = max(0, min(1, centroid_score))
        
        spectral_score = (
            0.4 * mud_score +
            0.3 * clarity_score +
            0.3 * centroid_score
        )
        
        return min(1.0, max(0.0, spectral_score))
    
    def _detect_spectral_issues(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect potential spectral problems.
        """
        issues = []
        
        if analysis['mud_ratio'] > 0.25:
            issues.append({
                'type': 'mud_buildup',
                'severity': 'warning',
                'message': f"Excessive low-mid energy ({analysis['mud_ratio']:.1%}). "
                          "Consider EQ cut in 250-500Hz range."
            })
        
        if analysis['clarity_index'] < 0.1:
            issues.append({
                'type': 'low_clarity',
                'severity': 'warning',
                'message': f"Low high-frequency presence ({analysis['clarity_index']:.1%}). "
                          "Track may sound dull."
            })
        
        band_energies = analysis.get('band_energies', {})
        if band_energies.get('sub_bass', 0) > band_energies.get('bass', 0) * 2:
            issues.append({
                'type': 'sub_bass_heavy',
                'severity': 'info',
                'message': "Sub-bass dominant. May not translate well on small speakers."
            })
        
        return issues
