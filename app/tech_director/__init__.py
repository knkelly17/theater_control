
'''Profile blueprint for user authentication and profile management.'''
from flask import Blueprint

# 1. Define the blueprint object
# 'qlab' is the name used for url_for (e.g., url_for('qlab.login'))
av_club_bp = Blueprint('av_club', __name__, template_folder='templates', static_folder='static')

# 2. Import routes at the BOTTOM to prevent circular imports
# This ensures profile_bp is defined before routes try to import it
from . import av_club_routes # pylint: disable=wrong-import-position
