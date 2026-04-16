from datetime import timedelta
from flask import Flask, session
from config import Config


app = Flask(__name__)
app.config.from_object(Config)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=120)
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(minutes=120)
app.dbconnection = app.config['DBCONNECTION']

from app.functions import get_site_settings

app.site_settings = get_site_settings()

app.site_name=app.site_settings['name']


@app.before_request
def handle_user_activity():
    session.permanent = True

from .qlab import qlab_bp
app.register_blueprint(qlab_bp, url_prefix='/qlab')
    
from .profile import profile_bp
app.register_blueprint(profile_bp, url_prefix='/profile')

from .etcconnect import etcconnect_bp
app.register_blueprint(etcconnect_bp, url_prefix='/etcconnect')

from .admin import admin_bp
app.register_blueprint(admin_bp, url_prefix='/admin')

from app import routes
