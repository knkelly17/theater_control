from flask import Blueprint

# 1. Define the blueprint object
# 'admin' is the name used for url_for (e.g., url_for('admin'))
admin_bp = Blueprint('admin', __name__, template_folder='templates', static_folder='static')

# 2. Import routes at the BOTTOM to prevent circular imports
# This ensures admin_bp is defined before routes try to import it
from . import admin_routes
