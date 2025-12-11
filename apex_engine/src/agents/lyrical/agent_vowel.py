"""
Vowel Analyzer Agent - Assonance Heatmaps & Vowel Entropy.

This agent focuses on vowel-based analysis for:
- Assonance pattern detection
- Vowel entropy (earworm detection)
- Melodic flow indicators
- Phonetic euphony scoring

Reference: Raplyzer vowel isolation algorithm from framework documentation
"""

from typing import Dict, Any, List, Optional, Tuple
import re
from collections import Counter
import math

from ..agent_base import AnalysisAgent, AgentRole, AgentResult


class VowelAnalyzer(AnalysisAgent):
    """
    Vowel Analyzer: Assonance and phonetic euphony analysis.
    
    The Raplyzer algorithm posits that rap flow is primarily 
    driven by vowels. This agent:
    
    1. Extracts vowel streams from lyrics
    2. Calculates vowel entropy (predictability)
    3. Detects assonance chains and patterns
    4. Measures phonetic "catchiness" (earworm potential)
    
    Low entropy = predictable, catchy patterns (hooks)
    High entropy = complex, varied patterns (verses)
    """
    
    VOWELS = 'aeiou'
    VOWEL_FAMILIES = {
        'front': ['i', 'e'],
        'central': ['a'],
        'back': ['o', 'u'],
        'high': ['i', 'u'],
        'low': ['a', 'e', 'o']
    }
    
    @property
    def role(self) -> AgentRole:
        return AgentRole.RHYME_ANALYZER
    
    def _validate_input(self, state: Dict[str, Any]) -> List[str]:
        """Validate input state."""
        errors = []
        
        lyrics = state.get('lyrics_validated') or state.get('lyrics_draft')
        if not lyrics:
            errors.append("Lyrics are required for vowel analysis")
            
        return errors
    
    def _execute(self, state: Dict[str, Any]) -> AgentResult:
        """
        Perform vowel-based phonetic analysis.
        
        Steps:
        1. Extract vowel streams from each line
        2. Build vowel frequency heatmap
        3. Calculate vowel entropy
        4. Detect assonance patterns
        5. Compute earworm score
        """
        lyrics = state.get('lyrics_validated') or state.get('lyrics_draft', '')
        
        lines = self._extract_content_lines(lyrics)
        
        vowel_streams = self._extract_vowel_streams(lines)
        
        heatmap = self._build_vowel_heatmap(vowel_streams)
        
        entropy = self._calculate_vowel_entropy(vowel_streams)
        
        assonance_patterns = self._detect_assonance_patterns(vowel_streams)
        
        earworm_score = self._calculate_earworm_score(entropy, assonance_patterns)
        
        euphony_score = self._calculate_euphony(vowel_streams)
        
        metrics_update = {
            'vowel_entropy': entropy,
            'earworm_score': earworm_score,
            'euphony_score': euphony_score,
            'assonance_patterns': len(assonance_patterns)
        }
        
        existing_metrics = state.get('lyrical_metrics', {})
        updated_metrics = {**existing_metrics, **metrics_update}
        
        return AgentResult.success_result(
            state_updates={
                'lyrical_metrics': updated_metrics
            },
            metadata={
                'vowel_streams': vowel_streams,
                'heatmap': heatmap,
                'entropy': entropy,
                'assonance_patterns': assonance_patterns,
                'earworm_score': earworm_score,
                'euphony_score': euphony_score
            }
        )
    
    def _extract_content_lines(self, lyrics: str) -> List[str]:
        """Extract content lines from lyrics."""
        lines = []
        for line in lyrics.split('\n'):
            line = line.strip()
            if line and not line.startswith('[') and not line.startswith('('):
                lines.append(line)
        return lines
    
    def _extract_vowel_streams(self, lines: List[str]) -> List[str]:
        """
        Extract vowel streams from each line.
        
        Example:
        "My vision is clear" -> "iiiea"
        """
        streams = []
        
        for line in lines:
            text = line.lower()
            vowel_stream = ''.join(c for c in text if c in self.VOWELS)
            streams.append(vowel_stream)
            
        return streams
    
    def _build_vowel_heatmap(self, streams: List[str]) -> Dict[str, List[int]]:
        """
        Build a heatmap of vowel occurrences per line.
        
        Returns a dictionary mapping each vowel to its
        occurrence count in each line.
        """
        heatmap = {v: [] for v in self.VOWELS}
        
        for stream in streams:
            counts = Counter(stream)
            for vowel in self.VOWELS:
                heatmap[vowel].append(counts.get(vowel, 0))
                
        return heatmap
    
    def _calculate_vowel_entropy(self, streams: List[str]) -> float:
        """
        Calculate Shannon entropy of vowel distribution.
        
        Lower entropy = more predictable = potentially catchier
        Higher entropy = more varied = more complex
        
        Formula: H = -sum(p(x) * log2(p(x)))
        """
        all_vowels = ''.join(streams)
        if not all_vowels:
            return 0.0
            
        total = len(all_vowels)
        counts = Counter(all_vowels)
        
        entropy = 0.0
        for count in counts.values():
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)
                
        max_entropy = math.log2(len(self.VOWELS))
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
        
        return normalized_entropy
    
    def _detect_assonance_patterns(self, streams: List[str]) -> List[Dict[str, Any]]:
        """
        Detect repeating vowel patterns across lines.
        
        Assonance patterns indicate:
        - Internal rhyme structures
        - Melodic consistency
        - Phonetic cohesion
        """
        patterns = []
        pattern_length = 3
        
        all_patterns = Counter()
        
        for stream in streams:
            for i in range(len(stream) - pattern_length + 1):
                pattern = stream[i:i + pattern_length]
                all_patterns[pattern] += 1
        
        for pattern, count in all_patterns.most_common():
            if count >= 3:
                patterns.append({
                    'pattern': pattern,
                    'count': count,
                    'type': 'assonance_chain'
                })
                
        return patterns
    
    def _calculate_earworm_score(
        self, 
        entropy: float, 
        patterns: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate "earworm" potential based on vowel patterns.
        
        Earworm characteristics:
        - Moderate entropy (not too simple, not too complex)
        - Strong repeating patterns
        - Vowel consistency within lines
        
        Score 0-1, where higher = more catchy
        """
        optimal_entropy = 0.6
        entropy_factor = 1 - abs(entropy - optimal_entropy) / 0.6
        
        pattern_score = min(1.0, len(patterns) / 5)
        
        pattern_strength = 0
        for p in patterns:
            pattern_strength += p['count']
        pattern_strength_score = min(1.0, pattern_strength / 20)
        
        earworm_score = (
            0.3 * max(0, entropy_factor) +
            0.3 * pattern_score +
            0.4 * pattern_strength_score
        )
        
        return min(1.0, max(0.0, earworm_score))
    
    def _calculate_euphony(self, streams: List[str]) -> float:
        """
        Calculate phonetic euphony (pleasant sound quality).
        
        Based on vowel family transitions:
        - Smooth transitions between similar vowels = euphonic
        - Jarring transitions = cacophonous
        """
        if not streams:
            return 0.5
            
        smooth_transitions = 0
        total_transitions = 0
        
        for stream in streams:
            for i in range(1, len(stream)):
                prev_vowel = stream[i-1]
                curr_vowel = stream[i]
                
                same_family = any(
                    prev_vowel in family and curr_vowel in family
                    for family in self.VOWEL_FAMILIES.values()
                )
                
                if same_family:
                    smooth_transitions += 1
                total_transitions += 1
        
        if total_transitions == 0:
            return 0.5
            
        return smooth_transitions / total_transitions
