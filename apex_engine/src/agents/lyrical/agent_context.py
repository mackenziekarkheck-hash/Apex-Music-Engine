"""
Context Analyzer Agent - Narrative Consistency & Persona Drift.

This agent analyzes semantic coherence in rap lyrics:
- Narrative consistency across verses
- Persona/character drift detection
- Theme coherence scoring
- Semantic similarity between sections

Reference: DopeLearning semantic analysis from framework documentation
"""

from typing import Dict, Any, List, Optional, Set
import re
from collections import Counter

from ..agent_base import AnalysisAgent, AgentRole, AgentResult


class ContextAnalyzer(AnalysisAgent):
    """
    Context Analyzer: Semantic coherence and narrative analysis.
    
    Ensures lyrical creativity doesn't descend into nonsense by:
    
    1. Tracking thematic keywords across verses
    2. Detecting persona consistency (first person, etc.)
    3. Measuring semantic similarity between sections
    4. Identifying narrative arc patterns
    
    Uses bag-of-words overlap and keyword tracking
    for lightweight semantic analysis.
    """
    
    PERSONA_FIRST_PERSON = {'i', 'me', 'my', 'mine', "i'm", 'we', 'us', 'our'}
    PERSONA_SECOND_PERSON = {'you', 'your', "you're", 'yours'}
    PERSONA_THIRD_PERSON = {'he', 'she', 'they', 'them', 'his', 'her', 'their'}
    
    STOP_WORDS = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 
                  'to', 'for', 'of', 'is', 'it', 'this', 'that', 'with'}
    
    @property
    def role(self) -> AgentRole:
        return AgentRole.LYRICAL_ARCHITECT
    
    def _validate_input(self, state: Dict[str, Any]) -> List[str]:
        """Validate input state."""
        errors = []
        
        lyrics = state.get('lyrics_validated') or state.get('lyrics_draft')
        if not lyrics:
            errors.append("Lyrics are required for context analysis")
            
        return errors
    
    def _execute(self, state: Dict[str, Any]) -> AgentResult:
        """
        Analyze semantic context and narrative coherence.
        
        Steps:
        1. Parse lyrics into sections (verse, chorus, etc.)
        2. Extract keywords per section
        3. Analyze persona consistency
        4. Calculate thematic coherence
        5. Detect narrative patterns
        """
        lyrics = state.get('lyrics_validated') or state.get('lyrics_draft', '')
        
        sections = self._parse_sections(lyrics)
        
        keyword_analysis = self._analyze_keywords(sections)
        
        persona_analysis = self._analyze_persona(sections)
        
        coherence_score = self._calculate_coherence(sections, keyword_analysis)
        
        narrative_arc = self._detect_narrative_arc(sections)
        
        drift_score = self._calculate_persona_drift(persona_analysis)
        
        metrics_update = {
            'semantic_coherence': coherence_score,
            'persona_drift': drift_score,
            'primary_persona': persona_analysis['primary_persona'],
            'theme_keywords': keyword_analysis['top_keywords']
        }
        
        existing_metrics = state.get('lyrical_metrics', {})
        updated_metrics = {**existing_metrics, **metrics_update}
        
        quality_passed = coherence_score > 0.3 and drift_score < 0.5
        
        return AgentResult.success_result(
            state_updates={
                'lyrical_metrics': updated_metrics
            },
            warnings=self._generate_warnings(coherence_score, drift_score),
            metadata={
                'sections': sections,
                'keyword_analysis': keyword_analysis,
                'persona_analysis': persona_analysis,
                'narrative_arc': narrative_arc,
                'quality_passed': quality_passed
            }
        )
    
    def _parse_sections(self, lyrics: str) -> List[Dict[str, Any]]:
        """
        Parse lyrics into labeled sections.
        
        Returns a list of sections with type and content.
        """
        sections = []
        current_section = {'type': 'intro', 'lines': []}
        
        for line in lyrics.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('['):
                if current_section['lines']:
                    sections.append(current_section)
                    
                section_type = re.sub(r'[\[\]\d\s]', '', line.lower())
                current_section = {'type': section_type, 'lines': []}
            elif not line.startswith('('):
                current_section['lines'].append(line)
        
        if current_section['lines']:
            sections.append(current_section)
            
        return sections
    
    def _analyze_keywords(self, sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract and analyze keywords from each section.
        
        Excludes stop words and identifies thematic patterns.
        """
        all_keywords = Counter()
        section_keywords = []
        
        for section in sections:
            text = ' '.join(section['lines']).lower()
            words = re.findall(r'\b[a-z]+\b', text)
            
            keywords = [w for w in words 
                       if w not in self.STOP_WORDS and len(w) > 3]
            
            section_counter = Counter(keywords)
            section_keywords.append({
                'type': section['type'],
                'keywords': section_counter.most_common(10)
            })
            
            all_keywords.update(keywords)
        
        return {
            'top_keywords': [kw for kw, _ in all_keywords.most_common(20)],
            'section_keywords': section_keywords,
            'total_unique': len(all_keywords)
        }
    
    def _analyze_persona(self, sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze persona consistency across sections.
        
        Detects which grammatical person (I, you, they) dominates
        and how consistent it is across the song.
        """
        persona_counts = {
            'first': 0,
            'second': 0,
            'third': 0
        }
        section_personas = []
        
        for section in sections:
            text = ' '.join(section['lines']).lower()
            words = set(re.findall(r'\b[a-z\']+\b', text))
            
            first = len(words & self.PERSONA_FIRST_PERSON)
            second = len(words & self.PERSONA_SECOND_PERSON)
            third = len(words & self.PERSONA_THIRD_PERSON)
            
            persona_counts['first'] += first
            persona_counts['second'] += second
            persona_counts['third'] += third
            
            dominant = 'first' if first >= second and first >= third else \
                      'second' if second >= third else 'third'
            section_personas.append({
                'type': section['type'],
                'dominant_persona': dominant,
                'counts': {'first': first, 'second': second, 'third': third}
            })
        
        total = sum(persona_counts.values())
        if total == 0:
            primary = 'first'
        else:
            primary = max(persona_counts.keys(), key=lambda k: persona_counts[k])
        
        return {
            'primary_persona': primary,
            'persona_counts': persona_counts,
            'section_personas': section_personas
        }
    
    def _calculate_coherence(
        self, 
        sections: List[Dict[str, Any]], 
        keyword_analysis: Dict[str, Any]
    ) -> float:
        """
        Calculate thematic coherence score.
        
        Based on:
        - Keyword overlap between sections
        - Theme consistency
        - Semantic similarity between verses
        """
        if len(sections) < 2:
            return 1.0
            
        section_kw_sets = []
        for sk in keyword_analysis['section_keywords']:
            kw_set = set(kw for kw, _ in sk['keywords'])
            section_kw_sets.append(kw_set)
        
        overlaps = []
        for i in range(1, len(section_kw_sets)):
            prev_set = section_kw_sets[i-1]
            curr_set = section_kw_sets[i]
            
            if prev_set or curr_set:
                intersection = len(prev_set & curr_set)
                union = len(prev_set | curr_set)
                jaccard = intersection / union if union > 0 else 0
                overlaps.append(jaccard)
        
        return sum(overlaps) / len(overlaps) if overlaps else 0.5
    
    def _calculate_persona_drift(self, persona_analysis: Dict[str, Any]) -> float:
        """
        Calculate persona drift score.
        
        High drift = inconsistent perspective shifts
        Low drift = consistent narrative voice
        """
        section_personas = persona_analysis['section_personas']
        
        if len(section_personas) < 2:
            return 0.0
            
        primary = persona_analysis['primary_persona']
        
        drift_count = 0
        for sp in section_personas:
            if sp['dominant_persona'] != primary:
                drift_count += 1
                
        return drift_count / len(section_personas)
    
    def _detect_narrative_arc(self, sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect narrative arc patterns.
        
        Common rap structures:
        - Setup -> Conflict -> Resolution
        - Intro -> Development -> Climax -> Outro
        """
        section_types = [s['type'] for s in sections]
        
        has_intro = 'intro' in section_types
        has_outro = 'outro' in section_types
        verse_count = sum(1 for t in section_types if 'verse' in t)
        has_chorus = 'chorus' in section_types or 'hook' in section_types
        
        if has_intro and has_outro and verse_count >= 2:
            arc_type = 'complete'
        elif verse_count >= 2 and has_chorus:
            arc_type = 'standard'
        elif verse_count >= 1:
            arc_type = 'simple'
        else:
            arc_type = 'fragment'
            
        return {
            'arc_type': arc_type,
            'section_sequence': section_types,
            'verse_count': verse_count,
            'has_hook': has_chorus
        }
    
    def _generate_warnings(self, coherence: float, drift: float) -> List[str]:
        """Generate warnings for quality issues."""
        warnings = []
        
        if coherence < 0.3:
            warnings.append(
                f"Low thematic coherence ({coherence:.2f}). "
                "Sections may feel disconnected."
            )
            
        if drift > 0.5:
            warnings.append(
                f"High persona drift ({drift:.2f}). "
                "Consider maintaining consistent perspective."
            )
            
        return warnings
