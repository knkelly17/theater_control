"""Routes for the Flask web application handling lighting and QLab control via OSC."""
import logging
import datetime
from urllib.parse import urlparse
from dataclasses import dataclass, field
from flask import(
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    current_app
)

from flask_login import (
        current_user,
        login_user,
        login_required,
        logout_user,
        UserMixin
    )

from werkzeug.security import generate_password_hash, check_password_hash
# from config import DBCONNECTION
from app.extensions import login_manager
from app.functions import get_setting
from app.functions_db import get_db
from .profile_forms import LoginForm
from . import profile_bp # pylint: disable=cyclic-import

log = logging.getLogger(__name__)

currentDT = datetime.datetime.now()
ver = currentDT.strftime("%Y-%m-%d-%H:%M:%S")
session_start_time = currentDT.strftime("%Y%m%d%H%M%S")


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

def check_password(this_user, password):
    '''Check user password'''
    with get_db(current_app.config) as db:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s", (this_user,))
        user_data = cursor.fetchone()
        if not user_data:
            return False
    return check_password_hash(user_data["password_hash"], password)

@login_manager.unauthorized_handler
def unauthorized():
    """Return JSON for AJAX auth failures, otherwise redirect to login."""
    # Special case: always redirect for login route to avoid 401 on login attempts
    # if request.endpoint == 'profile.login':
        # return redirect(url_for('profile.login', next=request.url))

    # Detect AJAX requests by X-Requested-With header (standard for jQuery/fetch)
    wants_json = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if wants_json:
        return jsonify({'error': 'login_required'}), 401
    return redirect(url_for('profile.login', next=request.path))


@login_manager.user_loader
def load_user(user_id):
    '''Load user from the database by ID.'''
    with get_db(current_app.config) as db:
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

@profile_bp.route("/login", methods=["GET", "POST"])
def login():
    """Login page route."""
    form = LoginForm()
    if request.method == "POST":
        json_data = request.get_json(silent=True) or {}
        with get_db(current_app.config) as db:
            cursor = db.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM users WHERE username=%s", (json_data.get('username'),)
            )
            user_data = cursor.fetchone()
            if user_data and check_password_hash(
                    user_data["password_hash"],
                    json_data.get('password')
                ):
                session_id = str(user_data["username"]) + ":" + json_data.get('timestamp', '')
                user = User(
                    user_data["ID"],
                    user_data["username"],
                    user_data["password_hash"],
                    session_id
                )
                cursor.execute(
                    "INSERT INTO sessionLog (sessionID, userID) VALUES (%s, %s)", 
                    (session_id, user.id))
                db.commit()
                login_user(user)
                next_page = request.args.get('next') or json_data.get('next')
                if not next_page or urlparse(next_page).netloc != '':
                    next_page = url_for('index')
                login_result = 1
                return jsonify({
                    'text': next_page,
                    'login_result': login_result
                })
            login_result = 0
            this_text = "Invalid username or password. Please try again."
            return jsonify({
                'text': this_text,
                'login_result': login_result
            })
    return render_template(
        "profile/login.html", 
        title="Login",
        session_start_time=session_start_time,
        form=form,
        version=ver
    )

@profile_bp.route("/logout")
@login_required
def logout():
    '''Logout route.'''
    logout_user()
    return redirect(url_for("main.index"))


@profile_bp.route("/", methods=["GET", "POST"])
@login_required
def profile():
    '''Profile page route.'''
    form = LoginForm()
    return render_template(
        'profile/profile.html', 
        title='Profile',
        site_name=get_setting(current_app.config, 'name'),
        version=ver,
        form=form,
        main_menu='profile')


@profile_bp.route("/change_password", methods=["POST"])
@login_required
def change_password():
    '''Change password route.'''
    current_password = request.get_json()['current_password']
    this_user = current_user.username

    if not check_password(this_user, current_password):
        return jsonify({'text': "Current password is incorrect."})
    new_password = request.get_json()['new_password']
    confirm_password = request.get_json()['confirm_password']

    if new_password != confirm_password:
        return jsonify({'text': "Passwords do not match."})

    hashed_password = generate_password_hash(new_password)

    with get_db(current_app.config) as db:
        cursor = db.cursor()
        cursor.execute(
            "UPDATE users SET password_hash=%s WHERE ID=%s", 
            (hashed_password, current_user.id)
        )
        db.commit()

    logout_user()
    login_result = 1
    return jsonify({
        'text': url_for("profile.login"),
        'login_result': login_result
        }
    )
