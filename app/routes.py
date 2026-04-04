"""Routes for the Flask web application handling lighting and QLab control via OSC."""
import datetime
from flask import render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, current_user, login_required, UserMixin
from pythonosc.udp_client import SimpleUDPClient
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from app import app
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


@login_manager.user_loader
def load_user(user_id):
    with get_db(dbconnection=app.dbconnection) as db:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE ID=%s", (user_id,))
        data = cursor.fetchone()
        if data:
            return User(data["ID"], data["username"], data["password_hash"])
        return None


@app.route("/")
@app.route('/index')
@login_required
def index():
    """Home page route."""
    return render_template('index.html', title='Home', version=ver)


@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    form = LoginForm()
    return render_template('admin.html', title='Admin', version=ver, form=form)


