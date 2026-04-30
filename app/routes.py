"""Routes top level functions."""
from datetime import datetime
from dataclasses import dataclass, field
from flask import render_template, request
from flask_login import LoginManager, login_required, UserMixin
# from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
import config
from app import app
from app.functions import (
    get_db,
    get_setting,
    get_site_settings,
    get_db_value
)

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)

app.site_settings = get_site_settings()
# app.settings_last_loaded = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")

app.settings_last_loaded = get_db_value("MAX(timestamp)", "settings", "1")

app.device_last_seen = []

def track_device(ip):
    '''Tracks the last seen time of a device based on its IP address.'''
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


app.secret_key = config.SECRET_KEY

app.dbconnection = DBCONNECTION = {
        'dbhost': config.DBHOST,
        'dbport': config.DBPORT,
        'dbuser': config.DBUSER,
        'dbpassword': config.DBPASSWORD,
        'dbdatabase': config.DBDATABASE
    }

currentDT = datetime.now()
ver = currentDT.strftime("%Y-%m-%d-%H:%M:%S")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'profile.login'

@dataclass
class User(UserMixin):
    '''User class for Flask-Login'''
    id: int
    username: str
    password_hash: str
    groups: list[str] = field(default_factory=list)
    sessionid: str | None = None

    def has_group(self, group_name):
        '''Check if the user belongs to a specific group.'''
        return group_name in self.groups

@login_manager.user_loader
def load_user(user_id):
    '''Load user from the database by ID.'''
    with get_db() as db:
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
    '''Log all devices that connect'''
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
