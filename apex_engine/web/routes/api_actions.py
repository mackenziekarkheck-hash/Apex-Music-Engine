"""
API routes for actions: lyrics generation, analysis, audio generation, and AI optimization.

Routes:
- POST /api/project/<id>/generate-lyrics: Generate lyrics from seed
- POST /api/project/<id>/iterate: Iterate on lyrics with scoring
- POST /api/project/<id>/score: Score lyrics using agents
- POST /api/project/<id>/approve: Approve lyrics for audio generation
- POST /api/project/<id>/preview-payload: Preview API payload
- POST /api/project/<id>/generate-audio: Generate audio via Fal.ai
- POST /api/project/<id>/analyze/<type>: On-demand analysis
- POST /api/optimize-seed: Optimize seed composition fields
- POST /api/magic-fill: Auto-populate form fields
- POST /api/optimize-field: Optimize individual field with AI
- POST /api/run-full-analysis: Run comprehensive analysis
"""

import logging
from flask import Blueprint, request, jsonify
from apex_engine.src.core.project_manager import ProjectManager
from apex_engine.src.core.llm_client import LLMClient
from apex_engine.src.services.fal_client import FalMusicClient
from apex_engine.src.services.payload_factory import PayloadFactory
from apex_engine.src.services.validators import validate_full_payload
from apex_engine.src.services.optimizer import FieldOptimizer
from .helpers import (
    score_lyrics,
    generate_recommendations,
    generate_console_output,
    generate_detailed_console_output,
    build_api_payload
)

api_actions_bp = Blueprint('api_actions', __name__)
logger = logging.getLogger(__name__)

project_manager = ProjectManager()
llm_client = LLMClient()
fal_client = FalMusicClient()
payload_factory = PayloadFactory()
field_optimizer = FieldOptimizer()


@api_actions_bp.route('/api/project/<project_id>/generate-lyrics', methods=['POST'])
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


@api_actions_bp.route('/api/project/<project_id>/iterate', methods=['POST'])
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


@api_actions_bp.route('/api/project/<project_id>/score', methods=['POST'])
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


@api_actions_bp.route('/api/project/<project_id>/approve', methods=['POST'])
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


@api_actions_bp.route('/api/project/<project_id>/preview-payload', methods=['POST'])
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


@api_actions_bp.route('/api/optimize-seed', methods=['POST'])
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


@api_actions_bp.route('/api/project/<project_id>/generate-audio', methods=['POST'])
def api_generate_audio(project_id):
    """API: Generate audio using Fal.ai MiniMax Music v2 (requires explicit approval)."""
    try:
        project = project_manager.load_project(project_id)
        
        is_approved = (
            project.get('status') == 'approved' or
            project.get('state', {}).get('approval', {}).get('lyrics', {}).get('approved', False)
        )
        
        if not is_approved:
            return jsonify({
                'error': 'Lyrics must be approved before generating audio. Use the Approve button first.'
            }), 400
        
        ui_data = {
            'description': project.get('prompt_text', ''),
            'lyrics': project.get('lyrics_text', ''),
            'neuro_effects': project.get('neuro_effects', ''),
            'neurochemical_targets': project.get('neurochemical_effects', ''),
            'musical_effects': project.get('musical_effects', ''),
            'seed_composition': project.get('seed_composition', '')
        }
        
        fal_payload = payload_factory.construct_payload(ui_data)
        
        prompt = fal_payload.get('input', {}).get('prompt', '')
        lyrics = fal_payload.get('input', {}).get('lyrics_prompt', '')
        validated_prompt, validated_lyrics, issues = validate_full_payload(prompt, lyrics)
        
        fal_payload['input']['prompt'] = validated_prompt
        fal_payload['input']['lyrics_prompt'] = validated_lyrics
        
        result = fal_client.generate_music(fal_payload)
        
        if result.status == 'COMPLETED':
            return jsonify({
                'success': True,
                'request_id': result.request_id,
                'audio_url': result.audio_url,
                'duration': result.duration,
                'validation_issues': issues,
                'payload_used': fal_payload
            })
        else:
            return jsonify({
                'success': False,
                'error': result.error or 'Generation failed',
                'status': result.status,
                'validation_issues': issues
            }), 500
        
    except Exception as e:
        logger.error(f"Generate audio failed: {e}")
        return jsonify({'error': str(e)}), 500


@api_actions_bp.route('/api/magic-fill', methods=['POST'])
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


@api_actions_bp.route('/api/project/<project_id>/analyze/<analysis_type>', methods=['POST'])
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


@api_actions_bp.route('/api/optimize-field', methods=['POST'])
def api_optimize_field():
    """API: Optimize a specific form field using GPT-4o with Fal.ai context."""
    try:
        data = request.json
        project_id = data.get('project_id')
        field_name = data.get('field_name')
        current_value = data.get('current_value', '')
        
        if not field_name:
            return jsonify({'error': 'field_name is required'}), 400
        
        if not current_value.strip():
            return jsonify({
                'success': False,
                'error': 'No text provided to optimize',
                'optimized': current_value
            })
        
        result = field_optimizer.optimize_field(
            field_name=field_name,
            text=current_value
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Field optimization failed: {e}")
        return jsonify({'error': str(e), 'success': False}), 500


@api_actions_bp.route('/api/run-full-analysis', methods=['POST'])
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
