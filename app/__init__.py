from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

from .qlab import qlab_bp
app.register_blueprint(qlab_bp, url_prefix='/qlab')
    
from .profile import profile_bp
app.register_blueprint(profile_bp, url_prefix='/profile')

from .etcconnect import etcconnect_bp
app.register_blueprint(etcconnect_bp, url_prefix='/etcconnect')

from app import routes
