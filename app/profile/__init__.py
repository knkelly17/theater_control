from flask import Blueprint

# 1. Define the blueprint object
# 'qlab' is the name used for url_for (e.g., url_for('qlab.login'))
profile_bp = Blueprint('profile', __name__, template_folder='templates', static_folder='static')

# 2. Import routes at the BOTTOM to prevent circular imports
# This ensures qlab_bp is defined before routes try to import it
from . import profile_routes
