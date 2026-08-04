
'''Profile blueprint for user authentication and profile management.'''
from flask import Blueprint

# 1. Define the blueprint object
# 'qlab' is the name used for url_for (e.g., url_for('qlab.login'))
tech_director_bp = Blueprint(
        'tech_director', __name__,
        template_folder='templates',
        static_folder='static'
    )

# 2. Import routes at the BOTTOM to prevent circular imports
# This ensures profile_bp is defined before routes try to import it
from . import tech_director_routes # pylint: disable=wrong-import-position
