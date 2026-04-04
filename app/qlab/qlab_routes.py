"""Routes for the Flask web application handling lighting and QLab control via OSC."""
import datetime
from flask import render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from pythonosc.udp_client import SimpleUDPClient
from werkzeug.security import generate_password_hash, check_password_hash
from app import app
from .qlab_forms import QlabForm
from . import qlab_bp
from systems import qlab_ip, qlab_port


app.secret_key = app.config['SECRET_KEY']
app.dbconnection = app.config['DBCONNECTION']


currentDT = datetime.datetime.now()
ver = currentDT.strftime("%Y-%m-%d-%H:%M:%S")

@qlab_bp.route('/', methods=['GET', 'POST'])
@login_required
def qlab_control():
    """QLab Control page route."""
    form = QlabForm()
    return render_template('qlab/qlab.html', title='QLab Control', form=form, version=ver)


@app.route('/qlabAJAX', methods=['POST', 'GET'])
@login_required
def qlab_remote_ajax():
    """QLab control via AJAX route."""
    this_text = "All Cues stopped"
    ip = str(qlab_ip)
    port = int(qlab_port)
    client = SimpleUDPClient(ip, port)
    action = request.form['action']
    if action == 'fire_qlab_cue':
        cue_number = request.form['cue_number']
        message = '/cue/'+cue_number+'/start'
        this_text = 'Cue '+cue_number+' has been triggered'
    elif action == 'stop_qlab_cue':
        cue_number = request.form['cue_number']
        message = '/cue/' + cue_number + '/stop'
        this_text = 'Cue ' + cue_number + ' has been stopped'
    else:
        message = '/'+action
    client.send_message(message, 1)
    if action == 'go':
        this_text = 'GO button pressed'
    return jsonify({'text': this_text})

