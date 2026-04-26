"""Routes for the Flask web application handling lighting and QLab control via OSC."""
import logging
import datetime
from flask import abort, abort, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from pythonosc.udp_client import SimpleUDPClient
from werkzeug.security import generate_password_hash, check_password_hash
from app import app
from app.functions import group_required, get_db_setting, get_db
from .etcconnect_forms import ETCForm
from . import etcconnect_bp
# from systems import etc_ip, etc_port

log = logging.getLogger(__name__)

etc_ip = str(get_db_setting('etc_ip'))
etc_port = int(get_db_setting('etc_port'))


app.secret_key = app.config['SECRET_KEY']
app.dbconnection = app.config['DBCONNECTION']


currentDT = datetime.datetime.now()
ver = currentDT.strftime("%Y-%m-%d-%H:%M:%S")

@etcconnect_bp.route('/', methods=['GET', 'POST'])
@login_required
@group_required("etcconnect")
def etcconnect_control():
    """Lighting Control page route."""
    form = ETCForm()
    return render_template(
        'etcconnect/etcconnect.html', 
        site_name=app.site_name, 
        title='Lighting Control', 
        form=form, 
        version=ver, 
        main_menu='etcconnect')


@etcconnect_bp.route('/channelSetAJAX', methods=['POST', 'GET'])
@login_required
@group_required("etcconnect")
def channel_set_full_out():
    """Channel level setting via AJAX route."""
    if current_user.is_authenticated:
        ip = str(etc_ip)
        port = int(etc_port)
        client = SimpleUDPClient(ip, port)
        level = request.form['level']
        chan_id = request.form['chan_id']
        message = "/eos/chan/" + chan_id + "/"
        client.send_message(message, level)
        output_result = 1
        this_text = 'Channel '+chan_id+' is @ '+request.form['level']
    else:
        output_result = 0
        this_text = url_for("index")
    return jsonify({
        'text': this_text,
        'result': output_result})

@etcconnect_bp.route('/cueFireAJAX', methods=['POST', 'GET'])
@login_required
@group_required("etcconnect")
def cue_fire():
    """Channel level setting via AJAX route."""
    if current_user.is_authenticated:
        ip = str(etc_ip)
        port = int(etc_port)
        client = SimpleUDPClient(ip, port)
        cue_number = request.form['cue_number']
        message = "/eos/cue/fire"
        client.send_message(message, cue_number)
        output_result = 1
        this_text = 'Cue '+cue_number+' is active'
    else:
        output_result = 0
        this_text = url_for("index")
    return jsonify({
        'text': this_text,
        'result': output_result})


@etcconnect_bp.route('/addressSetAJAX', methods=['POST', 'GET'])
@login_required
@group_required("etcconnect")
def address_set_full_out():
    """Address level setting via AJAX route."""
    if current_user.is_authenticated:
        ip = str(etc_ip)
        port = int(etc_port)
        client = SimpleUDPClient(ip, port)
        level = request.form['level']
        addr_id = request.form['addr_id']
        message = "/eos/addr/" + addr_id + "/"
        client.send_message(message, level)
        output_result = 1
        this_text = 'Address '+addr_id+' is @ '+request.form['level']
    else:
        output_result = 0
        this_text = url_for("index")
    return jsonify({
        'text': this_text, 
        'result': output_result
    })

@etcconnect_bp.route('/fireCueRest', methods=['POST'])
def fire_cue_rest():
    """Address level setting via REST route."""
    
    qlab_ext_ip = get_db_setting('qlab_ext_ip')
    qlab_ext_key = get_db_setting('qlab_ext_key')

    if request.remote_addr != str(qlab_ext_ip):
        log.warning(f"Unauthorized access attempt from IP")
        abort(403)

    api_key = request.headers.get('X-Api-Key')

    if api_key != str(qlab_ext_key):
        log.warning(f"Unauthorized access attempt with API key")
        abort(403)
    
    
    # Get JSON data - silent=True prevents 400 on parse failure
    json_data = request.get_json(silent=True)
    
    if json_data and 'command' in json_data:
        etc_ip = str(get_db_setting('etc_ip'))
        etc_port = int(get_db_setting('etc_port'))
        command = json_data['command']
        qlab_parameters = get_qlab_command_db(command)
        if qlab_parameters:
            client = SimpleUDPClient(etc_ip, etc_port)
            message = '/eos'
            param1 = qlab_parameters.get('parameter_1')
            param2 = qlab_parameters.get('parameter_2')
            param3 = qlab_parameters.get('parameter_3')
            if param1:
                message += '/' + param1
            if param2:
                message += '/' + param2

            client.send_message(message, param3)
        log.info(f"QLab trigger: {command} from {request.remote_addr} to {etc_ip}")
    
        return jsonify({
            'text': "Cue fired via REST endpoint with command: ",
            'result': 1
        })
    #if not input_command:
    #    return jsonify({'error': 'Missing command parameter'}), 400
   

    
    log.info("Cue fired via REST endpoint with command: " + command)
    log.info("Allowed IP: " + str(qlab_ext_ip))
    return jsonify({
        'text': "Cue fired via REST endpoint with command: " + command,
        'result': 1
    })

def get_qlab_command_db(command_name):
    with get_db(dbconnection=app.dbconnection) as db:
        cursor = db.cursor(dictionary=True)
        query = "SELECT * FROM qlab_commands WHERE name = %s and active = 'Y'" 
        cursor.execute(query, (command_name,))
        qlab_commands_data = cursor.fetchone()
        return qlab_commands_data