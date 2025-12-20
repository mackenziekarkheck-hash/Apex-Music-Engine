"""
View routes for APEX Engine - HTML page rendering.

Routes:
- /: Dashboard with project list
- /project/new: Create new project form
- /project/<id>: Project workspace
"""

from flask import Blueprint, render_template, request, redirect, url_for
from apex_engine.src.core.project_manager import ProjectManager

views_bp = Blueprint('views', __name__)

project_manager = ProjectManager()


@views_bp.route('/')
def index():
    """Dashboard - list all projects."""
    projects = project_manager.list_projects()
    return render_template('index.html', projects=projects)


@views_bp.route('/project/new', methods=['GET', 'POST'])
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
        return redirect(url_for('views.project_workspace', project_id=config['id']))
    
    return render_template('new_project.html')


@views_bp.route('/project/<project_id>')
def project_workspace(project_id):
    """Project workspace - main editing interface."""
    try:
        project = project_manager.load_project(project_id)
        return render_template('workspace.html', project=project)
    except ValueError as e:
        return render_template('error.html', error=str(e)), 404
