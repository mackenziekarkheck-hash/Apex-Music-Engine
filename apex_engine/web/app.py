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
from apex_engine.src.core.llm_client import LLMClient
from apex_engine.src.agents.lyrical.lyrical_architect import LyricalArchitectAgent
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
    """API: Approve lyrics and preview API payload."""
    try:
        project = project_manager.load_project(project_id)
        data = request.json or {}
        
        version = data.get('version')
        if not version and project.get('iterations'):
            version = project['iterations'][-1]['version']
        
        if not version:
            return jsonify({'error': 'No iteration to approve'}), 400
        
        iteration = next(
            (i for i in project.get('iterations', []) if i['version'] == version),
            None
        )
        if not iteration:
            return jsonify({'error': f'Iteration v{version} not found'}), 404
        
        api_payload = build_api_payload(project, iteration['lyrics'])
        
        project_manager.approve_iteration(
            project_id=project_id,
            version=version,
            api_payload=api_payload
        )
        
        return jsonify({
            'success': True,
            'version': version,
            'api_payload': api_payload
        })
        
    except Exception as e:
        logger.error(f"Approve lyrics failed: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/project/<project_id>/preview-payload', methods=['POST'])
def api_preview_payload(project_id):
    """API: Preview the API payload before generation (no approval)."""
    try:
        project = project_manager.load_project(project_id)
        data = request.json or {}
        
        lyrics = data.get('lyrics', '')
        if not lyrics and project.get('iterations'):
            lyrics = project['iterations'][-1].get('lyrics', '')
        
        api_payload = build_api_payload(project, lyrics)
        
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


def build_api_payload(project: dict, lyrics: str) -> dict:
    """Build the Sonauto API payload for review."""
    genre = project.get('genre', 'trap')
    mood = project.get('mood', 'aggressive')
    tags = project.get('tags', [genre, 'hip hop', 'rap'])
    
    prompt = f"High-fidelity, studio-quality {genre} track. {mood.title()} energy with professional mixing."
    
    if genre == 'phonk':
        prompt += " Heavy distorted 808s, cowbell melodies, Memphis rap influence."
    elif genre == 'drill':
        prompt += " Dark atmosphere, sliding 808s, aggressive delivery."
    elif genre == 'boom bap' or genre == 'boom_bap':
        prompt += " Classic hip hop production, sample-based, vinyl warmth."
    elif genre == 'trap':
        prompt += " Hard-hitting 808s, hi-hat rolls, modern trap production."
    
    return {
        'prompt': prompt,
        'tags': tags,
        'lyrics': lyrics,
        'bpm': project.get('bpm', 140),
        'prompt_strength': project.get('prompt_strength', 2.0),
        'balance_strength': project.get('balance_strength', 0.7),
        'output_format': 'wav',
        'instrumental': False,
        'num_songs': 1
    }


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
