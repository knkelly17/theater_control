'''
This module initializes the Flask application, 
sets up configuration, 
and registers blueprints for different parts of'''

from datetime import timedelta
import logging
from flask import Flask, session
import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
)

# pylint: disable=too-few-public-methods
class Config:
    '''Base configuration class'''
    SECRET_KEY = config.SECRET_KEY
    DBCONNECTION = config.DBCONNECTION

app = Flask(__name__)
app.config.from_object(Config)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=120)
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(minutes=120)
app.dbconnection = app.config['DBCONNECTION']


@app.before_request
def handle_user_activity():
    '''Set session to permanent and reset the lifetime on each request.'''
    session.permanent = True

from .qlab import qlab_bp # pylint: disable=wrong-import-position
app.register_blueprint(qlab_bp, url_prefix='/qlab')

from .profile import profile_bp # pylint: disable=wrong-import-position
app.register_blueprint(profile_bp, url_prefix='/profile')

from .etcconnect import etcconnect_bp # pylint: disable=wrong-import-position
app.register_blueprint(etcconnect_bp, url_prefix='/etcconnect')

from .admin import admin_bp # pylint: disable=wrong-import-position
app.register_blueprint(admin_bp, url_prefix='/admin')

from app import routes # pylint: disable=wrong-import-position
