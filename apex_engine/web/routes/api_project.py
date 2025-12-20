"""
API routes for project CRUD and field information.

Routes:
- GET /api/projects: List all projects
- GET/PUT/DELETE /api/project/<id>: Project CRUD
- POST /api/project/<id>/seed: Save seed text
- GET /api/field-help/<name>: Get field help content
- GET /api/tag-explorer: Get Sonauto tag taxonomy
- GET /api/field-context/<name>: Get knowledge context for field
"""

import logging
from flask import Blueprint, request, jsonify
from apex_engine.src.core.project_manager import ProjectManager

api_project_bp = Blueprint('api_project', __name__)
logger = logging.getLogger(__name__)

project_manager = ProjectManager()


@api_project_bp.route('/api/projects', methods=['GET'])
def api_list_projects():
    """API: List all projects."""
    projects = project_manager.list_projects()
    return jsonify(projects)


@api_project_bp.route('/api/project/<project_id>', methods=['GET', 'PUT', 'DELETE'])
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


@api_project_bp.route('/api/project/<project_id>/seed', methods=['POST'])
def api_save_seed(project_id):
    """API: Save seed text."""
    data = request.json
    project_manager.save_seed(project_id, data.get('seed_text', ''))
    return jsonify({'success': True})


@api_project_bp.route('/api/field-help/<field_name>', methods=['GET'])
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


@api_project_bp.route('/api/tag-explorer', methods=['GET'])
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


@api_project_bp.route('/api/field-context/<field_name>', methods=['GET'])
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
