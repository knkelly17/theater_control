"""Routes top level functions."""
from datetime import datetime, timezone
from flask import render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, current_user, login_required, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from app import app
from app.functions import get_db, get_setting, get_site_settings, insert_db, get_db_value

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)

app.site_settings = get_site_settings()
# app.settings_last_loaded = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")

app.settings_last_loaded = get_db_value("MAX(timestamp)", "settings", "1")

app.device_last_seen = []

def track_device(ip):
    for device in app.device_last_seen:
        if device["ip"] == ip:
            device["last_seen"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            break
    else:
        app.device_last_seen.append(
            {
                "ip": ip,
                "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )


app.secret_key = app.config['SECRET_KEY']
app.dbconnection = app.config['DBCONNECTION']

currentDT = datetime.now()
ver = currentDT.strftime("%Y-%m-%d-%H:%M:%S")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, password_hash, groups=None, sessionid=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.sessionid = sessionid
        self.groups = groups or []

    def has_group(self, group_name):
        return group_name in self.groups

@login_manager.user_loader
def load_user(user_id):
    with get_db(dbconnection=app.dbconnection) as db:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE ID=%s", (user_id,))
        user_data = cursor.fetchone()
        if not user_data:
            return None
        
        groups_query = """SELECT g.name
        FROM user_groups g
        JOIN user2group ug ON g.ID = ug.groupID
        WHERE ug.userID = %s"""

        cursor.execute(groups_query, (user_id,))
        groups = [row["name"] for row in cursor.fetchall()]

        # Get the most recent session_id for this user from sessionLog
        cursor.execute("""
            SELECT sessionID FROM sessionLog
            WHERE userID = %s
            ORDER BY sessionID DESC
            LIMIT 1
        """, (user_id,))
        session_data = cursor.fetchone()
        session_id = session_data['sessionID'] if session_data else None
        
        return User(
            user_data["ID"],
            user_data["username"],
            user_data["password_hash"],
            groups,                
            session_id
        )
   
@app.before_request
def log_device():
    if request.remote_addr:
        track_device(request.remote_addr)

@app.route('/')
@app.route('/index')
@login_required
def index():
    """Home page route."""
    return render_template(
        'index.html', 
        title='Home', 
        version=ver,
        site_name=get_setting('name'),
        main_menu='index')



