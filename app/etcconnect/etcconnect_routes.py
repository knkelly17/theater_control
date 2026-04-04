"""Routes for the Flask web application handling lighting and QLab control via OSC."""
import datetime
from flask import render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from pythonosc.udp_client import SimpleUDPClient
from werkzeug.security import generate_password_hash, check_password_hash
from app import app
from .etcconnect_forms import ETCForm
from . import etcconnect_bp
from systems import etc_ip, etc_port


app.secret_key = app.config['SECRET_KEY']
app.dbconnection = app.config['DBCONNECTION']


currentDT = datetime.datetime.now()
ver = currentDT.strftime("%Y-%m-%d-%H:%M:%S")

@etcconnect_bp.route('/', methods=['GET', 'POST'])
@login_required
def etcconnect_control():
    """Lighting Control page route."""
    form = ETCForm()
    return render_template('etcconnect/etcconnect.html', title='Lighting Control', form=form, version=ver)


@etcconnect_bp.route('/channelSetAJAX', methods=['POST', 'GET'])
@login_required
def channel_set_full_out():
    """Channel level setting via AJAX route."""
    ip = str(etc_ip)
    port = int(etc_port)
    client = SimpleUDPClient(ip, port)
    level = request.form['level']
    chan_id = request.form['chan_id']
    message = "/eos/chan/" + chan_id + "/"
    client.send_message(message, level)
    this_text = 'Channel '+chan_id+' is @ '+request.form['level']
    return jsonify({'text': this_text})

@etcconnect_bp.route('/cueFireAJAX', methods=['POST', 'GET'])
@login_required
def cue_fire():
    """Channel level setting via AJAX route."""
    ip = str(etc_ip)
    port = int(etc_port)
    client = SimpleUDPClient(ip, port)
    cue_number = request.form['cue_number']
    message = "/eos/cue/fire"
    client.send_message(message, cue_number)
    this_text = 'Cue '+cue_number+' is active'
    return jsonify({'text': this_text})


@etcconnect_bp.route('/addressSetAJAX', methods=['POST', 'GET'])
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

