"""
Mix Engineer Agent - Post-Processing & Mastering.

This agent handles the final audio processing:
- Reference-based mastering (matchering)
- Loudness normalization
- Format conversion
- Export quality control

Reference: Section 3.4 "The Mix Engineer" from framework documentation
"""

from typing import Dict, Any, List, Optional
import os

from ..agents.agent_base import BaseAgent, AgentRole, AgentResult


class MixEngineerAgent(BaseAgent):
    """
    Mix Engineer: Post-processing and mastering.
    
    Ensures the final output is commercially viable:
    - Applies reference-based mastering
    - Normalizes loudness to industry standards
    - Handles format conversion
    - Validates final export quality
    
    Uses matchering library for automated mastering when available.
    """
    
    TARGET_LUFS = -14.0
    REFERENCE_TRACKS = {
        'trap': 'reference_trap.wav',
        'drill': 'reference_drill.wav',
        'boom_bap': 'reference_boombap.wav',
        'pop_rap': 'reference_pop.wav',
        'cloud_rap': 'reference_cloud.wav'
    }
    
    @property
    def role(self) -> AgentRole:
        return AgentRole.MIX_ENGINEER
    
    def _validate_input(self, state: Dict[str, Any]) -> List[str]:
        """Validate input state."""
        errors = []
        
        if not state.get('local_filepath') and not state.get('audio_url'):
            errors.append("Audio file required for mastering")
            
        if not state.get('is_complete') and state.get('fix_segments'):
            errors.append("Cannot master track with pending fix segments")
            
        return errors
    
    def _execute(self, state: Dict[str, Any]) -> AgentResult:
        """
        Execute mastering pipeline.
        
        Steps:
        1. Select reference track based on genre
        2. Apply automated mastering (or simulation)
        3. Normalize loudness
        4. Export final file
        5. Validate export quality
        """
        audio_path = state.get('local_filepath', '')
        
        if not os.path.exists(audio_path):
            return AgentResult.failure_result(
                errors=[f"Audio file not found: {audio_path}"]
            )
        
        plan = state.get('structured_plan', {})
        subgenre = plan.get('subgenre', 'trap')
        
        reference_path = self._get_reference_track(subgenre)
        
        try:
            result = self._apply_mastering(audio_path, reference_path)
        except ImportError:
            result = self._simulated_mastering(audio_path)
        
        quality = self._validate_export(result['output_path'])
        
        return AgentResult.success_result(
            state_updates={
                'mastered_filepath': result['output_path'],
                'reference_track': reference_path,
                'status': 'mastered',
                'is_complete': True
            },
            metadata={
                'mastering_result': result,
                'quality_validation': quality
            }
        )
    
    def _get_reference_track(self, subgenre: str) -> Optional[str]:
        """
        Get the reference track path for the genre.
        
        Returns None if no reference is available.
        """
        reference_dir = './references'
        
        if subgenre in self.REFERENCE_TRACKS:
            ref_path = os.path.join(reference_dir, self.REFERENCE_TRACKS[subgenre])
            if os.path.exists(ref_path):
                return ref_path
        
        default_ref = os.path.join(reference_dir, 'reference_default.wav')
        if os.path.exists(default_ref):
            return default_ref
            
        return None
    
    def _apply_mastering(self, target_path: str, reference_path: Optional[str]) -> Dict[str, Any]:
        """
        Apply automated mastering using matchering.
        
        Falls back to simple normalization if reference unavailable.
        """
        import matchering as mg
        
        os.makedirs('./output/mastered', exist_ok=True)
        output_path = target_path.replace('.ogg', '_mastered.wav')
        output_path = output_path.replace('./output/', './output/mastered/')
        
        if reference_path and os.path.exists(reference_path):
            mg.process(
                target=target_path,
                reference=reference_path,
                results=[
                    mg.pcm16(output_path)
                ]
            )
            
            return {
                'output_path': output_path,
                'method': 'reference_mastering',
                'reference_used': reference_path
            }
        else:
            return self._normalize_audio(target_path)
    
    def _normalize_audio(self, audio_path: str) -> Dict[str, Any]:
        """
        Apply simple loudness normalization.
        
        Used when reference-based mastering is not available.
        """
        os.makedirs('./output/mastered', exist_ok=True)
        output_path = audio_path.replace('.ogg', '_normalized.wav')
        output_path = output_path.replace('./output/', './output/mastered/')
        
        try:
            import librosa
            import numpy as np
            import soundfile as sf
            
            y, sr = librosa.load(audio_path)
            
            current_rms = np.sqrt(np.mean(y**2))
            target_rms = 0.1
            
            if current_rms > 0:
                y = y * (target_rms / current_rms)
            
            y = np.clip(y, -1.0, 1.0)
            
            sf.write(output_path, y, sr)
            
            return {
                'output_path': output_path,
                'method': 'rms_normalization',
                'current_rms': float(current_rms),
                'target_rms': target_rms
            }
            
        except ImportError:
            return self._simulated_mastering(audio_path)
    
    def _simulated_mastering(self, audio_path: str) -> Dict[str, Any]:
        """
        Simulated mastering for development.
        
        Creates a placeholder output file.
        """
        self.logger.warning("Using simulated mastering (audio libraries not available)")
        
        os.makedirs('./output/mastered', exist_ok=True)
        
        base = os.path.basename(audio_path)
        output_path = f'./output/mastered/{base}_mastered.wav'
        
        with open(output_path, 'w') as f:
            f.write(f"# Simulated mastered audio\n# Source: {audio_path}\n")
        
        return {
            'output_path': output_path,
            'method': 'simulated',
            'warning': 'Audio processing libraries not available'
        }
    
    def _validate_export(self, output_path: str) -> Dict[str, Any]:
        """
        Validate the exported file quality.
        
        Checks:
        - File exists and is readable
        - File size is reasonable
        - Basic format validation
        """
        validation = {
            'path': output_path,
            'exists': os.path.exists(output_path),
            'size_bytes': 0,
            'quality_passed': False,
            'issues': []
        }
        
        if not validation['exists']:
            validation['issues'].append("Output file not found")
            return validation
        
        validation['size_bytes'] = os.path.getsize(output_path)
        
        if validation['size_bytes'] < 1000:
            validation['issues'].append("Output file suspiciously small")
        elif validation['size_bytes'] > 100 * 1024 * 1024:
            validation['issues'].append("Output file unusually large")
        else:
            validation['quality_passed'] = True
        
        return validation
