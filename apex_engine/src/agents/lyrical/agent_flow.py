"""
Flow Analyzer Agent - Syllabic Velocity & Rhythmic Dynamics.

This agent analyzes the "flow" of rap lyrics:
- Syllabic velocity (syllables per beat)
- Plosive impact (hard consonant clusters)
- Breath injection points
- Stress pattern analysis

Reference: Section 3.2 "Flow Dynamics" from "Neuro-Acoustic Optimization"
"""

from typing import Dict, Any, List, Optional
import re

from ..agent_base import AnalysisAgent, AgentRole, AgentResult


class FlowAnalyzer(AnalysisAgent):
    """
    Flow Analyzer: Rhythmic dynamics and delivery analysis.
    
    "Flow" is the interaction of lyrics with time. This agent
    measures rhythmic consistency and detects flow patterns
    like syncopation, double-time, and triplet flows.
    
    Key Metrics:
    - Syllabic Velocity: syllables per beat
    - Stress Variance: consistency of stressed syllables
    - Breath Points: natural pause locations
    - Plosive Density: hard consonant clusters
    """
    
    PLOSIVE_CONSONANTS = set('bpdtgk')
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
        2. Calculate syllable velocity per line
        3. Build stress maps for each line
        4. Detect plosive clusters
        5. Identify natural breath points
        """
        lyrics = state.get('lyrics_validated') or state.get('lyrics_draft', '')
        plan = state.get('structured_plan', {})
        target_bpm = plan.get('bpm', 90)
        
        lines = self._extract_content_lines(lyrics)
        
        flow_analysis = self._analyze_flow(lines, target_bpm)
        
        stress_analysis = self._analyze_stress_patterns(lines)
        
        plosive_analysis = self._analyze_plosives(lines)
        
        breath_points = self._detect_breath_points(lines)
        
        syllable_rate = self._calculate_syllable_rate(
            flow_analysis['total_syllables'], 
            len(lines),
            target_bpm
        )
        
        metrics_update = {
            'syllable_velocity': syllable_rate,
            'stress_pattern': stress_analysis['stress_map'],
            'plosive_density': plosive_analysis['density'],
            'breath_points': len(breath_points),
            'flow_consistency': flow_analysis['consistency']
        }
        
        existing_metrics = state.get('lyrical_metrics', {})
        updated_metrics = {**existing_metrics, **metrics_update}
        
        quality_passed = self._assess_flow_quality(flow_analysis, stress_analysis)
        
        return AgentResult.success_result(
            state_updates={
                'lyrical_metrics': updated_metrics
            },
            metadata={
                'flow_analysis': flow_analysis,
                'stress_analysis': stress_analysis,
                'plosive_analysis': plosive_analysis,
                'breath_points': breath_points,
                'quality_passed': quality_passed
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
    
    def _analyze_flow(self, lines: List[str], bpm: int) -> Dict[str, Any]:
        """
        Analyze overall flow characteristics.
        
        Calculates:
        - Total syllables
        - Syllables per line
        - Flow consistency (variance-based)
        - Estimated duration
        """
        syllable_counts = []
        total = 0
        
        for line in lines:
            count = self._count_syllables(line)
            syllable_counts.append(count)
            total += count
        
        consistency = self._calculate_consistency(syllable_counts)
        
        beats_per_line = 4
        seconds_per_beat = 60.0 / bpm
        estimated_duration = len(lines) * beats_per_line * seconds_per_beat
        
        return {
            'total_syllables': total,
            'syllables_per_line': syllable_counts,
            'consistency': consistency,
            'estimated_duration': estimated_duration,
            'avg_syllables_per_line': total / len(lines) if lines else 0
        }
    
    def _count_syllables(self, text: str) -> int:
        """Count syllables using vowel cluster heuristic."""
        text = re.sub(r'[^a-zA-Z\s]', '', text.lower())
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
            total += max(1, count)
            
        return total
    
    def _calculate_consistency(self, counts: List[int]) -> float:
        """Calculate flow consistency based on syllable variance."""
        if len(counts) < 2:
            return 1.0
            
        import statistics
        mean = statistics.mean(counts)
        variance = statistics.variance(counts)
        
        cv = (variance ** 0.5) / mean if mean > 0 else 0
        
        return max(0, min(1, 1 - cv))
    
    def _analyze_stress_patterns(self, lines: List[str]) -> Dict[str, Any]:
        """
        Build stress maps for each line.
        
        Uses a simple heuristic based on word length and position.
        Real implementation would use pronouncing library.
        """
        stress_map = []
        pattern_counts = {}
        
        for line in lines:
            words = re.findall(r'\b[a-zA-Z]+\b', line.lower())
            line_stress = []
            
            for i, word in enumerate(words):
                stress = self._estimate_word_stress(word, i, len(words))
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
    
    def _estimate_word_stress(self, word: str, position: int, total: int) -> List[int]:
        """Estimate stress pattern for a word."""
        syllables = self._count_syllables(word)
        
        if syllables == 1:
            return [1 if position in (0, total-1) else 0]
        elif syllables == 2:
            return [1, 0]
        else:
            pattern = []
            for i in range(syllables):
                if i == 0:
                    pattern.append(1)
                elif i % 2 == 0:
                    pattern.append(2)
                else:
                    pattern.append(0)
            return pattern
    
    def _analyze_plosives(self, lines: List[str]) -> Dict[str, Any]:
        """
        Analyze plosive consonant density.
        
        Plosives (b, d, g, k, p, t) create rhythmic "punch"
        and are characteristic of aggressive delivery.
        """
        total_plosives = 0
        total_chars = 0
        clusters = []
        
        for line in lines:
            text = line.lower()
            total_chars += len(re.findall(r'[a-z]', text))
            
            cluster_count = 0
            for i, char in enumerate(text):
                if char in self.PLOSIVE_CONSONANTS:
                    total_plosives += 1
                    cluster_count += 1
                else:
                    if cluster_count >= 2:
                        clusters.append(cluster_count)
                    cluster_count = 0
        
        density = total_plosives / total_chars if total_chars > 0 else 0
        
        return {
            'total_plosives': total_plosives,
            'density': density,
            'clusters': len(clusters),
            'avg_cluster_size': sum(clusters) / len(clusters) if clusters else 0
        }
    
    def _detect_breath_points(self, lines: List[str]) -> List[int]:
        """
        Detect natural breath injection points.
        
        These are positions where a rapper would naturally
        take a breath, typically at punctuation or line ends.
        """
        breath_points = []
        
        for i, line in enumerate(lines):
            if any(p in line for p in [',', ';', '-', '...']):
                breath_points.append(i)
            if line.endswith('.') or line.endswith('!') or line.endswith('?'):
                breath_points.append(i)
                
        return breath_points
    
    def _calculate_syllable_rate(self, total_syllables: int, line_count: int, bpm: int) -> float:
        """
        Calculate syllables per second.
        
        Different rap styles have different target rates:
        - Boom Bap (90 BPM): ~4-5 syllables/sec
        - Trap (140 BPM): ~7-8 syllables/sec (double-time)
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
        stress_analysis: Dict[str, Any]
    ) -> bool:
        """Assess overall flow quality."""
        if flow_analysis['consistency'] < 0.5:
            self.logger.warning("Flow consistency below threshold")
            return False
            
        return True
