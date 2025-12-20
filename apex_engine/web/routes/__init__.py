"""
Flask Blueprint registration for APEX Engine routes.
"""

from .views import views_bp
from .api_project import api_project_bp
from .api_actions import api_actions_bp
from .helpers import (
    score_lyrics,
    generate_recommendations,
    generate_console_output,
    generate_detailed_console_output,
    build_api_payload
)

__all__ = [
    'views_bp',
    'api_project_bp',
    'api_actions_bp',
    'score_lyrics',
    'generate_recommendations',
    'generate_console_output',
    'generate_detailed_console_output',
    'build_api_payload'
]
