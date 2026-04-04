"""Routes for the Flask web application handling lighting and QLab control via OSC."""
import datetime
from flask import render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, current_user, login_user, login_required, logout_user, UserMixin
from pythonosc.udp_client import SimpleUDPClient
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from app import app
from .profile_forms import LoginForm
from systems import etc_ip, etc_port, qlab_ip, qlab_port


app.secret_key = app.config['SECRET_KEY']
app.dbconnection = app.config['DBCONNECTION']

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


currentDT = datetime.datetime.now()
ver = currentDT.strftime("%Y-%m-%d-%H:%M:%S")

# --- DATABASE CONNECTION ---
def get_db(dbconnection=app.dbconnection):
    return mysql.connector.connect(
        host=dbconnection['dbhost'],
        user=dbconnection['dbuser'],
        password=dbconnection['dbpassword'],
        database=dbconnection['dbdatabase']
    )



# --- USER CLASS ---
class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

def check_password(this_user, password):
    with get_db(dbconnection=app.dbconnection) as db:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s", (this_user,))
        user_data = cursor.fetchone()
        if not user_data:
            return False
    return check_password_hash(user_data["password_hash"], password)

@login_manager.user_loader
def load_user(user_id):
    with get_db(dbconnection=app.dbconnection) as db:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE ID=%s", (user_id,))
        data = cursor.fetchone()
        if data:
            return User(data["ID"], data["username"], data["password_hash"])
        return None


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
                user = User(user_data["ID"], user_data["username"], user_data["password_hash"])
                login_user(user)
                login_result = 1
                return jsonify({
                    'text': url_for("index"),
                    'login_result': login_result
                    })
                #return redirect(url_for("index"))
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


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = LoginForm()
    return render_template('profile/profile.html', title='Profile', version=ver, form=form)


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

    return jsonify({'text': "Password changed successfully."})

