from flask import Blueprint

# 1. Define the blueprint object
# 'etcconnect' is the name used for url_for)
etcconnect_bp = Blueprint('etcconnect', __name__, template_folder='templates', static_folder='static')

# 2. Import routes at the BOTTOM to prevent circular imports
# This ensures etcconnect_bp is defined before routes try to import it
from . import etcconnect_routes
