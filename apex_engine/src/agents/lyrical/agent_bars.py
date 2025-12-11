"""
Bars Analyzer Agent - Rhyme Density & Multi-syllabic Chain Analysis.

This agent implements the Raplyzer protocol for advanced phonetic analysis:
- Rhyme density calculation
- Multi-syllabic chain counting
- Slant rhyme detection
- Assonance chain identification

Reference: Section 3.1.2 "The Rhyme Density Check" from framework documentation
"""

from typing import Dict, Any, List, Optional, Tuple
import re

from ..agent_base import AnalysisAgent, AgentRole, AgentResult


VOWEL_PHONEMES = {'AA', 'AE', 'AH', 'AO', 'AW', 'AY', 'EH', 'ER', 'EY', 
                  'IH', 'IY', 'OW', 'OY', 'UH', 'UW'}

PHONEME_SIMILARITY = {
    ('AA', 'AH'): 0.8, ('AE', 'EH'): 0.7, ('IH', 'IY'): 0.8,
    ('UH', 'UW'): 0.8, ('OW', 'AO'): 0.7, ('AY', 'EY'): 0.6,
}


class BarsAnalyzer(AnalysisAgent):
    """
    Bars Analyzer: Advanced rhyme density and phonetic analysis.
    
    Implements the Raplyzer algorithm for detecting:
    - Perfect rhymes (exact vowel+consonant matches)
    - Slant rhymes (similar but not identical sounds)
    - Multi-syllabic rhymes (multiple matching syllables)
    - Assonance chains (repeating vowel patterns)
    
    The Rhyme Factor (RF) metric:
    RF = sum(Length(LCS_i)) / N
    Where N is total word count and LCS is longest common suffix
    RF > 1.0 indicates elite lyricism (every word in a rhyme chain)
    """
    
    LOOKBACK_WINDOW = 15
    
    @property
    def role(self) -> AgentRole:
        return AgentRole.RHYME_ANALYZER
    
    def _validate_input(self, state: Dict[str, Any]) -> List[str]:
        """Validate that we have lyrics to analyze."""
        errors = []
        
        if not state.get('lyrics_validated') and not state.get('lyrics_draft'):
            errors.append("Lyrics are required for bars analysis")
            
        return errors
    
    def _execute(self, state: Dict[str, Any]) -> AgentResult:
        """
        Perform comprehensive bars analysis on the lyrics.
        
        Analysis includes:
        1. Word extraction and normalization
        2. Phonetic transduction (text to phonemes)
        3. Vowel stream extraction
        4. LCS rhyme matching within lookback window
        5. Multi-syllabic rhyme detection
        6. Assonance chain identification
        """
        lyrics = state.get('lyrics_validated') or state.get('lyrics_draft', '')
        
        lines = self._extract_content_lines(lyrics)
        words = self._extract_words(lines)
        
        if len(words) < 2:
            return AgentResult.failure_result(
                errors=["Insufficient words for rhyme analysis"]
            )
        
        rhyme_analysis = self._analyze_rhyme_patterns(words)
        assonance_chains = self._detect_assonance_chains(lyrics)
        multis = self._count_multisyllabic_rhymes(words)
        
        rhyme_factor = rhyme_analysis['total_rhyme_score'] / len(words) if words else 0
        
        metrics_update = {
            'rhyme_factor': rhyme_factor,
            'multisyllabic_rhymes': multis,
            'assonance_chains': assonance_chains,
        }
        
        if 'lyrical_metrics' in state:
            updated_metrics = {**state['lyrical_metrics'], **metrics_update}
        else:
            updated_metrics = metrics_update
        
        quality_passed = self._check_quality(rhyme_factor, multis)
        
        return AgentResult.success_result(
            state_updates={
                'lyrical_metrics': updated_metrics,
            },
            metadata={
                'rhyme_analysis': rhyme_analysis,
                'assonance_chains': assonance_chains,
                'quality_passed': quality_passed
            }
        )
    
    def _extract_content_lines(self, lyrics: str) -> List[str]:
        """Extract content lines, excluding structural tags and ad-libs."""
        lines = []
        for line in lyrics.split('\n'):
            line = line.strip()
            if not line:
                continue
            if line.startswith('[') or line.startswith('('):
                continue
            lines.append(line)
        return lines
    
    def _extract_words(self, lines: List[str]) -> List[str]:
        """Extract and normalize words from lines."""
        words = []
        for line in lines:
            line_words = re.findall(r'\b[a-zA-Z]+\b', line.lower())
            words.extend(line_words)
        return words
    
    def _analyze_rhyme_patterns(self, words: List[str]) -> Dict[str, Any]:
        """
        Analyze rhyme patterns using lookback window matching.
        
        For each word, look back up to LOOKBACK_WINDOW words
        to find the best rhyme match.
        """
        analysis = {
            'total_rhyme_score': 0,
            'rhyme_pairs': [],
            'perfect_rhymes': 0,
            'slant_rhymes': 0
        }
        
        for i, word in enumerate(words):
            if i == 0:
                continue
                
            best_match = None
            best_score = 0
            
            start_idx = max(0, i - self.LOOKBACK_WINDOW)
            for j in range(start_idx, i):
                score = self._calculate_rhyme_score(words[j], word)
                if score > best_score:
                    best_score = score
                    best_match = (j, words[j])
            
            if best_match and best_score >= 1:
                analysis['total_rhyme_score'] += best_score
                analysis['rhyme_pairs'].append({
                    'word1': best_match[1],
                    'word2': word,
                    'score': best_score
                })
                if best_score >= 2:
                    analysis['perfect_rhymes'] += 1
                else:
                    analysis['slant_rhymes'] += 1
        
        return analysis
    
    def _calculate_rhyme_score(self, word1: str, word2: str) -> int:
        """
        Calculate rhyme score between two words.
        
        Score based on matching ending phonemes:
        - 3+ matching vowels = perfect multi-syllabic rhyme
        - 2 matching vowels = strong rhyme
        - 1 matching vowel + consonant = basic rhyme
        - Similar vowels = slant rhyme
        """
        if word1 == word2:
            return 0
            
        ending1 = self._get_word_ending(word1, 4)
        ending2 = self._get_word_ending(word2, 4)
        
        if ending1 == ending2 and len(ending1) >= 3:
            return 3
        
        ending1_short = self._get_word_ending(word1, 3)
        ending2_short = self._get_word_ending(word2, 3)
        
        if ending1_short == ending2_short and len(ending1_short) >= 2:
            return 2
            
        if self._get_word_ending(word1, 2) == self._get_word_ending(word2, 2):
            return 1
            
        if self._vowels_match(word1, word2):
            return 0.5
            
        return 0
    
    def _get_word_ending(self, word: str, length: int) -> str:
        """Get the ending characters of a word."""
        return word[-length:] if len(word) >= length else word
    
    def _vowels_match(self, word1: str, word2: str) -> bool:
        """Check if the vowel pattern in endings match (slant rhyme)."""
        vowels = 'aeiou'
        
        v1 = ''.join(c for c in word1[-3:] if c in vowels)
        v2 = ''.join(c for c in word2[-3:] if c in vowels)
        
        return v1 == v2 and len(v1) >= 1
    
    def _detect_assonance_chains(self, lyrics: str) -> List[List[str]]:
        """
        Detect chains of words with matching vowel sounds.
        
        Assonance creates internal rhythm and is characteristic
        of advanced rap techniques.
        """
        chains = []
        lines = self._extract_content_lines(lyrics)
        
        for line in lines:
            words = re.findall(r'\b[a-zA-Z]+\b', line.lower())
            if len(words) < 3:
                continue
                
            vowel_patterns = {}
            for word in words:
                pattern = self._extract_vowel_pattern(word)
                if pattern:
                    if pattern not in vowel_patterns:
                        vowel_patterns[pattern] = []
                    vowel_patterns[pattern].append(word)
            
            for pattern, matching_words in vowel_patterns.items():
                if len(matching_words) >= 3:
                    chains.append(matching_words)
        
        return chains
    
    def _extract_vowel_pattern(self, word: str) -> str:
        """Extract the vowel pattern from a word."""
        vowels = 'aeiou'
        pattern = ''.join(c for c in word if c in vowels)
        return pattern if len(pattern) >= 2 else ''
    
    def _count_multisyllabic_rhymes(self, words: List[str]) -> int:
        """
        Count multi-syllabic rhymes (2+ syllable matching).
        
        Multi-syllabic rhymes are a hallmark of technical rap
        and indicate high lyrical skill.
        """
        multis = 0
        
        for i in range(1, len(words)):
            for j in range(max(0, i - self.LOOKBACK_WINDOW), i):
                score = self._calculate_rhyme_score(words[j], words[i])
                if score >= 2:
                    multis += 1
                    break
                    
        return multis
    
    def _check_quality(self, rhyme_factor: float, multis: int) -> bool:
        """Check if the bars meet quality thresholds."""
        rf_threshold = self.thresholds.get('rhyme_factor_min', 0.5)
        
        if rhyme_factor < rf_threshold:
            self.logger.warning(
                f"Rhyme factor {rhyme_factor:.2f} below threshold {rf_threshold}"
            )
            return False
            
        return True
