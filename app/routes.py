"""Routes for the Flask web application handling lighting and QLab control via OSC."""
import datetime
from flask import render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, current_user, login_required, UserMixin
from pythonosc.udp_client import SimpleUDPClient
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from app import app
from app.forms import ETCForm, QlabForm, LoginForm
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


@app.route("/")
@app.route('/index')
@login_required
def index():
    """Home page route."""
    return render_template('index.html', title='Home', version=ver)


@app.route('/channel_set', methods=['GET', 'POST'])
@login_required
def channel_set():
    """Lighting Control page route."""
    form = ETCForm()
    return render_template('channelSet.html', title='Lighting Control', form=form, version=ver)


@app.route('/channelSetAJAX', methods=['POST', 'GET'])
@login_required
def channel_set_full_out():
    """Channel level setting via AJAX route."""
    ip = str(etc_ip)
    port = int(etc_port)
    client = SimpleUDPClient(ip, port)
    level = request.form['level']
    if level == 'cue':
        cue_number = request.form['cue_number']
        message = "/eos/cue/fire"
        client.send_message(message, cue_number)
        this_text = 'Cue '+cue_number+' is active'
    else:
        chan_id = request.form['chan_id']
        message = "/eos/chan/" + chan_id + "/"
        client.send_message(message, level)
        this_text = 'Channel '+chan_id+' is @ '+request.form['level']
    return jsonify({'text': this_text})


@app.route('/addressSetAJAX', methods=['POST', 'GET'])
@login_required
def address_set_full_out():
    """Address level setting via AJAX route."""
    ip = str(etc_ip)
    port = int(etc_port)
    client = SimpleUDPClient(ip, port)
    level = request.form['level']
    addr_id = request.form['addr_id']
    message = "/eos/addr/" + addr_id + "/"
    client.send_message(message, level)
    this_text = 'Address '+addr_id+' is @ '+request.form['level']
    return jsonify({'text': this_text})

@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    form = LoginForm()
    return render_template('admin.html', title='Admin', version=ver, form=form)


