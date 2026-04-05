from datetime import timedelta
from flask import Flask, session
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(minutes=10)

@app.before_request
def handle_user_activity():
    session.permanent = True

from .qlab import qlab_bp
app.register_blueprint(qlab_bp, url_prefix='/qlab')
    
from .profile import profile_bp
app.register_blueprint(profile_bp, url_prefix='/profile')

from .etcconnect import etcconnect_bp
app.register_blueprint(etcconnect_bp, url_prefix='/etcconnect')

from app import routes
