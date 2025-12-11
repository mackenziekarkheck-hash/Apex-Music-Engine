"""
Bars Analyzer Agent - Rhyme Density & Multi-syllabic Chain Analysis.

This agent implements the TRUE Raplyzer protocol for advanced phonetic analysis:
- Phonetic transduction using CMU Pronouncing Dictionary
- Rhyme density calculation with vowel stream matching
- Multi-syllabic chain counting via Longest Common Suffix (LCS)
- Slant rhyme detection using phoneme similarity matrix
- Assonance chain identification

Reference: Section 3.1.2 "The Rhyme Density Check" from framework documentation
"""

from typing import Dict, Any, List, Optional, Tuple, Set
import re

from ..agent_base import AnalysisAgent, AgentRole, AgentResult

try:
    import pronouncing
    PRONOUNCING_AVAILABLE = True
except ImportError:
    PRONOUNCING_AVAILABLE = False

VOWEL_PHONEMES = {'AA', 'AE', 'AH', 'AO', 'AW', 'AY', 'EH', 'ER', 'EY', 
                  'IH', 'IY', 'OW', 'OY', 'UH', 'UW'}

PHONEME_SIMILARITY: Dict[Tuple[str, str], float] = {
    ('AA', 'AH'): 0.8, ('AH', 'AA'): 0.8,
    ('AE', 'EH'): 0.7, ('EH', 'AE'): 0.7,
    ('IH', 'IY'): 0.8, ('IY', 'IH'): 0.8,
    ('UH', 'UW'): 0.8, ('UW', 'UH'): 0.8,
    ('OW', 'AO'): 0.7, ('AO', 'OW'): 0.7,
    ('AY', 'EY'): 0.6, ('EY', 'AY'): 0.6,
    ('AY', 'OY'): 0.5, ('OY', 'AY'): 0.5,
    ('AW', 'OW'): 0.5, ('OW', 'AW'): 0.5,
    ('ER', 'UH'): 0.4, ('UH', 'ER'): 0.4,
}


class PhoneticTransducer:
    """
    Phonetic transducer using CMU Pronouncing Dictionary.
    
    Converts words to phoneme sequences and extracts vowel streams
    for rhyme analysis per the Raplyzer protocol.
    """
    
    _cache: Dict[str, List[str]] = {}
    _vowel_cache: Dict[str, List[str]] = {}
    
    @classmethod
    def word_to_phonemes(cls, word: str) -> List[str]:
        """
        Convert a word to its phoneme sequence using CMU Dictionary.
        
        Returns empty list if word not found in dictionary.
        Caches results for performance.
        """
        word_lower = word.lower().strip()
        
        if word_lower in cls._cache:
            return cls._cache[word_lower]
        
        if not PRONOUNCING_AVAILABLE:
            cls._cache[word_lower] = []
            return []
        
        phones = pronouncing.phones_for_word(word_lower)
        
        if phones:
            phoneme_list = phones[0].split()
            phoneme_list = [p.rstrip('012') for p in phoneme_list]
            cls._cache[word_lower] = phoneme_list
            return phoneme_list
        
        cls._cache[word_lower] = []
        return []
    
    @classmethod
    def extract_vowel_stream(cls, word: str) -> List[str]:
        """
        Extract the vowel phonemes from a word.
        
        Example: "CAT" → ['K', 'AE', 'T'] → ['AE']
        """
        word_lower = word.lower().strip()
        
        if word_lower in cls._vowel_cache:
            return cls._vowel_cache[word_lower]
        
        phonemes = cls.word_to_phonemes(word_lower)
        vowels = [p for p in phonemes if p in VOWEL_PHONEMES]
        
        cls._vowel_cache[word_lower] = vowels
        return vowels
    
    @classmethod
    def get_rhyme_phonemes(cls, word: str) -> List[str]:
        """
        Get the phonemes from the last stressed vowel to end of word.
        
        This is the "rhyme part" used for perfect rhyme matching.
        """
        word_lower = word.lower().strip()
        
        if not PRONOUNCING_AVAILABLE:
            return []
        
        phones = pronouncing.phones_for_word(word_lower)
        if not phones:
            return []
        
        phoneme_list = phones[0].split()
        
        last_vowel_idx = -1
        for i in range(len(phoneme_list) - 1, -1, -1):
            base_phoneme = phoneme_list[i].rstrip('012')
            if base_phoneme in VOWEL_PHONEMES:
                last_vowel_idx = i
                break
        
        if last_vowel_idx >= 0:
            return [p.rstrip('012') for p in phoneme_list[last_vowel_idx:]]
        
        return []
    
    @classmethod
    def clear_cache(cls):
        """Clear the phoneme caches."""
        cls._cache.clear()
        cls._vowel_cache.clear()


class BarsAnalyzer(AnalysisAgent):
    """
    Bars Analyzer: Advanced rhyme density and phonetic analysis.
    
    Implements the TRUE Raplyzer algorithm using CMU Pronouncing Dictionary:
    - Perfect rhymes: exact vowel+consonant matches from stressed vowel
    - Slant rhymes: similar phonemes using similarity matrix
    - Multi-syllabic rhymes: multiple matching syllables
    - Assonance chains: repeating vowel patterns across lines
    
    The Rhyme Factor (RF) metric:
    RF = Σ(Length(LCS_i)) / N
    Where N is total word count and LCS is longest common suffix of vowels
    RF > 1.0 indicates elite lyricism (every word in a rhyme chain)
    RF > 0.4 indicates lyrical rap
    RF > 0.2 indicates vibe rap
    """
    
    LOOKBACK_WINDOW = 15
    PERFECT_RHYME_THRESHOLD = 0.95
    SLANT_RHYME_THRESHOLD = 0.6
    
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
        2. Phonetic transduction (text to phonemes via CMU Dictionary)
        3. Vowel stream extraction per word
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
        
        rhyme_analysis = self._analyze_rhyme_patterns_phonetic(words)
        assonance_chains = self._detect_assonance_chains_phonetic(lyrics)
        multis = rhyme_analysis['multisyllabic_count']
        
        rhyme_factor = rhyme_analysis['rhyme_factor']
        
        word_coverage_pct = (rhyme_analysis['words_in_rhymes'] / len(words)) * 100 if words else 0
        
        metrics_update = {
            'rhyme_factor': rhyme_factor,
            'multisyllabic_rhymes': multis,
            'assonance_chains': assonance_chains,
            'perfect_rhymes': rhyme_analysis['perfect_rhymes'],
            'slant_rhymes': rhyme_analysis['slant_rhymes'],
            'word_coverage_pct': word_coverage_pct,
            'phonetic_mode': PRONOUNCING_AVAILABLE,
        }
        
        if 'lyrical_metrics' in state:
            updated_metrics = {**state['lyrical_metrics'], **metrics_update}
        else:
            updated_metrics = metrics_update
        
        quality_passed = self._check_quality(rhyme_factor, multis)
        
        quality_tier = self._determine_quality_tier(rhyme_factor)
        
        return AgentResult.success_result(
            state_updates={
                'lyrical_metrics': updated_metrics,
            },
            metadata={
                'rhyme_analysis': rhyme_analysis,
                'assonance_chains': assonance_chains,
                'quality_passed': quality_passed,
                'quality_tier': quality_tier,
                'using_cmu_dictionary': PRONOUNCING_AVAILABLE
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
    
    def _analyze_rhyme_patterns_phonetic(self, words: List[str]) -> Dict[str, Any]:
        """
        Analyze rhyme patterns using TRUE phonetic analysis.
        
        Algorithm:
        1. For each word w_i, extract vowel stream using CMU Dictionary
        2. Look back up to LOOKBACK_WINDOW words (k=15-20)
        3. Find best rhyme match using vowel stream LCS
        4. Score: RF = Σ(Length(LCS_i)) / N
        """
        analysis = {
            'total_lcs_score': 0,
            'rhyme_pairs': [],
            'perfect_rhymes': 0,
            'slant_rhymes': 0,
            'multisyllabic_count': 0,
            'words_in_rhymes': 0,
            'rhyme_factor': 0.0
        }
        
        words_in_rhyme_chain: Set[int] = set()
        
        for i, word in enumerate(words):
            if i == 0:
                continue
            
            best_match = None
            best_score = 0
            best_lcs_length = 0
            is_perfect = False
            is_multi = False
            
            start_idx = max(0, i - self.LOOKBACK_WINDOW)
            
            for j in range(start_idx, i):
                score, lcs_length, perfect, multi = self._calculate_phonetic_rhyme_score(
                    words[j], word
                )
                
                if score > best_score:
                    best_score = score
                    best_match = (j, words[j])
                    best_lcs_length = lcs_length
                    is_perfect = perfect
                    is_multi = multi
            
            if best_match and best_score >= self.SLANT_RHYME_THRESHOLD:
                analysis['total_lcs_score'] += best_lcs_length
                
                words_in_rhyme_chain.add(i)
                words_in_rhyme_chain.add(best_match[0])
                
                analysis['rhyme_pairs'].append({
                    'word1': best_match[1],
                    'word2': word,
                    'score': best_score,
                    'lcs_length': best_lcs_length,
                    'is_perfect': is_perfect,
                    'is_multisyllabic': is_multi
                })
                
                if is_perfect:
                    analysis['perfect_rhymes'] += 1
                else:
                    analysis['slant_rhymes'] += 1
                
                if is_multi:
                    analysis['multisyllabic_count'] += 1
        
        analysis['words_in_rhymes'] = len(words_in_rhyme_chain)
        analysis['rhyme_factor'] = analysis['total_lcs_score'] / len(words) if words else 0
        
        return analysis
    
    def _calculate_phonetic_rhyme_score(
        self, 
        word1: str, 
        word2: str
    ) -> Tuple[float, int, bool, bool]:
        """
        Calculate rhyme score between two words using phonetic analysis.
        
        Returns:
        - score: 0.0 to 1.0 rhyme strength
        - lcs_length: length of longest common suffix
        - is_perfect: True if perfect rhyme
        - is_multisyllabic: True if 2+ syllables match
        """
        if word1.lower() == word2.lower():
            return 0.0, 0, False, False
        
        if PRONOUNCING_AVAILABLE:
            return self._phonetic_rhyme_score(word1, word2)
        else:
            return self._fallback_rhyme_score(word1, word2)
    
    def _phonetic_rhyme_score(
        self, 
        word1: str, 
        word2: str
    ) -> Tuple[float, int, bool, bool]:
        """
        Calculate rhyme score using CMU Pronouncing Dictionary.
        
        Uses vowel stream matching and phoneme similarity matrix.
        """
        rhyme1 = PhoneticTransducer.get_rhyme_phonemes(word1)
        rhyme2 = PhoneticTransducer.get_rhyme_phonemes(word2)
        
        if not rhyme1 or not rhyme2:
            return self._fallback_rhyme_score(word1, word2)
        
        if rhyme1 == rhyme2:
            vowel_count = sum(1 for p in rhyme1 if p in VOWEL_PHONEMES)
            is_multi = vowel_count >= 2
            return 1.0, len(rhyme1), True, is_multi
        
        lcs_length = self._longest_common_suffix_phonemes(rhyme1, rhyme2)
        
        if lcs_length > 0:
            vowels_in_lcs = 0
            for i in range(1, lcs_length + 1):
                if rhyme1[-i] in VOWEL_PHONEMES:
                    vowels_in_lcs += 1
            
            base_score = lcs_length / max(len(rhyme1), len(rhyme2))
            score = min(1.0, base_score + 0.2)
            is_multi = vowels_in_lcs >= 2
            return score, lcs_length, score >= self.PERFECT_RHYME_THRESHOLD, is_multi
        
        similarity = self._calculate_vowel_similarity(word1, word2)
        if similarity >= self.SLANT_RHYME_THRESHOLD:
            vowels1 = PhoneticTransducer.extract_vowel_stream(word1)
            return similarity, 1, False, len(vowels1) >= 2
        
        return 0.0, 0, False, False
    
    def _longest_common_suffix_phonemes(
        self, 
        phonemes1: List[str], 
        phonemes2: List[str]
    ) -> int:
        """
        Find the longest common suffix between two phoneme lists.
        
        This is the core of the LCS rhyme matching algorithm.
        """
        lcs = 0
        min_len = min(len(phonemes1), len(phonemes2))
        
        for i in range(1, min_len + 1):
            if phonemes1[-i] == phonemes2[-i]:
                lcs += 1
            else:
                break
        
        return lcs
    
    def _calculate_vowel_similarity(self, word1: str, word2: str) -> float:
        """
        Calculate similarity between vowel streams using phoneme similarity matrix.
        
        Used for detecting slant rhymes where exact matches fail.
        """
        vowels1 = PhoneticTransducer.extract_vowel_stream(word1)
        vowels2 = PhoneticTransducer.extract_vowel_stream(word2)
        
        if not vowels1 or not vowels2:
            return 0.0
        
        if vowels1[-1] == vowels2[-1]:
            return 0.8
        
        pair = (vowels1[-1], vowels2[-1])
        similarity = PHONEME_SIMILARITY.get(pair, 0.0)
        
        if similarity > 0:
            return similarity
        
        matches = 0
        min_len = min(len(vowels1), len(vowels2))
        for i in range(1, min_len + 1):
            if vowels1[-i] == vowels2[-i]:
                matches += 1
            else:
                pair = (vowels1[-i], vowels2[-i])
                matches += PHONEME_SIMILARITY.get(pair, 0.0)
        
        return matches / max(len(vowels1), len(vowels2))
    
    def _fallback_rhyme_score(
        self, 
        word1: str, 
        word2: str
    ) -> Tuple[float, int, bool, bool]:
        """
        Fallback rhyme scoring when CMU Dictionary is unavailable.
        
        Uses character-based suffix matching as approximation.
        """
        ending1 = self._get_word_ending(word1, 4)
        ending2 = self._get_word_ending(word2, 4)
        
        if ending1 == ending2 and len(ending1) >= 3:
            return 0.9, 3, True, True
        
        ending1_short = self._get_word_ending(word1, 3)
        ending2_short = self._get_word_ending(word2, 3)
        
        if ending1_short == ending2_short and len(ending1_short) >= 2:
            return 0.8, 2, True, False
        
        if self._get_word_ending(word1, 2) == self._get_word_ending(word2, 2):
            return 0.6, 1, False, False
        
        if self._vowels_match_fallback(word1, word2):
            return 0.4, 1, False, False
        
        return 0.0, 0, False, False
    
    def _get_word_ending(self, word: str, length: int) -> str:
        """Get the ending characters of a word."""
        return word[-length:] if len(word) >= length else word
    
    def _vowels_match_fallback(self, word1: str, word2: str) -> bool:
        """Check if the vowel pattern in endings match (slant rhyme fallback)."""
        vowels = 'aeiou'
        
        v1 = ''.join(c for c in word1[-3:] if c in vowels)
        v2 = ''.join(c for c in word2[-3:] if c in vowels)
        
        return v1 == v2 and len(v1) >= 1
    
    def _detect_assonance_chains_phonetic(self, lyrics: str) -> List[List[str]]:
        """
        Detect chains of words with matching vowel phonemes.
        
        Uses CMU Dictionary for accurate vowel extraction.
        Assonance creates internal rhythm and is characteristic
        of advanced rap techniques.
        """
        chains = []
        lines = self._extract_content_lines(lyrics)
        
        for line in lines:
            words = re.findall(r'\b[a-zA-Z]+\b', line.lower())
            if len(words) < 3:
                continue
            
            vowel_patterns: Dict[str, List[str]] = {}
            
            for word in words:
                if PRONOUNCING_AVAILABLE:
                    vowels = PhoneticTransducer.extract_vowel_stream(word)
                    if vowels:
                        pattern = '-'.join(vowels)
                    else:
                        pattern = self._extract_vowel_pattern_fallback(word)
                else:
                    pattern = self._extract_vowel_pattern_fallback(word)
                
                if pattern:
                    if pattern not in vowel_patterns:
                        vowel_patterns[pattern] = []
                    vowel_patterns[pattern].append(word)
            
            for pattern, matching_words in vowel_patterns.items():
                if len(matching_words) >= 3:
                    chains.append(matching_words)
        
        return chains
    
    def _extract_vowel_pattern_fallback(self, word: str) -> str:
        """Extract the vowel pattern from a word (fallback method)."""
        vowels = 'aeiou'
        pattern = ''.join(c for c in word if c in vowels)
        return pattern if len(pattern) >= 2 else ''
    
    def _check_quality(self, rhyme_factor: float, multis: int) -> bool:
        """Check if the bars meet quality thresholds."""
        rf_threshold = self.thresholds.get('rhyme_factor_min', 0.2)
        
        if rhyme_factor < rf_threshold:
            self.logger.warning(
                f"Rhyme factor {rhyme_factor:.2f} below threshold {rf_threshold}"
            )
            return False
        
        return True
    
    def _determine_quality_tier(self, rhyme_factor: float) -> str:
        """
        Determine the quality tier based on rhyme factor.
        
        RF > 1.0 = Elite lyricism (every word in a rhyme chain)
        RF > 0.4 = Lyrical rap
        RF > 0.2 = Vibe rap
        RF <= 0.2 = Substandard
        """
        if rhyme_factor > 1.0:
            return "elite"
        elif rhyme_factor > 0.4:
            return "lyrical"
        elif rhyme_factor > 0.2:
            return "vibe"
        else:
            return "substandard"
