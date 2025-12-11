"""
APEX Engine Report Generator.

Generates analysis reports including:
- Brutal Critique: Honest quality assessment
- Dopamine Checklist: Engagement factors
- Technical Summary: Metrics breakdown
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ReportSection:
    """A section of the analysis report."""
    title: str
    content: str
    metrics: Dict[str, Any]
    grade: str


class ReportGenerator:
    """
    Report Generator: Creates analysis reports for generated tracks.
    
    Produces two types of reports:
    1. Brutal Critique - Honest, no-holds-barred quality assessment
    2. Dopamine Checklist - Engagement and virality factors
    """
    
    GRADE_THRESHOLDS = {
        'S': 0.95,
        'A': 0.85,
        'B': 0.70,
        'C': 0.55,
        'D': 0.40,
        'F': 0.0
    }
    
    def __init__(self):
        """Initialize the report generator."""
        self.report_count = 0
    
    def generate_full_report(
        self, 
        state: Dict[str, Any],
        include_brutal: bool = True,
        include_dopamine: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a complete analysis report.
        
        Args:
            state: RapGenerationState with all metrics
            include_brutal: Include brutal critique section
            include_dopamine: Include dopamine checklist
            
        Returns:
            Complete report dictionary
        """
        self.report_count += 1
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'report_id': f"APEX-{self.report_count:04d}",
            'summary': self._generate_summary(state),
            'sections': []
        }
        
        if include_brutal:
            report['sections'].append(self._generate_brutal_critique(state))
        
        if include_dopamine:
            report['sections'].append(self._generate_dopamine_checklist(state))
        
        report['sections'].append(self._generate_technical_summary(state))
        
        report['overall_grade'] = self._calculate_overall_grade(state)
        report['recommendations'] = self._generate_recommendations(state)
        
        return report
    
    def _generate_summary(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary."""
        lyrical = state.get('lyrical_metrics', {})
        audio = state.get('analysis_metrics', {})
        
        return {
            'status': state.get('status', 'unknown'),
            'iterations': state.get('iteration_count', 0),
            'credits_used': state.get('credits_used', 0),
            'rhyme_factor': lyrical.get('rhyme_factor', 0),
            'frisson_score': audio.get('frisson_score', 0),
            'quality_passed': audio.get('quality_passed', False)
        }
    
    def _generate_brutal_critique(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate the "Brutal Critique" section.
        
        Honest, direct assessment of the track's weaknesses and strengths.
        """
        lyrical = state.get('lyrical_metrics', {})
        audio = state.get('analysis_metrics', {})
        
        critique_points = []
        
        rhyme = lyrical.get('rhyme_factor', 0)
        if rhyme >= 0.8:
            critique_points.append(f"Rhyme density is strong ({rhyme:.2f}) - lyrical prowess evident")
        elif rhyme >= 0.5:
            critique_points.append(f"Rhyme density is acceptable ({rhyme:.2f}) - room for improvement")
        else:
            critique_points.append(f"Rhyme density is weak ({rhyme:.2f}) - needs significant work")
        
        frisson = audio.get('frisson_score', 0)
        if frisson >= 0.7:
            critique_points.append(f"Frisson potential is high ({frisson:.2f}) - chills guaranteed")
        elif frisson >= 0.4:
            critique_points.append(f"Frisson potential is moderate ({frisson:.2f}) - some emotional impact")
        else:
            critique_points.append(f"Frisson potential is low ({frisson:.2f}) - lacks emotional punch")
        
        sync = audio.get('syncopation_index', 22.5)
        if 15 <= sync <= 30:
            critique_points.append(f"Groove is in the sweet spot ({sync:.1f}) - head-nodding quality")
        elif sync < 15:
            critique_points.append(f"Groove is too rigid ({sync:.1f}) - needs more syncopation")
        else:
            critique_points.append(f"Groove is chaotic ({sync:.1f}) - dial back the complexity")
        
        onset = audio.get('onset_confidence', 0.5)
        if onset >= 0.7:
            critique_points.append("Vocals sit perfectly in the pocket")
        else:
            critique_points.append(f"Vocal timing is off ({onset:.2f}) - needs tighter delivery")
        
        return {
            'title': 'BRUTAL CRITIQUE',
            'content': '\n'.join(f"• {point}" for point in critique_points),
            'metrics': {
                'rhyme_factor': rhyme,
                'frisson_score': frisson,
                'syncopation_index': sync,
                'onset_confidence': onset
            },
            'grade': self._score_to_grade(
                (rhyme * 0.3 + frisson * 0.3 + onset * 0.4)
            )
        }
    
    def _generate_dopamine_checklist(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate the "Dopamine Checklist" section.
        
        Checks engagement and addiction factors.
        """
        lyrical = state.get('lyrical_metrics', {})
        audio = state.get('analysis_metrics', {})
        
        checks = []
        score_sum = 0
        
        earworm = lyrical.get('earworm_score', 0.5)
        checks.append({
            'item': 'Hook Catchiness (Earworm)',
            'passed': earworm >= 0.6,
            'value': earworm
        })
        score_sum += 1 if earworm >= 0.6 else 0
        
        frisson = audio.get('frisson_score', 0.5)
        checks.append({
            'item': 'Emotional Impact (Frisson)',
            'passed': frisson >= 0.5,
            'value': frisson
        })
        score_sum += 1 if frisson >= 0.5 else 0
        
        sync = audio.get('syncopation_index', 22.5)
        groove_pass = 15 <= sync <= 35
        checks.append({
            'item': 'Groove Quality',
            'passed': groove_pass,
            'value': sync
        })
        score_sum += 1 if groove_pass else 0
        
        meme = lyrical.get('meme_score', 0.5)
        checks.append({
            'item': 'Quotability (Meme Potential)',
            'passed': meme >= 0.5,
            'value': meme
        })
        score_sum += 1 if meme >= 0.5 else 0
        
        production = 1 - audio.get('mud_ratio', 0.15) * 3
        checks.append({
            'item': 'Production Polish',
            'passed': production >= 0.7,
            'value': production
        })
        score_sum += 1 if production >= 0.7 else 0
        
        passed = sum(1 for c in checks if c['passed'])
        
        return {
            'title': 'DOPAMINE CHECKLIST',
            'content': '\n'.join(
                f"[{'✓' if c['passed'] else '✗'}] {c['item']}: {c['value']:.2f}"
                for c in checks
            ),
            'metrics': {c['item']: c['value'] for c in checks},
            'grade': self._score_to_grade(passed / len(checks)),
            'passed_count': passed,
            'total_count': len(checks)
        }
    
    def _generate_technical_summary(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate technical metrics summary."""
        lyrical = state.get('lyrical_metrics', {})
        audio = state.get('analysis_metrics', {})
        plan = state.get('structured_plan', {})
        
        metrics = {
            'Target BPM': plan.get('bpm', 'N/A'),
            'Detected BPM': audio.get('detected_bpm', 'N/A'),
            'BPM Accuracy': f"{audio.get('bpm_confidence', 0):.1%}" if 'bpm_confidence' in audio else 'N/A',
            'Rhyme Factor': f"{lyrical.get('rhyme_factor', 0):.2f}",
            'Flow Consistency': f"{lyrical.get('flow_consistency', 0):.2f}",
            'Syncopation Index': f"{audio.get('syncopation_index', 0):.1f}",
            'Frisson Score': f"{audio.get('frisson_score', 0):.2f}",
            'Dynamic Range': f"{audio.get('dynamic_range', 0):.3f}",
            'Spectral Centroid': f"{audio.get('spectral_centroid_mean', 0):.0f} Hz"
        }
        
        return {
            'title': 'TECHNICAL SUMMARY',
            'content': '\n'.join(f"{k}: {v}" for k, v in metrics.items()),
            'metrics': metrics,
            'grade': 'N/A'
        }
    
    def _calculate_overall_grade(self, state: Dict[str, Any]) -> str:
        """Calculate overall track grade."""
        lyrical = state.get('lyrical_metrics', {})
        audio = state.get('analysis_metrics', {})
        
        components = [
            lyrical.get('rhyme_factor', 0.5) * 0.2,
            lyrical.get('flow_consistency', 0.5) * 0.15,
            audio.get('onset_confidence', 0.5) * 0.2,
            audio.get('frisson_score', 0.5) * 0.2,
            lyrical.get('earworm_score', 0.5) * 0.15,
            (1 - audio.get('mud_ratio', 0.15) * 3) * 0.1
        ]
        
        overall = sum(components)
        return self._score_to_grade(overall)
    
    def _score_to_grade(self, score: float) -> str:
        """Convert numerical score to letter grade."""
        for grade, threshold in self.GRADE_THRESHOLDS.items():
            if score >= threshold:
                return grade
        return 'F'
    
    def _generate_recommendations(self, state: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        lyrical = state.get('lyrical_metrics', {})
        audio = state.get('analysis_metrics', {})
        
        if lyrical.get('rhyme_factor', 0) < 0.5:
            recommendations.append(
                "Increase rhyme density - aim for more end rhymes and internal rhymes"
            )
        
        if audio.get('frisson_score', 0) < 0.5:
            recommendations.append(
                "Add more dynamic contrast - build tension before drops"
            )
        
        sync = audio.get('syncopation_index', 22.5)
        if sync < 15:
            recommendations.append(
                "Add more syncopation - push some vocals off the beat"
            )
        elif sync > 40:
            recommendations.append(
                "Simplify the rhythm - some sections feel chaotic"
            )
        
        if audio.get('mud_ratio', 0) > 0.2:
            recommendations.append(
                "Clean up the mix - reduce energy in 250-500Hz range"
            )
        
        return recommendations[:5]
    
    def format_text_report(self, report: Dict[str, Any]) -> str:
        """Format report as plain text."""
        lines = [
            "=" * 60,
            f"APEX ENGINE ANALYSIS REPORT",
            f"Report ID: {report['report_id']}",
            f"Generated: {report['generated_at']}",
            f"Overall Grade: {report['overall_grade']}",
            "=" * 60,
            ""
        ]
        
        for section in report.get('sections', []):
            lines.append(f"\n--- {section['title']} ---")
            lines.append(section['content'])
            if section.get('grade') and section['grade'] != 'N/A':
                lines.append(f"Section Grade: {section['grade']}")
        
        if report.get('recommendations'):
            lines.append("\n--- RECOMMENDATIONS ---")
            for i, rec in enumerate(report['recommendations'], 1):
                lines.append(f"{i}. {rec}")
        
        lines.append("\n" + "=" * 60)
        
        return '\n'.join(lines)
