"""Routes for the Flask web application handling lighting and QLab control via OSC."""
import datetime
from flask import render_template, request, jsonify, redirect, url_for
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.routes import User
from app.functions import get_db, get_setting
from config import DBCONNECTION
from .profile_forms import LoginForm
from . import profile_bp


currentDT = datetime.datetime.now()
ver = currentDT.strftime("%Y-%m-%d-%H:%M:%S")
session_start_time = currentDT.strftime("%Y%m%d%H%M%S")


def check_password(this_user, password):
    '''Check user password'''
    with get_db(dbconnection=DBCONNECTION) as db:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s", (this_user,))
        user_data = cursor.fetchone()
        if not user_data:
            return False
    return check_password_hash(user_data["password_hash"], password)


@profile_bp.route("/login", methods=["GET", "POST"])
def login():
    """Login page route."""
    form = LoginForm()
    if request.method == "POST":
        with get_db(dbconnection=DBCONNECTION) as db:
            cursor = db.cursor(dictionary=True)

            cursor.execute("SELECT * FROM users WHERE username=%s", (request.form["username"],))
            user_data = cursor.fetchone()
            if user_data and check_password_hash(
                    user_data["password_hash"],
                    request.form["password"]
                ):
                session_id = str(user_data["username"]) + ":" + request.form["timestamp"]
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
                login_result = 1
                return jsonify({
                    'text': url_for("index"),
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
    return redirect(url_for("index"))


@profile_bp.route("/", methods=["GET", "POST"])
@login_required
def profile():
    '''Profile page route.'''
    form = LoginForm()
    return render_template(
        'profile/profile.html', 
        title='Profile',
        site_name=get_setting('name'),
        version=ver,
        form=form,
        main_menu='profile')


@profile_bp.route("/change_password", methods=["POST"])
@login_required
def change_password():
    '''Change password route.'''
    current_password = request.form["current_password"]
    this_user = current_user.username

    if not check_password(this_user, current_password):
        return jsonify({'text': "Current password is incorrect."})
    new_password = request.form["new_password"]
    confirm_password = request.form["confirm_password"]

    if new_password != confirm_password:
        return jsonify({'text': "Passwords do not match."})

    hashed_password = generate_password_hash(new_password)

    with get_db(dbconnection=DBCONNECTION) as db:
        cursor = db.cursor()
        cursor.execute(
            "UPDATE users SET password_hash=%s WHERE ID=%s", 
            (hashed_password, current_user.id)
        )
        db.commit()

    logout_user()
    login_result = 1
    return jsonify({
        'text': url_for("login"),
        'login_result': login_result
        }
    )
