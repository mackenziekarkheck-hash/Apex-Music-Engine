"""
APEX Engine Web UI - Flask application for song project management.

Routes:
- /: Dashboard with project list
- /projects: API for project CRUD
- /project/<id>: Project workspace
- /api/generate-lyrics: GPT-4o lyric generation
- /api/iterate: Lyric iteration with scoring
- /api/score: Score lyrics using agents
- /api/approve: Approve lyrics for generation
- /api/generate-audio: Trigger Sonauto generation
"""

import os
import sys
import json
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for

apex_engine_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, apex_engine_path)
sys.path.insert(0, os.path.dirname(apex_engine_path))

from apex_engine.src.core.project_manager import ProjectManager
from apex_engine.src.core.llm_client import LLMClient, FIELD_AGENT_MAPPING
from apex_engine.src.agents.lyrical.lyrical_architect import LyricalArchitectAgent
from apex_engine.src.agents.lyrical.agent_bars import BarsAnalyzer
from apex_engine.src.agents.lyrical.agent_flow import FlowAnalyzer
from apex_engine.src.agents.lyrical.agent_vowel import VowelAnalyzer
from apex_engine.src.agents.cultural.agent_meme import MemeAnalyzer
from apex_engine.src.core.predictor import ViralityPredictor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'apex-dev-key-change-in-prod')

project_manager = ProjectManager()
llm_client = LLMClient()
lyrical_architect = LyricalArchitectAgent()
bars_analyzer = BarsAnalyzer()
flow_analyzer = FlowAnalyzer()
vowel_analyzer = VowelAnalyzer()
meme_analyzer = MemeAnalyzer()
virality_predictor = ViralityPredictor()


@app.route('/')
def index():
    """Dashboard - list all projects."""
    projects = project_manager.list_projects()
    return render_template('index.html', projects=projects)


@app.route('/project/new', methods=['GET', 'POST'])
def new_project():
    """Create a new project."""
    if request.method == 'POST':
        data = request.form
        config = project_manager.create_project(
            name=data.get('name', 'Untitled'),
            genre=data.get('genre', 'trap'),
            bpm=int(data.get('bpm', 140)),
            tags=data.get('tags', '').split(',') if data.get('tags') else None,
            seed_text=data.get('seed_text', ''),
            mood=data.get('mood', 'aggressive'),
            prompt_strength=float(data.get('prompt_strength', 2.0)),
            balance_strength=float(data.get('balance_strength', 0.7))
        )
        return redirect(url_for('project_workspace', project_id=config['id']))
    
    return render_template('new_project.html')


@app.route('/project/<project_id>')
def project_workspace(project_id):
    """Project workspace - main editing interface."""
    try:
        project = project_manager.load_project(project_id)
        return render_template('workspace.html', project=project)
    except ValueError as e:
        return render_template('error.html', error=str(e)), 404


@app.route('/api/projects', methods=['GET'])
def api_list_projects():
    """API: List all projects."""
    projects = project_manager.list_projects()
    return jsonify(projects)


@app.route('/api/project/<project_id>', methods=['GET', 'PUT', 'DELETE'])
def api_project(project_id):
    """API: Project CRUD operations."""
    if request.method == 'GET':
        try:
            project = project_manager.load_project(project_id)
            return jsonify(project)
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
    
    elif request.method == 'PUT':
        data = request.json
        config = project_manager.update_config(project_id, data)
        return jsonify(config)
    
    elif request.method == 'DELETE':
        success = project_manager.delete_project(project_id)
        return jsonify({'success': success})


@app.route('/api/project/<project_id>/seed', methods=['POST'])
def api_save_seed(project_id):
    """API: Save seed text."""
    data = request.json
    project_manager.save_seed(project_id, data.get('seed_text', ''))
    return jsonify({'success': True})


@app.route('/api/project/<project_id>/generate-lyrics', methods=['POST'])
def api_generate_lyrics(project_id):
    """API: Generate lyrics from seed using GPT-4o."""
    try:
        project = project_manager.load_project(project_id)
        data = request.json or {}
        
        seed_text = data.get('seed_text') or project.get('seed_text', '')
        
        if not seed_text:
            return jsonify({'error': 'Seed text required'}), 400
        
        result = llm_client.generate_lyrics(
            seed_text=seed_text,
            genre=project.get('genre', 'trap'),
            bpm=project.get('bpm', 140),
            mood=project.get('mood', 'aggressive'),
            tags=project.get('tags', [])
        )
        
        if not result.success:
            return jsonify({'error': result.error}), 500
        
        scores = score_lyrics(result.lyrics, project)
        
        version = project_manager.save_iteration(
            project_id=project_id,
            lyrics=result.lyrics,
            scores=scores,
            gpt4o_response=result.raw_response,
            notes="Initial generation from seed"
        )
        
        return jsonify({
            'success': True,
            'version': version,
            'lyrics': result.lyrics,
            'scores': scores,
            'model': result.model,
            'tokens_used': result.tokens_used
        })
        
    except Exception as e:
        logger.error(f"Generate lyrics failed: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/project/<project_id>/iterate', methods=['POST'])
def api_iterate_lyrics(project_id):
    """API: Iterate on lyrics based on scoring feedback."""
    try:
        project = project_manager.load_project(project_id)
        data = request.json or {}
        
        current_lyrics = data.get('lyrics')
        if not current_lyrics and project.get('iterations'):
            latest = project['iterations'][-1]
            current_lyrics = latest.get('lyrics', '')
        
        if not current_lyrics:
            return jsonify({'error': 'No lyrics to iterate on'}), 400
        
        current_scores = data.get('scores', {})
        if not current_scores and project.get('iterations'):
            latest = project['iterations'][-1]
            current_scores = latest.get('scores', {})
        
        recommendations = generate_recommendations(current_scores)
        
        result = llm_client.iterate_lyrics(
            current_lyrics=current_lyrics,
            scores=current_scores,
            recommendations=recommendations,
            genre=project.get('genre', 'trap'),
            bpm=project.get('bpm', 140)
        )
        
        if not result.success:
            return jsonify({'error': result.error}), 500
        
        new_scores = score_lyrics(result.lyrics, project)
        
        version = project_manager.save_iteration(
            project_id=project_id,
            lyrics=result.lyrics,
            scores=new_scores,
            gpt4o_response=result.raw_response,
            notes=f"Iteration based on: {', '.join(recommendations[:3])}"
        )
        
        return jsonify({
            'success': True,
            'version': version,
            'lyrics': result.lyrics,
            'scores': new_scores,
            'recommendations_applied': recommendations,
            'model': result.model
        })
        
    except Exception as e:
        logger.error(f"Iterate lyrics failed: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/project/<project_id>/score', methods=['POST'])
def api_score_lyrics(project_id):
    """API: Score lyrics using analysis agents."""
    try:
        project = project_manager.load_project(project_id)
        data = request.json or {}
        
        lyrics = data.get('lyrics', '')
        if not lyrics:
            return jsonify({'error': 'Lyrics required'}), 400
        
        scores = score_lyrics(lyrics, project)
        recommendations = generate_recommendations(scores)
        
        return jsonify({
            'success': True,
            'scores': scores,
            'recommendations': recommendations
        })
        
    except Exception as e:
        logger.error(f"Score lyrics failed: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/project/<project_id>/approve', methods=['POST'])
def api_approve_lyrics(project_id):
    """API: Approve seed composition for audio generation.
    
    Can approve either:
    1. From form fields (prompt_text, lyrics_text, etc) directly
    2. From an existing iteration version
    """
    try:
        project = project_manager.load_project(project_id)
        data = request.json or {}
        
        prompt_text = data.get('prompt_text', '') or project.get('prompt_text', '')
        lyrics_text = data.get('lyrics_text', '') or project.get('lyrics_text', '')
        neuro_effects = data.get('neuro_effects', '') or project.get('neuro_effects', '')
        neurochemical_effects = data.get('neurochemical_effects', '') or project.get('neurochemical_effects', '')
        musical_effects = data.get('musical_effects', '') or project.get('musical_effects', '')
        
        version = data.get('version')
        if not version and project.get('iterations'):
            version = project['iterations'][-1]['version']
            iteration = project['iterations'][-1]
            if not lyrics_text:
                lyrics_text = iteration.get('lyrics', '')
        
        if not prompt_text.strip() and not lyrics_text.strip():
            return jsonify({'error': 'Please provide at least a prompt/description or lyrics'}), 400
        
        api_payload = build_api_payload(
            project=project,
            prompt_text=prompt_text,
            lyrics_text=lyrics_text,
            neuro_effects=neuro_effects,
            neurochemical_effects=neurochemical_effects,
            musical_effects=musical_effects
        )
        
        project_manager.approve_seed_composition(
            project_id=project_id,
            api_payload=api_payload,
            prompt_text=prompt_text,
            lyrics_text=lyrics_text,
            neuro_effects=neuro_effects,
            neurochemical_effects=neurochemical_effects,
            musical_effects=musical_effects
        )
        
        return jsonify({
            'success': True,
            'version': version or 'direct',
            'api_payload': api_payload
        })
        
    except Exception as e:
        logger.error(f"Approve failed: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/project/<project_id>/preview-payload', methods=['POST'])
def api_preview_payload(project_id):
    """API: Preview the API payload before generation (no approval)."""
    try:
        project = project_manager.load_project(project_id)
        data = request.json or {}
        
        prompt_text = data.get('prompt_text', '') or project.get('prompt_text', '')
        lyrics_text = data.get('lyrics_text', '') or project.get('lyrics_text', '')
        neuro_effects = data.get('neuro_effects', '') or project.get('neuro_effects', '')
        neurochemical_effects = data.get('neurochemical_effects', '') or project.get('neurochemical_effects', '')
        musical_effects = data.get('musical_effects', '') or project.get('musical_effects', '')
        
        if not lyrics_text and project.get('iterations'):
            lyrics_text = project['iterations'][-1].get('lyrics', '')
        
        api_payload = build_api_payload(
            project=project,
            prompt_text=prompt_text,
            lyrics_text=lyrics_text,
            neuro_effects=neuro_effects,
            neurochemical_effects=neurochemical_effects,
            musical_effects=musical_effects
        )
        
        return jsonify({
            'success': True,
            'api_payload': api_payload,
            'estimated_cost_usd': 0.075
        })
        
    except Exception as e:
        logger.error(f"Preview payload failed: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/optimize-seed', methods=['POST'])
def api_optimize_seed():
    """API: Optimize seed composition fields using GPT-4o."""
    try:
        data = request.json or {}
        
        result = llm_client.optimize_seed(
            prompt_text=data.get('prompt_text', ''),
            lyrics_text=data.get('lyrics_text', ''),
            neuro_effects=data.get('neuro_effects', ''),
            neurochemical_effects=data.get('neurochemical_effects', ''),
            musical_effects=data.get('musical_effects', ''),
            genre=data.get('genre', 'trap'),
            mood=data.get('mood', 'aggressive'),
            bpm=int(data.get('bpm', 140)),
            tags=data.get('tags', '')
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Seed optimization failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/project/<project_id>/generate-audio', methods=['POST'])
def api_generate_audio(project_id):
    """API: Generate audio using Sonauto (requires explicit approval)."""
    try:
        project = project_manager.load_project(project_id)
        
        if project.get('status') != 'approved':
            return jsonify({
                'error': 'Lyrics must be approved before generating audio. Use the Approve button first.'
            }), 400
        
        approved_payload = project.get('approved_payload', {}).get('payload', {})
        if not approved_payload:
            return jsonify({'error': 'No approved payload found'}), 400
        
        return jsonify({
            'success': True,
            'message': 'Audio generation would be triggered here',
            'payload': approved_payload,
            'note': 'Full Sonauto integration pending - this shows the approved payload'
        })
        
    except Exception as e:
        logger.error(f"Generate audio failed: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/magic-fill', methods=['POST'])
def api_magic_fill():
    """API: Magic Fill - Auto-populate all form fields using GPT-4o."""
    try:
        data = request.json or {}
        
        partial_inputs = {
            'name': data.get('name', ''),
            'genre': data.get('genre', ''),
            'bpm': data.get('bpm'),
            'mood': data.get('mood', ''),
            'prompt_text': data.get('prompt_text', ''),
            'lyrics_text': data.get('lyrics_text', ''),
            'tags': data.get('tags', ''),
            'concept': data.get('concept', '')
        }
        
        partial_inputs = {k: v for k, v in partial_inputs.items() if v}
        
        context_text = data.get('context', '')
        
        result = llm_client.magic_fill(
            partial_inputs=partial_inputs,
            context_text=context_text
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Magic fill failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/project/<project_id>/analyze/<analysis_type>', methods=['POST'])
def api_analyze_lyrics(project_id, analysis_type):
    """API: On-demand agent invocation for specific analysis types."""
    valid_types = ['rhyme', 'flow', 'meme', 'trend', 'comprehensive']
    if analysis_type not in valid_types:
        return jsonify({'error': f'Invalid analysis type. Valid: {valid_types}'}), 400
    
    try:
        project = project_manager.load_project(project_id)
        data = request.json or {}
        
        lyrics = data.get('lyrics', '')
        if not lyrics and project.get('iterations'):
            lyrics = project['iterations'][-1].get('lyrics', '')
        
        if not lyrics:
            return jsonify({'error': 'No lyrics to analyze'}), 400
        
        algo_scores = score_lyrics(lyrics, project)
        
        gpt_analysis = llm_client.analyze_with_gpt(
            lyrics=lyrics,
            analysis_type=analysis_type,
            scores=algo_scores
        )
        
        console_logs = generate_console_output(analysis_type, algo_scores, gpt_analysis)
        
        return jsonify({
            'success': True,
            'analysis_type': analysis_type,
            'algorithmic_scores': algo_scores,
            'gpt_analysis': gpt_analysis,
            'console_logs': console_logs
        })
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/field-help/<field_name>', methods=['GET'])
def api_field_help(field_name):
    """API: Get comprehensive help content for a specific field."""
    try:
        from apex_engine.config.knowledge_base import get_field_help_content
        from apex_engine.config.ui_text_config import FIELD_HELP, AGENT_DESCRIPTIONS
        
        comprehensive_help = get_field_help_content(field_name)
        
        if comprehensive_help and comprehensive_help.get('sections'):
            return jsonify({
                'success': True, 
                'help': comprehensive_help,
                'has_rich_content': True
            })
        elif field_name in FIELD_HELP:
            return jsonify({
                'success': True, 
                'help': FIELD_HELP[field_name],
                'has_rich_content': False
            })
        elif field_name in AGENT_DESCRIPTIONS:
            return jsonify({
                'success': True, 
                'help': AGENT_DESCRIPTIONS[field_name],
                'has_rich_content': False
            })
        else:
            return jsonify({'success': False, 'error': 'Field not found'}), 404
            
    except Exception as e:
        logger.error(f"Field help failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tag-explorer', methods=['GET'])
def api_tag_explorer():
    """API: Get full Sonauto tag taxonomy for the Tag Explorer modal."""
    try:
        from apex_engine.config.knowledge_base import get_tag_explorer_data
        return jsonify({
            'success': True,
            'taxonomy': get_tag_explorer_data()
        })
    except Exception as e:
        logger.error(f"Tag explorer failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/field-context/<field_name>', methods=['GET'])
def api_field_context(field_name):
    """API: Get knowledge context for AI field optimization."""
    try:
        from apex_engine.config.knowledge_base import get_field_context
        context = get_field_context(field_name)
        return jsonify({
            'success': True,
            'context': context
        })
    except Exception as e:
        logger.error(f"Field context failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/optimize-field', methods=['POST'])
def api_optimize_field():
    """API: Optimize a specific form field using GPT with agent analysis context."""
    try:
        data = request.json
        project_id = data.get('project_id')
        field_name = data.get('field_name')
        current_value = data.get('current_value', '')
        console_logs = data.get('console_logs', [])
        metrics = data.get('metrics', {})
        
        if not project_id or not field_name:
            return jsonify({'error': 'project_id and field_name are required'}), 400
        
        project = project_manager.load_project(project_id)
        
        if field_name not in FIELD_AGENT_MAPPING:
            return jsonify({'error': f'Unknown field: {field_name}'}), 400
        
        analysis_context = {
            'console_logs': console_logs,
            'metrics': metrics
        }
        
        project_context = {
            'genre': project.get('genre', 'trap'),
            'bpm': project.get('bpm', 140),
            'mood': project.get('mood', 'aggressive')
        }
        
        result = llm_client.optimize_field(
            field_name=field_name,
            current_value=current_value,
            analysis_context=analysis_context,
            project_context=project_context
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Field optimization failed: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/run-full-analysis', methods=['POST'])
def api_run_full_analysis():
    """API: Run comprehensive analysis on lyrics and return detailed console output."""
    try:
        data = request.json
        project_id = data.get('project_id')
        lyrics = data.get('lyrics')
        
        if not project_id:
            return jsonify({'error': 'project_id is required'}), 400
        
        project = project_manager.load_project(project_id)
        
        if not lyrics:
            lyrics = project.get('lyrics_text', '')
            if project.get('iterations'):
                lyrics = project['iterations'][-1].get('lyrics', '') or lyrics
        
        if not lyrics:
            return jsonify({'error': 'No lyrics to analyze'}), 400
        
        result = generate_detailed_console_output(lyrics, project)
        
        return jsonify({
            'success': True,
            'console_logs': result['console_logs'],
            'metrics': result['metrics']
        })
        
    except Exception as e:
        logger.error(f"Full analysis failed: {e}")
        return jsonify({'error': str(e)}), 500


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
