"""Routes top level functions."""
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from flask import Flask, render_template, request, jsonify, redirect, url_for, current_app
from flask_login import login_required
# from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
# import config
# from app import app
from app.extensions import login_manager
from app.functions import (
    get_db,
    get_setting,
    get_site_settings,
    get_db_value
)

# app.config.from_object(Config)
# app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=120)
#app.config['REMEMBER_COOKIE_DURATION'] = timedelta(minutes=120)
#app.dbconnection = app.config['DBCONNECTION']

#app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)

#app.site_settings = get_site_settings()
# app.settings_last_loaded = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")

#app.settings_last_loaded = get_db_value("MAX(timestamp)", "settings", "1")

#app.device_last_seen = []




#app.secret_key = config.SECRET_KEY

#app.dbconnection = DBCONNECTION = {
#        'dbhost': config.DBHOST,
#        'dbport': config.DBPORT,
#        'dbuser': config.DBUSER,
#        'dbpassword': config.DBPASSWORD,
#        'dbdatabase': config.DBDATABASE
#    }

#@app.route('/')
#@app.route('/index')
#@login_required
#def index():
#    """Home page route."""
#    return render_template(
#        'index.html', 
#        title='Home',
#        version=ver,
#        site_name=get_setting(current_app.config, 'name'),