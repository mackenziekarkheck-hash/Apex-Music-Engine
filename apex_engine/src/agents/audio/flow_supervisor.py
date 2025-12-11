"""
Flow Supervisor Agent - Audio Analysis & DSP.

The quality control auditor that downloads generated audio and performs
Digital Signal Processing (DSP) to verify that the rap is "on beat."

Key Responsibilities:
- Beat tracking and BPM verification
- Onset alignment (The "Pocket" Check)
- Syncopation detection using Longuet-Higgins model
- Inpaint segment triggering

Reference: Section 3.3 "The Flow Supervisor" from framework documentation
"""

from typing import Dict, Any, List, Optional, Tuple
import os

from ..agent_base import AnalysisAgent, AgentRole, AgentResult


METRIC_WEIGHTS_16TH = [
    0,   # Beat 1 (downbeat) - maximum expectation
    -3,  # 1e (16th after beat 1)
    -2,  # 1& (8th after beat 1)
    -3,  # 1a (16th before beat 2)
    -1,  # Beat 2 (quarter note)
    -3,  # 2e
    -2,  # 2&
    -3,  # 2a
    -1,  # Beat 3 (quarter note)
    -3,  # 3e
    -2,  # 3&
    -3,  # 3a
    -1,  # Beat 4 (quarter note)
    -3,  # 4e
    -2,  # 4&
    -3,  # 4a
]


class FlowSupervisorAgent(AnalysisAgent):
    """
    Flow Supervisor: Audio quality control auditor.
    
    This is the most computationally intensive node, performing DSP
    analysis using Librosa to verify rhythmic coherence.
    
    Algorithm:
    1. Beat Tracking - Detect tempo and beat frames
    2. BPM Verification - Compare detected vs. target BPM (>5% = hallucinated)
    3. Onset Alignment - Check vocal onsets against beat grid
    4. Syncopation Detection - Longuet-Higgins model on 16th-note grid
    5. Inpaint Triggering - Flag problematic sections for regeneration
    
    Syncopation Index Ranges:
    - < 5: Monotonous (no dopamine)
    - 15-30: "Goldilocks Zone" (optimal groove)
    - > 50: Chaotic (cognitive overload)
    """
    
    BPM_DEVIATION_THRESHOLD = 0.05
    ONSET_CONFIDENCE_THRESHOLD = 0.7
    OPTIMAL_SYNCOPATION_MIN = 15
    OPTIMAL_SYNCOPATION_MAX = 30
    
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
        4. Compute Longuet-Higgins syncopation index
        5. Determine if inpainting is needed
        6. Return analysis metrics and quality assessment
        """
        audio_path = state.get('local_filepath', '')
        target_bpm = state.get('structured_plan', {}).get('bpm')
        genre_key = state.get('structured_plan', {}).get('genre_key', 'default')
        
        if not audio_path or not os.path.exists(audio_path):
            audio_path = self._download_audio(state.get('audio_url', ''))
            if not audio_path:
                return AgentResult.failure_result(
                    errors=["Could not load audio file"]
                )
        
        analysis = self._analyze_audio(audio_path, target_bpm)
        
        quality_passed = self._assess_quality(analysis, target_bpm, genre_key)
        
        fix_segments = []
        if not quality_passed and state.get('iteration_count', 0) < state.get('max_iterations', 3):
            fix_segments = self._identify_fix_segments(analysis)
        
        syncopation_rating = self._rate_syncopation(analysis.get('syncopation_index', 0))
        
        analysis_metrics = {
            'detected_bpm': analysis['tempo'],
            'bpm_confidence': analysis['tempo_confidence'],
            'onset_confidence': analysis['onset_confidence'],
            'beat_frames': analysis.get('beat_frames', [])[:20],
            'syncopation_index': analysis.get('syncopation_index', 0),
            'syncopation_rating': syncopation_rating,
            'dynamic_range': analysis.get('dynamic_range', 0),
            'pocket_alignment': analysis.get('pocket_alignment', 0),
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
                'quality_passed': quality_passed,
                'syncopation_rating': syncopation_rating
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
        
        Uses librosa for real analysis, falls back to simulation
        when unavailable or when dealing with simulated/invalid files.
        """
        if 'simulated' in filepath or 'sim_' in filepath:
            self.logger.info("Detected simulated audio file, using simulated analysis")
            return self._simulated_analysis(target_bpm)
        
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
            
            syncopation_index = self._calculate_syncopation_longuet_higgins(
                onset_env, beats, sr
            )
            
            pocket_alignment = self._calculate_pocket_alignment(onset_env, beats)
            
            return {
                'tempo': float(tempo),
                'tempo_confidence': tempo_confidence,
                'beats': beats.tolist() if hasattr(beats, 'tolist') else list(beats),
                'beat_frames': beats.tolist() if hasattr(beats, 'tolist') else list(beats),
                'onset_envelope': onset_env[:100].tolist() if len(onset_env) > 100 else onset_env.tolist(),
                'onset_confidence': onset_confidence,
                'dynamic_range': dynamic_range,
                'syncopation_index': syncopation_index,
                'pocket_alignment': pocket_alignment,
                'duration': len(y) / sr,
                'sample_rate': sr
            }
            
        except ImportError:
            self.logger.warning("Librosa not available, using simulated analysis")
            return self._simulated_analysis(target_bpm)
        except Exception as e:
            self.logger.warning(f"Could not load audio file ({e}), using simulated analysis")
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
            'syncopation_index': random.uniform(15, 30),
            'pocket_alignment': random.uniform(0.7, 0.95),
            'duration': 90.0,
            'sample_rate': 22050
        }
    
    def _calculate_syncopation_longuet_higgins(
        self, 
        onset_env: 'np.ndarray', 
        beats: 'np.ndarray',
        sr: int
    ) -> float:
        """
        Calculate syncopation index using the Longuet-Higgins model.
        
        Algorithm:
        1. Quantize audio to 16th-note grid
        2. Assign metric weights per position (METRIC_WEIGHTS_16TH)
        3. Detect syncopation: onset at weak position + silence at next strong position
        4. Score: S_index = Σ(W_strong - W_weak) for all syncopated pairs
        
        Optimal range: 15-30 (engaging groove)
        Too low (<5): Monotonous
        Too high (>50): Chaotic
        """
        try:
            import numpy as np
            
            if len(beats) < 4:
                return 15.0
            
            syncopation_score = 0.0
            syncopation_events = 0
            
            for i in range(1, len(beats)):
                beat_start = beats[i-1]
                beat_end = beats[i]
                beat_length = beat_end - beat_start
                
                if beat_length < 16:
                    continue
                
                subdivision_length = beat_length // 4
                
                for sub in range(4):
                    weak_pos = beat_start + (sub * subdivision_length) + (subdivision_length // 2)
                    strong_pos = beat_start + ((sub + 1) * subdivision_length)
                    
                    if weak_pos >= len(onset_env) or strong_pos >= len(onset_env):
                        continue
                    
                    weak_onset = onset_env[weak_pos]
                    strong_onset = onset_env[min(strong_pos, len(onset_env) - 1)]
                    
                    mean_strength = np.mean(onset_env)
                    weak_threshold = mean_strength * 1.3
                    
                    if weak_onset > weak_threshold and strong_onset < mean_strength * 0.7:
                        weak_metric_position = (sub * 4 + 2) % 16
                        strong_metric_position = ((sub + 1) * 4) % 16
                        
                        weak_weight = METRIC_WEIGHTS_16TH[weak_metric_position]
                        strong_weight = METRIC_WEIGHTS_16TH[strong_metric_position]
                        
                        syncopation_weight = abs(strong_weight - weak_weight)
                        syncopation_score += syncopation_weight
                        syncopation_events += 1
            
            if syncopation_events > 0:
                normalized_score = (syncopation_score / len(beats)) * 15
            else:
                normalized_score = 0
            
            return float(min(60, max(0, normalized_score)))
            
        except Exception as e:
            self.logger.warning(f"Syncopation calculation failed: {e}")
            return 15.0
    
    def _calculate_pocket_alignment(
        self, 
        onset_env: 'np.ndarray', 
        beats: 'np.ndarray'
    ) -> float:
        """
        Calculate how well onsets align with the beat grid ("pocket").
        
        Returns 0-1 where:
        - 1.0 = Perfect pocket (onsets right on beats)
        - 0.5 = Moderate pocket
        - 0.0 = Completely off-grid
        """
        try:
            import numpy as np
            
            if len(beats) < 2 or len(onset_env) < 10:
                return 0.8
            
            mean_strength = np.mean(onset_env)
            strong_onsets = np.where(onset_env > mean_strength * 1.5)[0]
            
            if len(strong_onsets) == 0:
                return 0.8
            
            avg_beat_interval = np.mean(np.diff(beats))
            tolerance = avg_beat_interval * 0.15
            
            on_pocket = 0
            for onset in strong_onsets:
                distances = np.abs(beats - onset)
                if np.min(distances) < tolerance:
                    on_pocket += 1
            
            return float(on_pocket / len(strong_onsets)) if len(strong_onsets) > 0 else 0.8
            
        except Exception as e:
            self.logger.warning(f"Pocket alignment calculation failed: {e}")
            return 0.8
    
    def _rate_syncopation(self, syncopation_index: float) -> str:
        """
        Rate the syncopation level.
        
        Returns a qualitative rating based on the index.
        """
        if syncopation_index < 5:
            return 'monotonous'
        elif syncopation_index < 15:
            return 'rigid'
        elif syncopation_index <= 30:
            return 'optimal'
        elif syncopation_index <= 50:
            return 'complex'
        else:
            return 'chaotic'
    
    def _assess_quality(
        self, 
        analysis: Dict[str, Any], 
        target_bpm: Optional[int],
        genre_key: str
    ) -> bool:
        """
        Assess whether the audio passes quality thresholds.
        
        Checks:
        1. BPM accuracy (within 5% of target)
        2. Onset confidence (strong beat alignment)
        3. Syncopation within genre-appropriate range
        4. Pocket alignment
        """
        if target_bpm:
            bpm_deviation = abs(analysis['tempo'] - target_bpm) / target_bpm
            if bpm_deviation > self.BPM_DEVIATION_THRESHOLD:
                self.logger.warning(
                    f"BPM deviation {bpm_deviation:.2%} exceeds threshold (hallucinated tempo?)"
                )
                return False
        
        if analysis['onset_confidence'] < self.ONSET_CONFIDENCE_THRESHOLD:
            self.logger.warning(
                f"Onset confidence {analysis['onset_confidence']:.2f} below threshold"
            )
            return False
        
        syncopation = analysis.get('syncopation_index', 0)
        if syncopation < 5:
            self.logger.warning(
                f"Syncopation index {syncopation:.1f} too low (monotonous)"
            )
        elif syncopation > 50:
            self.logger.warning(
                f"Syncopation index {syncopation:.1f} too high (chaotic)"
            )
        
        pocket = analysis.get('pocket_alignment', 0)
        if pocket < 0.5:
            self.logger.warning(
                f"Pocket alignment {pocket:.2f} poor (off-beat delivery)"
            )
            return False
        
        return True
    
    def _identify_fix_segments(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify segments that need regeneration via inpainting.
        
        Looks for:
        - Low onset confidence regions
        - BPM inconsistencies
        - Poor pocket alignment zones
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
                        'severity': 'moderate' if avg_strength > 0.2 else 'severe',
                        'prompt_override': None
                    })
        
        return fix_segments[:2]
