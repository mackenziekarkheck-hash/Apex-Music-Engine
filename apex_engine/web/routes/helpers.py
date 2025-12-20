"""
Shared helper functions for APEX Engine API routes.

Contains analysis and payload building utilities used across multiple routes.
"""

import logging
from apex_engine.src.core.project_manager import ProjectManager
from apex_engine.src.agents.lyrical.lyrical_architect import LyricalArchitectAgent
from apex_engine.src.agents.lyrical.agent_bars import BarsAnalyzer
from apex_engine.src.agents.lyrical.agent_flow import FlowAnalyzer
from apex_engine.src.agents.lyrical.agent_vowel import VowelAnalyzer
from apex_engine.src.agents.cultural.agent_meme import MemeAnalyzer
from apex_engine.src.core.predictor import ViralityPredictor

logger = logging.getLogger(__name__)

lyrical_architect = LyricalArchitectAgent()
bars_analyzer = BarsAnalyzer()
flow_analyzer = FlowAnalyzer()
vowel_analyzer = VowelAnalyzer()
meme_analyzer = MemeAnalyzer()
virality_predictor = ViralityPredictor()


def score_lyrics(lyrics: str, project: dict) -> dict:
    """Score lyrics using analysis agents."""
    state = {
        'lyrics_draft': lyrics,
        'structured_plan': {
            'bpm': project.get('bpm', 140),
            'genre': project.get('genre', 'trap')
        }
    }
    
    try:
        lyrical_result = lyrical_architect.execute(state)
        lyrical_metrics = lyrical_result.state_updates.get('lyrical_metrics', {})
    except Exception as e:
        logger.warning(f"Lyrical analysis failed: {e}")
        lyrical_metrics = {}
    
    pvs_state = {
        'lyrical_metrics': lyrical_metrics,
        'analysis_metrics': {
            'syncopation_index': 20,
            'onset_confidence': 0.8,
            'pocket_alignment': 0.85
        }
    }
    
    try:
        pvs_result = virality_predictor.predict(pvs_state)
        pvs_score = pvs_result.pvs_score
        pvs_tier = pvs_result.tier
    except Exception as e:
        logger.warning(f"PVS prediction failed: {e}")
        pvs_score = 0.5
        pvs_tier = 'UNKNOWN'
    
    return {
        'rhyme_factor': lyrical_metrics.get('rhyme_factor', 0.5),
        'flow_consistency': lyrical_metrics.get('flow_consistency', 0.6),
        'syllable_variance': lyrical_metrics.get('syllable_variance', 0),
        'plosive_density_index': lyrical_metrics.get('plosive_density_index', 0.1),
        'pvs_score': pvs_score,
        'pvs_tier': pvs_tier
    }


def generate_recommendations(scores: dict) -> list:
    """Generate improvement recommendations based on scores."""
    recommendations = []
    
    rhyme = scores.get('rhyme_factor', 0)
    if rhyme < 0.6:
        recommendations.append("Increase rhyme density - add more internal rhymes and multisyllabic end rhymes")
    elif rhyme < 0.8:
        recommendations.append("Consider adding slant rhymes and assonance chains for richer texture")
    
    flow = scores.get('flow_consistency', 0)
    if flow < 0.6:
        recommendations.append("Normalize syllable counts across bars for smoother flow")
    elif flow < 0.8:
        recommendations.append("Fine-tune line lengths for more consistent delivery")
    
    pdi = scores.get('plosive_density_index', 0)
    if pdi < 0.12:
        recommendations.append("Add more plosive consonants (P, B, T, D, K, G) for punch")
    
    pvs = scores.get('pvs_score', 0)
    if pvs < 0.5:
        recommendations.append("Add a memorable hook or quotable line for viral potential")
    elif pvs < 0.7:
        recommendations.append("Strengthen the chorus with repetition and catchiness")
    
    if not recommendations:
        recommendations.append("Lyrics are scoring well! Consider minor polish or approve for generation.")
    
    return recommendations


def generate_console_output(analysis_type: str, algo_scores: dict, gpt_analysis: dict) -> list:
    """Generate color-coded console output for the pre-production console."""
    logs = []
    
    logs.append({
        'type': 'info',
        'message': f"Starting {analysis_type} analysis..."
    })
    
    rhyme = algo_scores.get('rhyme_factor', 0)
    if rhyme >= 0.6:
        logs.append({'type': 'success', 'message': f"PASS: Rhyme Factor = {rhyme:.2f} (threshold: 0.6)"})
    elif rhyme >= 0.3:
        logs.append({'type': 'warning', 'message': f"WARN: Rhyme Factor = {rhyme:.2f} (below recommended: 0.6)"})
    else:
        logs.append({'type': 'error', 'message': f"FAIL: Rhyme Factor = {rhyme:.2f} (minimum: 0.3)"})
    
    flow = algo_scores.get('flow_consistency', 0)
    if flow >= 0.7:
        logs.append({'type': 'success', 'message': f"PASS: Flow Consistency = {flow:.2f}"})
    elif flow >= 0.5:
        logs.append({'type': 'warning', 'message': f"WARN: Flow Consistency = {flow:.2f} (consider normalizing)"})
    else:
        logs.append({'type': 'error', 'message': f"FAIL: Flow Consistency = {flow:.2f} (too inconsistent)"})
    
    pvs = algo_scores.get('pvs_score', 0)
    tier = algo_scores.get('pvs_tier', 'UNKNOWN')
    logs.append({'type': 'info', 'message': f"PVS Score: {pvs:.2f} (Tier: {tier})"})
    
    if gpt_analysis.get('success'):
        gpt_score = gpt_analysis.get('score', 'N/A')
        logs.append({'type': 'info', 'message': f"GPT-4o Analysis Score: {gpt_score}/10"})
        
        for rec in gpt_analysis.get('recommendations', [])[:3]:
            logs.append({'type': 'tip', 'message': f"TIP: {rec}"})
    else:
        logs.append({'type': 'warning', 'message': "GPT-4o analysis unavailable"})
    
    logs.append({'type': 'info', 'message': f"{analysis_type.title()} analysis complete"})
    
    return logs


def generate_detailed_console_output(lyrics: str, project: dict) -> dict:
    """
    Run all lyrical agents and generate comprehensive console output with every metric.
    
    Returns dict with:
    - console_logs: List of color-coded log entries
    - metrics: Flat dict of all extracted metrics for AI context
    """
    logs = []
    metrics = {}
    
    state = {
        'lyrics_draft': lyrics,
        'structured_plan': {
            'bpm': project.get('bpm', 140),
            'genre': project.get('genre', 'trap'),
            'genre_key': project.get('genre', 'trap')
        }
    }
    
    logs.append({'type': 'info', 'message': '═══ APEX COMPREHENSIVE ANALYSIS ═══'})
    logs.append({'type': 'info', 'message': f'Genre: {project.get("genre", "trap")} | BPM: {project.get("bpm", 140)} | Mood: {project.get("mood", "aggressive")}'})
    
    logs.append({'type': 'info', 'message': '─── BarsAnalyzer (Phonetic Rhyme Density) ───'})
    try:
        bars_result = bars_analyzer.execute(state)
        bars_metrics = bars_result.state_updates.get('lyrical_metrics', {})
        bars_meta = bars_result.metadata or {}
        
        rf = bars_metrics.get('rhyme_factor', 0)
        metrics['rhyme_factor'] = rf
        if rf >= 0.8:
            logs.append({'type': 'success', 'message': f'Rhyme Factor: {rf:.3f} (EXCELLENT - elite lyricism)'})
        elif rf >= 0.6:
            logs.append({'type': 'success', 'message': f'Rhyme Factor: {rf:.3f} (GOOD - above threshold)'})
        elif rf >= 0.4:
            logs.append({'type': 'warning', 'message': f'Rhyme Factor: {rf:.3f} (NEEDS WORK - add more rhymes)'})
        else:
            logs.append({'type': 'error', 'message': f'Rhyme Factor: {rf:.3f} (POOR - increase rhyme density)'})
        
        perfect_rhymes = bars_metrics.get('perfect_rhymes', 0)
        slant_rhymes = bars_metrics.get('slant_rhymes', 0)
        metrics['perfect_rhymes'] = perfect_rhymes
        metrics['slant_rhymes'] = slant_rhymes
        logs.append({'type': 'info', 'message': f'Perfect Rhymes: {perfect_rhymes} | Slant Rhymes: {slant_rhymes}'})
        
        multis = bars_metrics.get('multisyllabic_rhymes', 0)
        metrics['multisyllabic_count'] = multis
        if multis >= 5:
            logs.append({'type': 'success', 'message': f'Multisyllabic Rhymes: {multis} (strong technical density)'})
        elif multis >= 2:
            logs.append({'type': 'warning', 'message': f'Multisyllabic Rhymes: {multis} (add more for complexity)'})
        else:
            logs.append({'type': 'error', 'message': f'Multisyllabic Rhymes: {multis} (critical: needs multis)'})
        
        assonance = bars_meta.get('assonance_chains', [])
        metrics['assonance_chain_count'] = len(assonance) if isinstance(assonance, list) else 0
        if assonance and isinstance(assonance, list):
            logs.append({'type': 'info', 'message': f'Assonance Chains Found: {len(assonance)}'})
            for chain in assonance[:3]:
                if isinstance(chain, dict):
                    logs.append({'type': 'tip', 'message': f'  Chain: {chain.get("pattern", chain)}'})
                else:
                    logs.append({'type': 'tip', 'message': f'  Chain: {chain}'})
        
        word_coverage = bars_metrics.get('word_coverage_pct', 0) / 100
        metrics['word_coverage'] = word_coverage
        logs.append({'type': 'info', 'message': f'Word Coverage: {word_coverage:.1%} of words participate in rhymes'})
        
        quality_tier = bars_meta.get('quality_tier', 'unknown')
        logs.append({'type': 'info', 'message': f'Quality Tier: {quality_tier}'})
        
    except Exception as e:
        logs.append({'type': 'error', 'message': f'BarsAnalyzer failed: {str(e)}'})
    
    logs.append({'type': 'info', 'message': '─── FlowAnalyzer (Rhythmic Dynamics) ───'})
    try:
        flow_result = flow_analyzer.execute(state)
        flow_metrics = flow_result.state_updates.get('lyrical_metrics', {})
        flow_meta = flow_result.metadata or {}
        
        velocity = flow_metrics.get('syllable_velocity', 0)
        metrics['syllable_velocity'] = velocity
        logs.append({'type': 'info', 'message': f'Syllable Velocity: {velocity:.2f} syllables/second'})
        
        compliance = flow_metrics.get('syllable_compliance', 0)
        metrics['syllable_compliance'] = compliance
        if compliance >= 0.8:
            logs.append({'type': 'success', 'message': f'Syllable Compliance: {compliance:.1%} (excellent meter)'})
        elif compliance >= 0.6:
            logs.append({'type': 'warning', 'message': f'Syllable Compliance: {compliance:.1%} (some meter issues)'})
        else:
            logs.append({'type': 'error', 'message': f'Syllable Compliance: {compliance:.1%} (inconsistent rhythm)'})
        
        pdi = flow_metrics.get('plosive_density_index', 0)
        metrics['plosive_density_index'] = pdi
        if pdi >= 0.15:
            logs.append({'type': 'success', 'message': f'Plosive Density Index: {pdi:.3f} (punchy delivery)'})
        elif pdi >= 0.10:
            logs.append({'type': 'info', 'message': f'Plosive Density Index: {pdi:.3f} (moderate punch)'})
        else:
            logs.append({'type': 'warning', 'message': f'Plosive Density Index: {pdi:.3f} (add P/B/T/D/K/G sounds)'})
        
        flow_class = flow_metrics.get('flow_classification', 'unknown')
        metrics['flow_classification'] = flow_class
        logs.append({'type': 'info', 'message': f'Flow Classification: {flow_class}'})
        
        consistency = flow_metrics.get('flow_consistency', 0)
        metrics['flow_consistency'] = consistency
        if consistency >= 0.7:
            logs.append({'type': 'success', 'message': f'Flow Consistency: {consistency:.1%}'})
        else:
            logs.append({'type': 'warning', 'message': f'Flow Consistency: {consistency:.1%} (normalize syllables)'})
        
        breath_points = flow_meta.get('breath_injections', [])
        metrics['breath_point_count'] = len(breath_points) if isinstance(breath_points, list) else 0
        if breath_points:
            logs.append({'type': 'info', 'message': f'Natural Breath Points: {len(breath_points)} detected'})
        
        syllable_variance = flow_metrics.get('syllable_variance', 0)
        metrics['syllable_variance'] = syllable_variance
        logs.append({'type': 'info', 'message': f'Syllable Variance: {syllable_variance:.2f}'})
        
    except Exception as e:
        logs.append({'type': 'error', 'message': f'FlowAnalyzer failed: {str(e)}'})
    
    logs.append({'type': 'info', 'message': '─── VowelAnalyzer (Phonetic Texture) ───'})
    try:
        vowel_result = vowel_analyzer.execute(state)
        vowel_metrics = vowel_result.state_updates.get('lyrical_metrics', {})
        vowel_meta = vowel_result.metadata or {}
        
        entropy = vowel_metrics.get('vowel_entropy', 0)
        metrics['vowel_entropy'] = entropy
        logs.append({'type': 'info', 'message': f'Vowel Entropy: {entropy:.3f} (variation in vowel sounds)'})
        
        earworm = vowel_metrics.get('earworm_score', 0)
        metrics['earworm_score'] = earworm
        if earworm >= 0.7:
            logs.append({'type': 'success', 'message': f'Earworm Score: {earworm:.2f} (highly memorable)'})
        elif earworm >= 0.5:
            logs.append({'type': 'info', 'message': f'Earworm Score: {earworm:.2f} (moderately catchy)'})
        else:
            logs.append({'type': 'warning', 'message': f'Earworm Score: {earworm:.2f} (increase repetition)'})
        
        euphony = vowel_metrics.get('euphony_score', 0)
        metrics['euphony_score'] = euphony
        logs.append({'type': 'info', 'message': f'Euphony Score: {euphony:.2f} (pleasantness of sound)'})
        
        assonance_patterns = vowel_metrics.get('assonance_patterns', 0)
        logs.append({'type': 'info', 'message': f'Assonance Patterns: {assonance_patterns}'})
        
    except Exception as e:
        logs.append({'type': 'error', 'message': f'VowelAnalyzer failed: {str(e)}'})
    
    logs.append({'type': 'info', 'message': '─── MemeAnalyzer (Cultural Quotability) ───'})
    try:
        meme_result = meme_analyzer.execute(state)
        meme_metrics = meme_result.state_updates.get('lyrical_metrics', {})
        meme_meta = meme_result.metadata or {}
        
        meme_score = meme_metrics.get('meme_score', 0)
        metrics['meme_score'] = meme_score
        if meme_score >= 0.7:
            logs.append({'type': 'success', 'message': f'Meme Score: {meme_score:.2f} (high viral potential)'})
        elif meme_score >= 0.4:
            logs.append({'type': 'info', 'message': f'Meme Score: {meme_score:.2f} (moderate shareability)'})
        else:
            logs.append({'type': 'warning', 'message': f'Meme Score: {meme_score:.2f} (needs quotable moments)'})
        
        quotables = meme_meta.get('quotable_lines', [])
        metrics['quotable_line_count'] = len(quotables) if isinstance(quotables, list) else 0
        if quotables and isinstance(quotables, list):
            logs.append({'type': 'info', 'message': f'Quotable Lines Found: {len(quotables)}'})
            for item in quotables[:3]:
                if isinstance(item, dict):
                    logs.append({'type': 'tip', 'message': f'  "{item.get("line", item)}"'})
                else:
                    logs.append({'type': 'tip', 'message': f'  "{item}"'})
        
        punchlines = meme_meta.get('punchlines', [])
        punchline_count = len(punchlines) if isinstance(punchlines, list) else meme_metrics.get('punchline_count', 0)
        metrics['punchline_count'] = punchline_count
        logs.append({'type': 'info', 'message': f'Punchlines Detected: {punchline_count}'})
        
    except Exception as e:
        logs.append({'type': 'error', 'message': f'MemeAnalyzer failed: {str(e)}'})
    
    logs.append({'type': 'info', 'message': '═══ ANALYSIS COMPLETE ═══'})
    
    return {
        'console_logs': logs,
        'metrics': metrics
    }


def build_api_payload(
    project: dict,
    prompt_text: str = '',
    lyrics_text: str = '',
    neuro_effects: str = '',
    neurochemical_effects: str = '',
    musical_effects: str = ''
) -> dict:
    """Build the Sonauto API payload from all 5 seed composition fields.
    
    Compiles:
    - prompt_text (Description) + neuro_effects + neurochemical_effects + musical_effects -> prompt
    - lyrics_text -> lyrics
    """
    genre = project.get('genre', 'trap')
    mood = project.get('mood', 'aggressive')
    tags = project.get('tags', [genre, 'hip hop', 'rap'])
    
    compiled_prompt_parts = []
    
    if prompt_text.strip():
        compiled_prompt_parts.append(prompt_text.strip())
    else:
        compiled_prompt_parts.append(f"High-fidelity, studio-quality {genre} track. {mood.title()} energy with professional mixing.")
    
    if neuro_effects.strip():
        compiled_prompt_parts.append(f"Mood/Vibe: {neuro_effects.strip()}")
    
    if neurochemical_effects.strip():
        compiled_prompt_parts.append(f"Intended Effect: {neurochemical_effects.strip()}")
    
    if musical_effects.strip():
        compiled_prompt_parts.append(f"Production Style: {musical_effects.strip()}")
    
    compiled_prompt = ". ".join(compiled_prompt_parts)
    if not compiled_prompt.endswith('.'):
        compiled_prompt += '.'
    
    is_instrumental = len(lyrics_text.strip()) == 0
    
    return {
        'prompt': compiled_prompt,
        'tags': tags,
        'lyrics': lyrics_text.strip(),
        'bpm': project.get('bpm', 140),
        'prompt_strength': project.get('prompt_strength', 2.0),
        'balance_strength': project.get('balance_strength', 0.7),
        'output_format': 'wav',
        'instrumental': is_instrumental,
        'num_songs': 1
    }
