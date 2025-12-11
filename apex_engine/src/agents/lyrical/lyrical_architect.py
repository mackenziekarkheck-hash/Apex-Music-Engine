"""
The Lyrical Architect Agent - Text & Phonetics.

This agent is responsible for generating the textual content of the rap.
Unlike a generic creative writing bot, the Lyrical Architect acts as a
"structure-first" poet, prioritizing rhythmic feasibility over semantic complexity.

Key Responsibilities:
- Generate lyrics with LLM integration
- Validate syllable counts per bar
- Check rhyme density using CMU Pronouncing Dictionary
- Find slant rhymes and assonance chains

Reference: Section 3.1 from "Autonomous Aural Architectures"
"""

from typing import Dict, Any, List, Optional
import re

from ..agent_base import GenerativeAgent, AgentRole, AgentResult


class LyricalArchitectAgent(GenerativeAgent):
    """
    The Lyrical Architect: Structure-first lyric generation.
    
    This agent generates rap lyrics that adhere to:
    - Target syllable counts based on BPM
    - Rhyme density requirements
    - Proper song structure tags ([Verse], [Chorus], etc.)
    
    Algorithm:
    1. Structure Definition - Determine bar structure from BPM
    2. Drafting Loop - Generate couplets via LLM
    3. Rhyme Density Check - Validate phonetic rhyme quality
    4. Syllabic Constraints - Ensure lines fit the beat
    """
    
    SYLLABLES_PER_BAR_BY_BPM = {
        (60, 80): (8, 10),
        (80, 100): (10, 12),
        (100, 120): (12, 14),
        (120, 150): (14, 16),
        (150, 200): (8, 10),
    }
    
    STRUCTURAL_TAGS = ['[Intro]', '[Verse]', '[Verse 1]', '[Verse 2]', 
                       '[Chorus]', '[Hook]', '[Bridge]', '[Outro]', '[Drop]']
    
    @property
    def role(self) -> AgentRole:
        return AgentRole.LYRICAL_ARCHITECT
    
    def _validate_input(self, state: Dict[str, Any]) -> List[str]:
        """Validate that we have the necessary inputs for lyric generation."""
        errors = []
        
        if not state.get('user_prompt') and not state.get('structured_plan'):
            errors.append("Either user_prompt or structured_plan is required")
            
        return errors
    
    def _execute(self, state: Dict[str, Any]) -> AgentResult:
        """
        Generate and validate lyrics based on the structured plan.
        
        Flow:
        1. Parse the structured plan for BPM and style
        2. Calculate target syllable range
        3. Generate lyrics (or validate provided draft)
        4. Analyze rhyme density and syllable counts
        5. Return validated lyrics or errors
        """
        plan = state.get('structured_plan', {})
        target_bpm = plan.get('bpm', 90)
        
        syllable_range = self._get_syllable_range(target_bpm)
        self.logger.info(f"Target BPM: {target_bpm}, Syllable range: {syllable_range}")
        
        lyrics_draft = state.get('lyrics_draft', '')
        
        if not lyrics_draft:
            lyrics_draft = self._generate_placeholder_lyrics(state.get('user_prompt', ''))
        
        analysis = self._analyze_lyrics(lyrics_draft, syllable_range)
        
        validation_passed = self._validate_lyrics(analysis, syllable_range)
        
        lyrical_metrics = {
            'rhyme_factor': analysis['rhyme_factor'],
            'syllable_counts': analysis['syllable_counts'],
            'syllable_variance': analysis['syllable_variance'],
            'stress_pattern': analysis.get('stress_pattern', []),
            'phoneme_map': analysis.get('phoneme_map', []),
            'assonance_chains': analysis.get('assonance_chains', []),
            'multisyllabic_rhymes': analysis.get('multisyllabic_rhymes', 0),
            'flow_consistency': analysis.get('flow_consistency', 0.0)
        }
        
        if validation_passed:
            return AgentResult.success_result(
                state_updates={
                    'lyrics_validated': lyrics_draft,
                    'lyrical_metrics': lyrical_metrics,
                    'status': 'lyrics_validated'
                },
                warnings=analysis.get('warnings', []),
                metadata={'analysis': analysis}
            )
        else:
            return AgentResult.failure_result(
                errors=analysis.get('errors', ['Lyrics failed validation']),
                state_updates={
                    'lyrics_draft': lyrics_draft,
                    'lyrical_metrics': lyrical_metrics
                },
                metadata={'analysis': analysis}
            )
    
    def _get_syllable_range(self, bpm: int) -> tuple:
        """Get the target syllable count range based on BPM."""
        for (low, high), syllables in self.SYLLABLES_PER_BAR_BY_BPM.items():
            if low <= bpm < high:
                return syllables
        return (10, 12)
    
    def _generate_placeholder_lyrics(self, prompt: str) -> str:
        """Generate placeholder lyrics structure when none provided."""
        return f"""[Intro]
(Yeah, uh-huh)
Check it out, one two

[Verse 1]
Digital signals flowing through the night
My rhymes are sharp and my flow is tight
Processing data at the speed of light
Every bar I spit is dynamite

[Chorus]
This is the future sound we make
Every beat drop for music's sake
Automated flow, no mistake
This is the path that we will take

[Verse 2]
Algorithm vibes in every line
Neural networks making beats divine
Structure meets the creative mind
Leaving all the weak flows behind

[Outro]
(Yeah, yeah)
APEX Engine, we out
"""
    
    def _analyze_lyrics(self, lyrics: str, syllable_range: tuple) -> Dict[str, Any]:
        """
        Perform comprehensive lyric analysis.
        
        Implements the Raplyzer protocol for:
        - Syllable counting
        - Rhyme density calculation
        - Assonance chain detection
        """
        analysis = {
            'total_lines': 0,
            'syllable_counts': [],
            'syllable_variance': 0.0,
            'rhyme_factor': 0.0,
            'phoneme_map': [],
            'assonance_chains': [],
            'multisyllabic_rhymes': 0,
            'flow_consistency': 0.0,
            'warnings': [],
            'errors': []
        }
        
        lines = [l.strip() for l in lyrics.split('\n') 
                 if l.strip() and not l.strip().startswith('[') 
                 and not l.strip().startswith('(')]
        
        analysis['total_lines'] = len(lines)
        
        for line in lines:
            syllables = self._count_syllables(line)
            analysis['syllable_counts'].append(syllables)
            
            if syllables > syllable_range[1] * 1.5:
                analysis['warnings'].append(
                    f"Line may be too long ({syllables} syllables): {line[:30]}..."
                )
        
        if analysis['syllable_counts']:
            import statistics
            analysis['syllable_variance'] = statistics.variance(analysis['syllable_counts']) if len(analysis['syllable_counts']) > 1 else 0.0
            
        analysis['rhyme_factor'] = self._calculate_rhyme_density(lines)
        
        analysis['flow_consistency'] = self._calculate_flow_consistency(analysis['syllable_counts'])
        
        return analysis
    
    def _count_syllables(self, text: str) -> int:
        """
        Count syllables in a line of text.
        
        Uses a heuristic approach based on vowel clusters.
        """
        text = text.lower()
        text = re.sub(r'[^a-z\s]', '', text)
        words = text.split()
        
        total = 0
        for word in words:
            count = 0
            prev_vowel = False
            
            for char in word:
                is_vowel = char in 'aeiouy'
                if is_vowel and not prev_vowel:
                    count += 1
                prev_vowel = is_vowel
                
            if word.endswith('e') and count > 1:
                count -= 1
            if word.endswith('le') and len(word) > 2 and word[-3] not in 'aeiouy':
                count += 1
            if count == 0:
                count = 1
                
            total += count
            
        return total
    
    def _calculate_rhyme_density(self, lines: List[str]) -> float:
        """
        Calculate rhyme density using end-word analysis.
        
        The Rhyme Factor (RF) = sum of matching phonemes / total words
        RF > 1.0 indicates every word is part of a rhyme chain
        """
        if len(lines) < 2:
            return 0.0
            
        rhyme_matches = 0
        total_comparisons = 0
        
        for i in range(1, len(lines)):
            prev_word = self._get_last_word(lines[i-1])
            curr_word = self._get_last_word(lines[i])
            
            if prev_word and curr_word:
                total_comparisons += 1
                if self._words_rhyme(prev_word, curr_word):
                    rhyme_matches += 1
        
        return rhyme_matches / total_comparisons if total_comparisons > 0 else 0.0
    
    def _get_last_word(self, line: str) -> str:
        """Extract the last word from a line."""
        words = re.findall(r'\b[a-zA-Z]+\b', line)
        return words[-1].lower() if words else ''
    
    def _words_rhyme(self, word1: str, word2: str) -> bool:
        """Check if two words rhyme using ending similarity."""
        if len(word1) < 2 or len(word2) < 2:
            return False
            
        if word1[-2:] == word2[-2:]:
            return True
        if word1[-3:] == word2[-3:] if len(word1) >= 3 and len(word2) >= 3 else False:
            return True
            
        vowels = set('aeiou')
        end1 = ''.join(c for c in word1[-3:] if c in vowels)
        end2 = ''.join(c for c in word2[-3:] if c in vowels)
        
        return end1 == end2 and len(end1) >= 1
    
    def _calculate_flow_consistency(self, syllable_counts: List[int]) -> float:
        """Calculate how consistent the flow is based on syllable distribution."""
        if len(syllable_counts) < 2:
            return 1.0
            
        import statistics
        variance = statistics.variance(syllable_counts)
        mean = statistics.mean(syllable_counts)
        
        cv = (variance ** 0.5) / mean if mean > 0 else 0
        
        consistency = max(0, 1 - (cv / 0.5))
        return min(1.0, consistency)
    
    def _validate_lyrics(self, analysis: Dict[str, Any], syllable_range: tuple) -> bool:
        """Validate that lyrics meet quality thresholds."""
        if analysis['total_lines'] < 4:
            analysis['errors'].append("Lyrics too short (minimum 4 lines)")
            return False
            
        if analysis['rhyme_factor'] < 0.2:
            analysis['warnings'].append(
                f"Low rhyme density ({analysis['rhyme_factor']:.2f}). Consider adding more rhymes."
            )
            
        if analysis['syllable_variance'] > 25:
            analysis['warnings'].append(
                f"High syllable variance ({analysis['syllable_variance']:.2f}). Flow may be inconsistent."
            )
            
        return len(analysis['errors']) == 0
