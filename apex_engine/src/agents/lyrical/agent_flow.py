"""
Flow Analyzer Agent - Syllabic Velocity & Rhythmic Dynamics.

This agent analyzes the "flow" of rap lyrics:
- Syllabic velocity (syllables per beat) with BPM-specific constraints
- Plosive Density Index (PDI) for rhythmic punch
- Automatic breath injection for extended phrases
- Stress pattern analysis using phonetic data

Reference: Section 3.2 "Flow Dynamics" from "Neuro-Acoustic Optimization"
"""

from typing import Dict, Any, List, Optional, Tuple
import re

from ..agent_base import AnalysisAgent, AgentRole, AgentResult

try:
    import syllables
    SYLLABLES_AVAILABLE = True
except ImportError:
    SYLLABLES_AVAILABLE = False

try:
    import pronouncing
    PRONOUNCING_AVAILABLE = True
except ImportError:
    PRONOUNCING_AVAILABLE = False

GENRE_SYLLABLE_CONSTRAINTS = {
    'trap': {'bpm_range': (130, 160), 'target_syllables': 14, 'tolerance': 2},
    'boom_bap': {'bpm_range': (85, 95), 'target_syllables': 11, 'tolerance': 2},
    'drill': {'bpm_range': (140, 145), 'target_syllables': 12, 'tolerance': 2},
    'pop_rap': {'bpm_range': (90, 120), 'target_syllables': 10, 'tolerance': 3},
    'cloud_rap': {'bpm_range': (65, 80), 'target_syllables': 8, 'tolerance': 3},
    'default': {'bpm_range': (80, 140), 'target_syllables': 12, 'tolerance': 3}
}

PLOSIVE_CONSONANTS = set('bpdtgk')
FRICATIVE_CONSONANTS = set('fvszh')
NASAL_CONSONANTS = set('mn')

MAX_PHRASE_SYLLABLES = 16
BREATH_TOKEN = '(breath)'


class FlowAnalyzer(AnalysisAgent):
    """
    Flow Analyzer: Rhythmic dynamics and delivery analysis.
    
    "Flow" is the interaction of lyrics with time. This agent
    measures rhythmic consistency and detects flow patterns
    like syncopation, double-time, and triplet flows.
    
    Key Metrics:
    - Syllabic Velocity: syllables per beat (BPM-adjusted)
    - Plosive Density Index (PDI): hard consonant clusters for punch
    - Breath Points: natural and injected pause locations
    - Syllable Variance: flow complexity indicator
    
    Flow Quality Classification:
    - High variance (>5): Broken/experimental flow
    - Low variance (<3): Choppy/rigid flow
    - Moderate variance (3-5): Complex syncopated flow
    """
    
    STRESS_MARKERS = {1: 'PRIMARY', 2: 'SECONDARY', 0: 'UNSTRESSED'}
    
    @property
    def role(self) -> AgentRole:
        return AgentRole.FLOW_SUPERVISOR
    
    def _validate_input(self, state: Dict[str, Any]) -> List[str]:
        """Validate input state."""
        errors = []
        
        lyrics = state.get('lyrics_validated') or state.get('lyrics_draft')
        if not lyrics:
            errors.append("Lyrics are required for flow analysis")
            
        return errors
    
    def _execute(self, state: Dict[str, Any]) -> AgentResult:
        """
        Analyze flow dynamics of the lyrics.
        
        Steps:
        1. Parse lyrics into lines and words
        2. Calculate syllable velocity per line with accurate counting
        3. Compute Plosive Density Index (PDI)
        4. Detect and suggest breath injection points
        5. Analyze syllable variance for flow classification
        6. Build stress maps for each line
        """
        lyrics = state.get('lyrics_validated') or state.get('lyrics_draft', '')
        plan = state.get('structured_plan', {})
        target_bpm = plan.get('bpm', 90)
        genre_key = plan.get('genre_key', 'default')
        
        lines = self._extract_content_lines(lyrics)
        
        flow_analysis = self._analyze_flow(lines, target_bpm, genre_key)
        
        pdi_analysis = self._calculate_plosive_density_index(lines)
        
        breath_analysis = self._analyze_breath_points(lines)
        
        variance_analysis = self._analyze_syllable_variance(flow_analysis['syllables_per_line'])
        
        stress_analysis = self._analyze_stress_patterns(lines)
        
        syllable_velocity = self._calculate_syllable_velocity(
            flow_analysis['total_syllables'], 
            len(lines),
            target_bpm
        )
        
        syllable_rate_per_bar = flow_analysis['total_syllables'] / len(lines) if lines else 0
        constraints = GENRE_SYLLABLE_CONSTRAINTS.get(genre_key, GENRE_SYLLABLE_CONSTRAINTS['default'])
        target = constraints['target_syllables']
        syllable_compliance = 1 - abs(syllable_rate_per_bar - target) / target if target else 1
        
        metrics_update = {
            'syllable_velocity': syllable_velocity,
            'syllable_rate_per_bar': syllable_rate_per_bar,
            'syllable_compliance': max(0, min(1, syllable_compliance)),
            'plosive_density_index': pdi_analysis['pdi'],
            'stress_pattern': stress_analysis['stress_map'],
            'breath_points': breath_analysis['total_breath_points'],
            'breath_injections_needed': breath_analysis['injections_needed'],
            'flow_consistency': flow_analysis['consistency'],
            'syllable_variance': variance_analysis['variance'],
            'flow_classification': variance_analysis['classification'],
            'using_syllables_library': SYLLABLES_AVAILABLE,
        }
        
        existing_metrics = state.get('lyrical_metrics', {})
        updated_metrics = {**existing_metrics, **metrics_update}
        
        quality_passed = self._assess_flow_quality(
            flow_analysis, 
            variance_analysis, 
            genre_key
        )
        
        return AgentResult.success_result(
            state_updates={
                'lyrical_metrics': updated_metrics
            },
            metadata={
                'flow_analysis': flow_analysis,
                'pdi_analysis': pdi_analysis,
                'breath_analysis': breath_analysis,
                'variance_analysis': variance_analysis,
                'stress_analysis': stress_analysis,
                'quality_passed': quality_passed,
                'genre_constraints': constraints
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
    
    def _analyze_flow(self, lines: List[str], bpm: int, genre_key: str) -> Dict[str, Any]:
        """
        Analyze overall flow characteristics.
        
        Calculates:
        - Total syllables (using syllables library if available)
        - Syllables per line
        - Flow consistency (variance-based)
        - Genre constraint compliance
        """
        syllable_counts = []
        total = 0
        
        for line in lines:
            count = self._count_syllables_accurate(line)
            syllable_counts.append(count)
            total += count
        
        consistency = self._calculate_consistency(syllable_counts)
        
        beats_per_line = 4
        seconds_per_beat = 60.0 / bpm
        estimated_duration = len(lines) * beats_per_line * seconds_per_beat
        
        constraints = GENRE_SYLLABLE_CONSTRAINTS.get(genre_key, GENRE_SYLLABLE_CONSTRAINTS['default'])
        avg_syllables = total / len(lines) if lines else 0
        constraint_compliance = self._check_constraint_compliance(avg_syllables, constraints)
        
        return {
            'total_syllables': total,
            'syllables_per_line': syllable_counts,
            'consistency': consistency,
            'estimated_duration': estimated_duration,
            'avg_syllables_per_line': avg_syllables,
            'constraint_compliance': constraint_compliance
        }
    
    def _count_syllables_accurate(self, text: str) -> int:
        """
        Count syllables using the syllables library if available.
        
        Falls back to vowel cluster heuristic if not.
        """
        text = re.sub(r'[^a-zA-Z\s]', '', text.lower())
        words = text.split()
        
        if not words:
            return 0
        
        if SYLLABLES_AVAILABLE:
            total = 0
            for word in words:
                try:
                    count = syllables.estimate(word)
                    total += max(1, count)
                except:
                    total += self._count_syllables_heuristic(word)
            return total
        else:
            return sum(self._count_syllables_heuristic(word) for word in words)
    
    def _count_syllables_heuristic(self, word: str) -> int:
        """Count syllables using vowel cluster heuristic."""
        word = word.lower()
        count = 0
        prev_vowel = False
        
        for char in word:
            is_vowel = char in 'aeiouy'
            if is_vowel and not prev_vowel:
                count += 1
            prev_vowel = is_vowel
        
        if word.endswith('e') and count > 1:
            count -= 1
        
        return max(1, count)
    
    def _check_constraint_compliance(
        self, 
        avg_syllables: float, 
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if syllable rate complies with genre constraints."""
        target = constraints['target_syllables']
        tolerance = constraints['tolerance']
        
        deviation = abs(avg_syllables - target)
        is_compliant = deviation <= tolerance
        
        return {
            'is_compliant': is_compliant,
            'deviation': deviation,
            'target': target,
            'tolerance': tolerance
        }
    
    def _calculate_consistency(self, counts: List[int]) -> float:
        """Calculate flow consistency based on syllable variance."""
        if len(counts) < 2:
            return 1.0
        
        import statistics
        mean = statistics.mean(counts)
        variance = statistics.variance(counts)
        
        cv = (variance ** 0.5) / mean if mean > 0 else 0
        
        return max(0, min(1, 1 - cv))
    
    def _calculate_plosive_density_index(self, lines: List[str]) -> Dict[str, Any]:
        """
        Calculate Plosive Density Index (PDI).
        
        PDI measures the ratio of plosive consonants (b, d, g, k, p, t)
        to total consonants. Higher PDI = more rhythmic "punch".
        
        Optimal range for aggressive rap: 0.12-0.18
        Low PDI (<0.08): Soft, melodic delivery
        High PDI (>0.20): Maximum punch, potentially fatiguing
        """
        total_plosives = 0
        total_consonants = 0
        total_chars = 0
        plosive_clusters = []
        
        consonants = set('bcdfghjklmnpqrstvwxyz')
        
        for line in lines:
            text = line.lower()
            total_chars += len(re.findall(r'[a-z]', text))
            
            current_cluster = []
            
            for char in text:
                if char in consonants:
                    total_consonants += 1
                    if char in PLOSIVE_CONSONANTS:
                        total_plosives += 1
                        current_cluster.append(char)
                else:
                    if len(current_cluster) >= 2:
                        plosive_clusters.append(''.join(current_cluster))
                    current_cluster = []
        
        pdi = total_plosives / total_consonants if total_consonants > 0 else 0
        
        if pdi > 0.18:
            pdi_rating = 'high_punch'
        elif pdi > 0.12:
            pdi_rating = 'optimal'
        elif pdi > 0.08:
            pdi_rating = 'moderate'
        else:
            pdi_rating = 'soft'
        
        return {
            'pdi': pdi,
            'total_plosives': total_plosives,
            'total_consonants': total_consonants,
            'plosive_clusters': plosive_clusters,
            'pdi_rating': pdi_rating
        }
    
    def _analyze_breath_points(self, lines: List[str]) -> Dict[str, Any]:
        """
        Analyze breath points and suggest injections for long phrases.
        
        Breath injection is needed when a phrase exceeds MAX_PHRASE_SYLLABLES
        (typically 14-16 syllables) without a natural pause.
        """
        natural_breath_points = []
        injection_points = []
        
        for i, line in enumerate(lines):
            if any(p in line for p in [',', ';', '-', '...', ':']):
                natural_breath_points.append({
                    'line_index': i,
                    'type': 'punctuation'
                })
            
            if line.endswith('.') or line.endswith('!') or line.endswith('?'):
                natural_breath_points.append({
                    'line_index': i,
                    'type': 'sentence_end'
                })
            
            syllable_count = self._count_syllables_accurate(line)
            if syllable_count > MAX_PHRASE_SYLLABLES:
                has_natural_break = any(p in line for p in [',', ';', '-'])
                if not has_natural_break:
                    suggested_position = self._find_breath_injection_point(line)
                    injection_points.append({
                        'line_index': i,
                        'syllable_count': syllable_count,
                        'suggested_position': suggested_position,
                        'reason': f'Exceeds {MAX_PHRASE_SYLLABLES} syllables'
                    })
        
        return {
            'natural_breath_points': natural_breath_points,
            'injection_points': injection_points,
            'injections_needed': len(injection_points),
            'total_breath_points': len(natural_breath_points)
        }
    
    def _find_breath_injection_point(self, line: str) -> int:
        """
        Find the optimal position to inject a breath in a long phrase.
        
        Prefers positions after conjunctions, prepositions, or mid-line.
        """
        words = line.split()
        if len(words) <= 2:
            return len(line) // 2
        
        break_words = {'and', 'but', 'or', 'the', 'a', 'an', 'to', 'in', 'on', 'at', 'for', 'with'}
        
        mid_point = len(words) // 2
        for i in range(mid_point - 2, mid_point + 3):
            if 0 < i < len(words) and words[i].lower() in break_words:
                return sum(len(w) + 1 for w in words[:i])
        
        return sum(len(w) + 1 for w in words[:mid_point])
    
    def _analyze_syllable_variance(self, syllable_counts: List[int]) -> Dict[str, Any]:
        """
        Analyze syllable variance to classify flow type.
        
        Flow Classification:
        - High variance (>5): Broken/experimental flow
        - Low variance (<3): Choppy/rigid flow  
        - Moderate variance (3-5): Complex syncopated flow (ideal)
        """
        if len(syllable_counts) < 2:
            return {
                'variance': 0,
                'std_dev': 0,
                'classification': 'insufficient_data',
                'optimal': False
            }
        
        import statistics
        variance = statistics.variance(syllable_counts)
        std_dev = statistics.stdev(syllable_counts)
        
        if variance > 5:
            classification = 'broken_flow'
            optimal = False
        elif variance < 3:
            classification = 'rigid_flow'
            optimal = False
        else:
            classification = 'syncopated_flow'
            optimal = True
        
        return {
            'variance': variance,
            'std_dev': std_dev,
            'classification': classification,
            'optimal': optimal
        }
    
    def _analyze_stress_patterns(self, lines: List[str]) -> Dict[str, Any]:
        """
        Build stress maps for each line.
        
        Uses CMU Pronouncing Dictionary for accurate stress when available.
        """
        stress_map = []
        pattern_counts = {}
        
        for line in lines:
            words = re.findall(r'\b[a-zA-Z]+\b', line.lower())
            line_stress = []
            
            for i, word in enumerate(words):
                stress = self._get_word_stress(word, i, len(words))
                line_stress.extend(stress)
            
            stress_map.append(line_stress)
            
            pattern = ''.join(str(s) for s in line_stress[:4])
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        dominant_pattern = max(pattern_counts.keys(), key=lambda k: pattern_counts[k]) if pattern_counts else ''
        
        return {
            'stress_map': stress_map,
            'pattern_counts': pattern_counts,
            'dominant_pattern': dominant_pattern
        }
    
    def _get_word_stress(self, word: str, position: int, total: int) -> List[int]:
        """
        Get stress pattern for a word.
        
        Uses CMU Dictionary when available, otherwise estimates.
        """
        if PRONOUNCING_AVAILABLE:
            phones = pronouncing.phones_for_word(word)
            if phones:
                stress = pronouncing.stresses(phones[0])
                return [int(s) for s in stress] if stress else [1]
        
        return self._estimate_word_stress(word, position, total)
    
    def _estimate_word_stress(self, word: str, position: int, total: int) -> List[int]:
        """Estimate stress pattern for a word."""
        syllables_count = self._count_syllables_heuristic(word)
        
        if syllables_count == 1:
            return [1 if position in (0, total-1) else 0]
        elif syllables_count == 2:
            return [1, 0]
        else:
            pattern = []
            for i in range(syllables_count):
                if i == 0:
                    pattern.append(1)
                elif i % 2 == 0:
                    pattern.append(2)
                else:
                    pattern.append(0)
            return pattern
    
    def _calculate_syllable_velocity(
        self, 
        total_syllables: int, 
        line_count: int, 
        bpm: int
    ) -> float:
        """
        Calculate syllables per second.
        
        Different rap styles have different target rates:
        - Boom Bap (90 BPM): ~4-5 syllables/sec
        - Trap (140 BPM): ~7-8 syllables/sec (double-time)
        - Speed Rap (160+ BPM): 10+ syllables/sec
        """
        if line_count == 0:
            return 0.0
        
        beats_per_line = 4
        total_beats = line_count * beats_per_line
        seconds = total_beats * (60.0 / bpm)
        
        return total_syllables / seconds if seconds > 0 else 0.0
    
    def _assess_flow_quality(
        self, 
        flow_analysis: Dict[str, Any], 
        variance_analysis: Dict[str, Any],
        genre_key: str
    ) -> bool:
        """Assess overall flow quality."""
        if flow_analysis['consistency'] < 0.3:
            self.logger.warning("Flow consistency too low")
            return False
        
        if not flow_analysis['constraint_compliance']['is_compliant']:
            deviation = flow_analysis['constraint_compliance']['deviation']
            self.logger.warning(f"Syllable rate deviates by {deviation:.1f} from genre target")
        
        return True
