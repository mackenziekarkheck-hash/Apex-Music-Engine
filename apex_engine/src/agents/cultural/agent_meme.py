"""
Meme Analyzer Agent - Caption Capability Score (Quotability).

This agent analyzes lyrics for meme potential and quotability:
- Punchline detection
- Caption-friendly phrase identification
- Shareability scoring
"""

from typing import Dict, Any, List, Optional
import re

from ..agent_base import AnalysisAgent, AgentRole, AgentResult


class MemeAnalyzer(AnalysisAgent):
    """
    Meme Analyzer: Quotability and shareability analysis.
    
    Evaluates lyrics for:
    - Standalone punch lines (work out of context)
    - Caption-friendly length (short, impactful)
    - Universal relatability
    - Wordplay and cleverness
    """
    
    OPTIMAL_CAPTION_LENGTH = (5, 15)
    
    @property
    def role(self) -> AgentRole:
        return AgentRole.LYRICAL_ARCHITECT
    
    def _validate_input(self, state: Dict[str, Any]) -> List[str]:
        """Validate input state."""
        errors = []
        if not state.get('lyrics_validated') and not state.get('lyrics_draft'):
            errors.append("Lyrics required for meme analysis")
        return errors
    
    def _execute(self, state: Dict[str, Any]) -> AgentResult:
        """
        Analyze lyrics for meme potential.
        """
        lyrics = state.get('lyrics_validated') or state.get('lyrics_draft', '')
        
        lines = self._extract_content_lines(lyrics)
        
        quotable_lines = self._find_quotable_lines(lines)
        
        punchlines = self._detect_punchlines(lines)
        
        meme_score = self._calculate_meme_score(quotable_lines, punchlines, len(lines))
        
        metrics_update = {
            'meme_score': meme_score,
            'quotable_lines': len(quotable_lines),
            'punchline_count': len(punchlines)
        }
        
        existing = state.get('lyrical_metrics', {})
        updated = {**existing, **metrics_update}
        
        return AgentResult.success_result(
            state_updates={'lyrical_metrics': updated},
            metadata={
                'quotable_lines': quotable_lines[:5],
                'punchlines': punchlines[:5],
                'meme_score': meme_score
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
    
    def _find_quotable_lines(self, lines: List[str]) -> List[Dict[str, Any]]:
        """
        Find lines that work well as standalone captions.
        
        Criteria:
        - Optimal length (5-15 words)
        - Contains strong imagery or metaphor
        - Self-contained meaning
        """
        quotable = []
        
        for i, line in enumerate(lines):
            words = line.split()
            word_count = len(words)
            
            if self.OPTIMAL_CAPTION_LENGTH[0] <= word_count <= self.OPTIMAL_CAPTION_LENGTH[1]:
                score = self._score_quotability(line)
                if score > 0.5:
                    quotable.append({
                        'line': line,
                        'index': i,
                        'score': score,
                        'word_count': word_count
                    })
        
        return sorted(quotable, key=lambda x: x['score'], reverse=True)
    
    def _score_quotability(self, line: str) -> float:
        """Score a line's quotability."""
        score = 0.5
        
        metaphor_indicators = ['like', 'than', 'same as', 'feel like']
        for indicator in metaphor_indicators:
            if indicator in line.lower():
                score += 0.1
        
        strong_words = ['never', 'always', 'everything', 'nothing', 'only', 'real']
        for word in strong_words:
            if word in line.lower():
                score += 0.05
        
        if any(c in line for c in ['?', '!', '...']):
            score += 0.1
        
        return min(1.0, score)
    
    def _detect_punchlines(self, lines: List[str]) -> List[Dict[str, Any]]:
        """
        Detect punchlines (lines with wordplay or surprise).
        """
        punchlines = []
        
        for i, line in enumerate(lines[1:], 1):
            if self._is_potential_punchline(lines[i-1], line):
                punchlines.append({
                    'setup': lines[i-1],
                    'punchline': line,
                    'index': i
                })
        
        return punchlines
    
    def _is_potential_punchline(self, setup: str, punchline: str) -> bool:
        """Check if a line pair forms a setup-punchline structure."""
        setup_words = set(re.findall(r'\b\w+\b', setup.lower()))
        punch_words = set(re.findall(r'\b\w+\b', punchline.lower()))
        
        overlap = len(setup_words & punch_words)
        if overlap >= 1 and overlap <= 3:
            return True
        
        return False
    
    def _calculate_meme_score(
        self, 
        quotable: List[Dict], 
        punchlines: List[Dict],
        total_lines: int
    ) -> float:
        """Calculate overall meme potential score."""
        if total_lines == 0:
            return 0.0
        
        quotable_density = len(quotable) / total_lines
        punchline_density = len(punchlines) / total_lines
        
        avg_quotability = sum(q['score'] for q in quotable) / len(quotable) if quotable else 0
        
        score = (
            0.4 * min(1.0, quotable_density * 5) +
            0.3 * min(1.0, punchline_density * 5) +
            0.3 * avg_quotability
        )
        
        return min(1.0, max(0.0, score))
