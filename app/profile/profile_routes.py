"""Routes for the Flask web application handling lighting and QLab control via OSC."""
import datetime
from flask import flash, render_template, request, jsonify, redirect, url_for
from flask_login import current_user, login_user, login_required, logout_user
from pythonosc.udp_client import SimpleUDPClient
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from app import app
from app.routes import User
from .profile_forms import LoginForm
from . import profile_bp
from app.functions import get_db


app.secret_key = app.config['SECRET_KEY']
app.dbconnection = app.config['DBCONNECTION']


currentDT = datetime.datetime.now()
ver = currentDT.strftime("%Y-%m-%d-%H:%M:%S")
session_start_time = currentDT.strftime("%Y%m%d%H%M%S")


def check_password(this_user, password):
    with get_db(dbconnection=app.dbconnection) as db:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s", (this_user,))
        user_data = cursor.fetchone()
        if not user_data:
            return False
    return check_password_hash(user_data["password_hash"], password)


@app.route("/", methods=["GET", "POST"])
def login():
    """Login page route."""
    form = LoginForm()
    error_message = None
    if request.method == "POST":
        with get_db(dbconnection=app.dbconnection) as db:
            cursor = db.cursor(dictionary=True)

            cursor.execute("SELECT * FROM users WHERE username=%s", (request.form["username"],))
            user_data = cursor.fetchone()

            if user_data and check_password_hash(user_data["password_hash"], request.form["password"]):
                session_id = str(user_data["username"]) + ":" + session_start_time
                user = User(
                    user_data["ID"], 
                    user_data["username"], 
                    user_data["password_hash"],
                    session_id
                )
                cursor.execute("INSERT INTO sessionLog (sessionID, userID) VALUES (%s, %s)", (session_id, user.id))
                db.commit()
                login_user(user)
                print(current_user.sessionid)
                login_result = 1
                return jsonify({
                    'text': url_for("index"),
                    'login_result': login_result
                    })
            else:
                login_result = 0
                this_text = "Invalid username or password. Please try again."
                return jsonify({
                    'text': this_text,
                    'login_result': login_result
                })

    return render_template("profile/login.html", title="Login", form=form, version=ver)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@profile_bp.route("/", methods=["GET", "POST"])
@login_required
def profile():
    form = LoginForm()
    return render_template(
        'profile/profile.html', 
        title='Profile', 
        site_name=app.site_name, 
        version=ver, 
        form=form, 
        main_menu='profile')


@app.route("/change_password", methods=["POST"])
@login_required
def change_password():
    
    current_password = request.form["current_password"]
    this_user = current_user.username

    if not check_password(this_user, current_password):
        return jsonify({'text': "Current password is incorrect."})
    new_password = request.form["new_password"]
    confirm_password = request.form["confirm_password"]

    if new_password != confirm_password:
        return jsonify({'text': "Passwords do not match."})

    hashed_password = generate_password_hash(new_password)

    with get_db(dbconnection=app.dbconnection) as db:
        cursor = db.cursor()
        cursor.execute("UPDATE users SET password_hash=%s WHERE ID=%s", (hashed_password, current_user.id))
        db.commit()
    

    form = LoginForm()
    logout_user()
    login_result = 1
    return jsonify({
        'text': url_for("login"),
        'login_result': login_result
        }
    )

