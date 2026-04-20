"""Routes for the Flask web application handling lighting and QLab control via OSC."""
import datetime
from flask import render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, current_user, login_required, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import app
from app.functions import get_db, update_db, get_site_settings, insert_db

app.secret_key = app.config['SECRET_KEY']
app.dbconnection = app.config['DBCONNECTION']

currentDT = datetime.datetime.now()
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
   

@app.route('/')
@app.route('/index')
@login_required
def index():
    """Home page route."""
    return render_template(
        'index.html', 
        title='Home', 
        version=ver,
        site_name=app.site_name,
        main_menu='index')



