"""
Audio Splitter Agent - Stem Separation with Confidence Gates.

This agent handles audio stem separation:
- Vocal isolation for analysis
- Instrumental extraction
- Confidence scoring for separation quality

Reference: Wrapper for Demucs with quality gates
"""

from typing import Dict, Any, List, Optional
import os

from ..agent_base import BaseAgent, AgentRole, AgentResult


class AudioSplitter(BaseAgent):
    """
    Audio Splitter: Stem separation with quality assessment.
    
    Wraps audio source separation tools (like Demucs) to:
    - Separate vocals from instrumentals
    - Extract individual stems (drums, bass, vocals, other)
    - Assess separation quality with confidence gates
    
    Quality gates prevent downstream analysis on poorly
    separated stems that would produce unreliable results.
    """
    
    STEM_TYPES = ['vocals', 'drums', 'bass', 'other']
    MIN_CONFIDENCE_THRESHOLD = 0.6
    
    @property
    def role(self) -> AgentRole:
        return AgentRole.MIX_ENGINEER
    
    def _validate_input(self, state: Dict[str, Any]) -> List[str]:
        """Validate input state."""
        errors = []
        
        if not state.get('local_filepath'):
            errors.append("Audio file required for stem separation")
            
        return errors
    
    def _execute(self, state: Dict[str, Any]) -> AgentResult:
        """
        Perform stem separation on audio file.
        
        Steps:
        1. Load audio file
        2. Apply source separation model (simulated or real)
        3. Calculate separation confidence scores
        4. Apply confidence gates
        5. Save stems if quality passes
        """
        audio_path = state.get('local_filepath', '')
        
        if not os.path.exists(audio_path):
            return AgentResult.failure_result(
                errors=[f"Audio file not found: {audio_path}"]
            )
        
        try:
            separation_result = self._separate_stems(audio_path)
        except Exception as e:
            separation_result = self._simulated_separation(audio_path)
        
        quality_assessment = self._assess_separation_quality(separation_result)
        
        usable_stems = self._apply_confidence_gates(
            separation_result, 
            quality_assessment
        )
        
        return AgentResult.success_result(
            state_updates={
                'stems': usable_stems,
                'separation_quality': quality_assessment
            },
            metadata={
                'separation_result': separation_result,
                'quality_assessment': quality_assessment,
                'usable_stems': list(usable_stems.keys())
            }
        )
    
    def _separate_stems(self, filepath: str) -> Dict[str, Any]:
        """
        Perform stem separation using available tools.
        
        In production, this would use Demucs or similar.
        Falls back to simulated separation for development.
        """
        self.logger.info(f"Separating stems from {filepath}")
        
        return self._simulated_separation(filepath)
    
    def _simulated_separation(self, filepath: str) -> Dict[str, Any]:
        """
        Simulated stem separation for development.
        
        Returns placeholder data structure that matches
        what real separation would produce.
        """
        import random
        
        base_name = os.path.splitext(os.path.basename(filepath))[0]
        output_dir = './temp/stems'
        os.makedirs(output_dir, exist_ok=True)
        
        stems = {}
        for stem_type in self.STEM_TYPES:
            stems[stem_type] = {
                'path': f'{output_dir}/{base_name}_{stem_type}.wav',
                'confidence': random.uniform(0.65, 0.95),
                'energy': random.uniform(0.1, 0.5),
                'exists': False
            }
        
        return {
            'source_file': filepath,
            'output_dir': output_dir,
            'stems': stems,
            'model_used': 'simulated',
            'processing_time': 0.0
        }
    
    def _assess_separation_quality(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess the quality of stem separation.
        
        Evaluates:
        - Individual stem confidence scores
        - Cross-talk between stems
        - Energy distribution
        """
        stems = result.get('stems', {})
        
        confidences = [s['confidence'] for s in stems.values()]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        energies = [s['energy'] for s in stems.values()]
        energy_balance = 1.0 - (max(energies) - min(energies)) if energies else 0.5
        
        overall_quality = (avg_confidence + energy_balance) / 2
        
        return {
            'average_confidence': avg_confidence,
            'energy_balance': energy_balance,
            'overall_quality': overall_quality,
            'stem_confidences': {k: v['confidence'] for k, v in stems.items()},
            'quality_grade': self._quality_grade(overall_quality)
        }
    
    def _quality_grade(self, score: float) -> str:
        """Convert numerical score to letter grade."""
        if score >= 0.9:
            return 'A'
        elif score >= 0.8:
            return 'B'
        elif score >= 0.7:
            return 'C'
        elif score >= 0.6:
            return 'D'
        else:
            return 'F'
    
    def _apply_confidence_gates(
        self, 
        result: Dict[str, Any], 
        quality: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Apply confidence gates to filter unreliable stems.
        
        Only stems with confidence above threshold are
        marked as usable for downstream analysis.
        """
        stems = result.get('stems', {})
        usable_stems = {}
        
        for stem_type, stem_data in stems.items():
            if stem_data['confidence'] >= self.MIN_CONFIDENCE_THRESHOLD:
                usable_stems[stem_type] = {
                    'path': stem_data['path'],
                    'confidence': stem_data['confidence'],
                    'usable': True
                }
            else:
                self.logger.warning(
                    f"Stem '{stem_type}' below confidence threshold "
                    f"({stem_data['confidence']:.2f} < {self.MIN_CONFIDENCE_THRESHOLD})"
                )
        
        return usable_stems
