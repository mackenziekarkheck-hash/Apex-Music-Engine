"""
APEX Engine Web UI - Flask application factory for song project management.

Uses Blueprint-based routing for maintainability:
- views_bp: HTML page rendering (index, new_project, workspace)
- api_project_bp: Project CRUD and field information endpoints
- api_actions_bp: Generation, analysis, and AI optimization endpoints
"""

import os
import sys
import logging

apex_engine_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, apex_engine_path)
sys.path.insert(0, os.path.dirname(apex_engine_path))

from flask import Flask

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app(config=None):
    """Application factory for APEX Engine Flask app.
    
    Args:
        config: Optional configuration dict to override defaults
        
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'apex-dev-key-change-in-prod')
    
    if config:
        app.config.update(config)
    
    from apex_engine.web.routes import views_bp, api_project_bp, api_actions_bp
    
    app.register_blueprint(views_bp)
    app.register_blueprint(api_project_bp)
    app.register_blueprint(api_actions_bp)
    
    logger.info("APEX Engine Flask app initialized with blueprints")
    
    return app


app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
