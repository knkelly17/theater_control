from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

from .qlab import qlab_bp
app.register_blueprint(qlab_bp, url_prefix='/qlab')
    
from .profile import profile_bp
app.register_blueprint(profile_bp, url_prefix='/profile')

from app import routes
