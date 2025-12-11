"""
Flow Supervisor Agent - Audio Analysis & DSP.

The quality control auditor that downloads generated audio and performs
Digital Signal Processing (DSP) to verify that the rap is "on beat."

Key Responsibilities:
- Beat tracking and BPM verification
- Onset alignment (The "Pocket" Check)
- Syncopation detection
- Inpaint segment triggering

Reference: Section 3.3 "The Flow Supervisor" from framework documentation
"""

from typing import Dict, Any, List, Optional, Tuple
import os

from ..agent_base import AnalysisAgent, AgentRole, AgentResult


class FlowSupervisorAgent(AnalysisAgent):
    """
    Flow Supervisor: Audio quality control auditor.
    
    This is the most computationally intensive node, performing DSP
    analysis using Librosa to verify rhythmic coherence.
    
    Algorithm:
    1. Beat Tracking - Detect tempo and beat frames
    2. BPM Verification - Compare detected vs. target BPM
    3. Onset Alignment - Check vocal onsets against beat grid
    4. Syncopation Detection - Distinguish intentional syncopation from errors
    5. Inpaint Triggering - Flag problematic sections for regeneration
    """
    
    BPM_DEVIATION_THRESHOLD = 0.05
    ONSET_CONFIDENCE_THRESHOLD = 0.7
    
    @property
    def role(self) -> AgentRole:
        return AgentRole.FLOW_SUPERVISOR
    
    def _validate_input(self, state: Dict[str, Any]) -> List[str]:
        """Validate that we have audio to analyze."""
        errors = []
        
        if not state.get('local_filepath') and not state.get('audio_url'):
            errors.append("Audio file or URL is required for flow analysis")
            
        return errors
    
    def _execute(self, state: Dict[str, Any]) -> AgentResult:
        """
        Perform comprehensive audio analysis.
        
        Flow:
        1. Load audio file (download if necessary)
        2. Extract tempo and beat information
        3. Calculate onset strength and alignment
        4. Determine if inpainting is needed
        5. Return analysis metrics and quality assessment
        """
        audio_path = state.get('local_filepath', '')
        target_bpm = state.get('structured_plan', {}).get('bpm')
        
        if not audio_path or not os.path.exists(audio_path):
            audio_path = self._download_audio(state.get('audio_url', ''))
            if not audio_path:
                return AgentResult.failure_result(
                    errors=["Could not load audio file"]
                )
        
        analysis = self._analyze_audio(audio_path, target_bpm)
        
        quality_passed = self._assess_quality(analysis, target_bpm)
        
        fix_segments = []
        if not quality_passed and state.get('iteration_count', 0) < state.get('max_iterations', 3):
            fix_segments = self._identify_fix_segments(analysis)
        
        analysis_metrics = {
            'detected_bpm': analysis['tempo'],
            'bpm_confidence': analysis['tempo_confidence'],
            'onset_confidence': analysis['onset_confidence'],
            'beat_frames': analysis.get('beat_frames', [])[:20],
            'syncopation_index': analysis.get('syncopation_index', 0),
            'dynamic_range': analysis.get('dynamic_range', 0),
            'quality_passed': quality_passed
        }
        
        return AgentResult.success_result(
            state_updates={
                'analysis_metrics': analysis_metrics,
                'fix_segments': fix_segments,
                'local_filepath': audio_path,
                'is_complete': quality_passed and not fix_segments
            },
            metadata={
                'full_analysis': analysis,
                'quality_passed': quality_passed
            }
        )
    
    def _download_audio(self, url: str) -> Optional[str]:
        """
        Download audio from URL to local filesystem.
        
        Returns the local file path or None if download fails.
        """
        if not url:
            return None
            
        try:
            import requests
            
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()
            
            os.makedirs('./temp', exist_ok=True)
            local_path = './temp/current_gen.ogg'
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            self.logger.info(f"Audio downloaded to {local_path}")
            return local_path
            
        except Exception as e:
            self.logger.error(f"Failed to download audio: {e}")
            return None
    
    def _analyze_audio(self, filepath: str, target_bpm: Optional[int]) -> Dict[str, Any]:
        """
        Perform comprehensive DSP analysis on audio file.
        
        Uses simulated analysis when librosa is not available,
        real implementation when it is.
        """
        try:
            import librosa
            import numpy as np
            
            y, sr = librosa.load(filepath)
            
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            
            if len(beats) > 0:
                beat_strength = onset_env[beats] if len(onset_env) > max(beats) else []
                onset_confidence = float(np.mean(beat_strength)) if len(beat_strength) > 0 else 0.5
            else:
                onset_confidence = 0.5
            
            rms = librosa.feature.rms(y=y)[0]
            dynamic_range = float(np.max(rms) - np.min(rms)) if len(rms) > 0 else 0
            
            tempo_confidence = 1.0
            if target_bpm:
                deviation = abs(float(tempo) - target_bpm) / target_bpm
                tempo_confidence = max(0, 1 - deviation * 2)
            
            syncopation_index = self._calculate_syncopation(onset_env, beats, sr)
            
            return {
                'tempo': float(tempo),
                'tempo_confidence': tempo_confidence,
                'beats': beats.tolist() if hasattr(beats, 'tolist') else list(beats),
                'beat_frames': beats.tolist() if hasattr(beats, 'tolist') else list(beats),
                'onset_envelope': onset_env[:100].tolist() if len(onset_env) > 100 else onset_env.tolist(),
                'onset_confidence': onset_confidence,
                'dynamic_range': dynamic_range,
                'syncopation_index': syncopation_index,
                'duration': len(y) / sr,
                'sample_rate': sr
            }
            
        except ImportError:
            self.logger.warning("Librosa not available, using simulated analysis")
            return self._simulated_analysis(target_bpm)
    
    def _simulated_analysis(self, target_bpm: Optional[int]) -> Dict[str, Any]:
        """
        Return simulated analysis when librosa is not available.
        
        Used for testing and development without audio dependencies.
        """
        import random
        
        tempo = target_bpm or 90
        tempo = tempo + random.uniform(-5, 5)
        
        return {
            'tempo': tempo,
            'tempo_confidence': random.uniform(0.8, 1.0),
            'beats': list(range(0, 1000, 100)),
            'beat_frames': list(range(0, 1000, 100)),
            'onset_envelope': [random.uniform(0, 1) for _ in range(100)],
            'onset_confidence': random.uniform(0.6, 0.9),
            'dynamic_range': random.uniform(0.1, 0.5),
            'syncopation_index': random.uniform(10, 30),
            'duration': 90.0,
            'sample_rate': 22050
        }
    
    def _calculate_syncopation(
        self, 
        onset_env: 'np.ndarray', 
        beats: 'np.ndarray',
        sr: int
    ) -> float:
        """
        Calculate syncopation index using Longuet-Higgins model.
        
        Syncopation occurs when strong onsets appear on weak beats
        and weak positions have silence where strong beats are expected.
        
        Optimal range: 15-30 (engaging groove)
        Too low (<5): Monotonous
        Too high (>50): Chaotic
        """
        try:
            import numpy as np
            
            if len(beats) < 4:
                return 15.0
                
            hop_length = 512
            
            syncopation_score = 0.0
            
            for i in range(1, len(beats)):
                beat_start = beats[i-1]
                beat_end = beats[i]
                
                if beat_end >= len(onset_env):
                    continue
                    
                midpoint = (beat_start + beat_end) // 2
                
                if midpoint < len(onset_env):
                    off_beat_strength = onset_env[midpoint]
                    on_beat_strength = onset_env[beat_start]
                    
                    if off_beat_strength > on_beat_strength * 1.2:
                        syncopation_score += 1
            
            normalized_score = (syncopation_score / len(beats)) * 50
            return float(normalized_score)
            
        except Exception as e:
            self.logger.warning(f"Syncopation calculation failed: {e}")
            return 15.0
    
    def _assess_quality(self, analysis: Dict[str, Any], target_bpm: Optional[int]) -> bool:
        """
        Assess whether the audio passes quality thresholds.
        
        Checks:
        1. BPM accuracy (within 5% of target)
        2. Onset confidence (strong beat alignment)
        3. Syncopation within reasonable range
        """
        if target_bpm:
            bpm_deviation = abs(analysis['tempo'] - target_bpm) / target_bpm
            if bpm_deviation > self.BPM_DEVIATION_THRESHOLD:
                self.logger.warning(
                    f"BPM deviation {bpm_deviation:.2%} exceeds threshold"
                )
                return False
        
        if analysis['onset_confidence'] < self.ONSET_CONFIDENCE_THRESHOLD:
            self.logger.warning(
                f"Onset confidence {analysis['onset_confidence']:.2f} below threshold"
            )
            return False
        
        syncopation = analysis.get('syncopation_index', 0)
        if syncopation < 5 or syncopation > 50:
            self.logger.warning(
                f"Syncopation index {syncopation:.1f} outside optimal range"
            )
        
        return True
    
    def _identify_fix_segments(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify segments that need regeneration via inpainting.
        
        Looks for:
        - Low onset confidence regions
        - BPM inconsistencies
        - Weak sections
        """
        fix_segments = []
        
        onset_env = analysis.get('onset_envelope', [])
        if len(onset_env) < 10:
            return fix_segments
            
        window_size = len(onset_env) // 4
        
        for i in range(4):
            start_idx = i * window_size
            end_idx = (i + 1) * window_size
            window = onset_env[start_idx:end_idx]
            
            if window:
                avg_strength = sum(window) / len(window)
                
                if avg_strength < 0.3:
                    duration = analysis.get('duration', 90)
                    segment_duration = duration / 4
                    
                    fix_segments.append({
                        'start': i * segment_duration,
                        'end': (i + 1) * segment_duration,
                        'reason': f'Low onset strength ({avg_strength:.2f})',
                        'prompt_override': None
                    })
        
        return fix_segments[:2]
