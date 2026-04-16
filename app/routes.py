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
    def __init__(self, id, username, password_hash, sessionid=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.sessionid = sessionid

@login_manager.user_loader
def load_user(user_id):
    with get_db(dbconnection=app.dbconnection) as db:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE ID=%s", (user_id,))
        data = cursor.fetchone()
        if data:
            session_id = str(data["username"]) + ":" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            return User(
                data["ID"],
                data["username"],
                data["password_hash"],
                session_id
            )
    return None

@app.route("/")
@app.route('/index')
@login_required
def index():
    """Home page route."""
    return render_template('index.html', title='Home', version=ver, main_menu='index')

@app.route('/update_db_field', methods=['POST'])
@login_required
def update_setting():
    editRow = request.get_json()
    table = editRow['table']
    updateFields = {
        editRow['field']: editRow['value'],
        'sessionid': current_user.sessionid
    }
    updateResult = update_db(table, editRow['ID'], updateFields)
    app.site_settings = get_site_settings()
    app.site_name=app.site_settings['name']
    return jsonify({
        "status": "ok",
        "value": updateResult
    })

@app.route('/insert_db_row', methods=['POST'])
@login_required
def insert_setting():
    insertValues = request.get_json()
    insertRow = insertValues['rowData']
    table = insertValues['table']
    insertRow['sessionid'] = current_user.sessionid
    inserted_id = insert_db(table, insertRow)
    return jsonify({
        "status": "ok",
        "value": inserted_id
    })


