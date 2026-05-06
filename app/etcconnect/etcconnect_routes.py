"""Routes for the Flask web application handling lighting and QLab control via OSC."""
import logging
import datetime
from flask import (
    abort,
    render_template,
    request,
    jsonify,
    url_for,
    current_app)
from flask_login import login_required, current_user
from pythonosc.udp_client import SimpleUDPClient
from app.functions import group_required, get_db, get_setting
from .etcconnect_forms import ETCForm
from . import etcconnect_bp # pylint: disable=cyclic-import

log = logging.getLogger(__name__)

#ETC_IP = str(get_setting(current_app.config,'etc_ip'))
#ETC_PORT = int(get_setting(current_app.config,'etc_port'))


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
        site_name=get_setting(current_app.config,'name'),
        title='Lighting Control',
        form=form,
        version=ver,
        main_menu='etcconnect')


@etcconnect_bp.route('/level_set', methods=['POST', 'GET'])
@login_required
@group_required("etcconnect")
def level_set():
    """Channel/Address level setting or Cue fire."""
    if current_user.is_authenticated:
        ip = str(get_setting(current_app.config,'etc_ip'))
        port = int(get_setting(current_app.config,'etc_port'))
        client = SimpleUDPClient(ip, port)

        mode = request.get_json()['mode']
        target = str(request.get_json()['target'])
        level = str(request.get_json()['level'])

        mode_code = ''
        return_text = ''

        if mode == 'channel':
            mode_code = 'chan'
            return_text = 'Channel ' + target +' is @ '+ level
        elif mode == 'address':
            mode_code = 'addr'
            return_text = 'Address ' + target +' is @ '+ level
        elif mode == 'cue':
            mode_code = mode
            return_text = 'Cue ' + level + ' is active'

        message = "/eos/"+ mode_code + "/" + target + "/"

        client.send_message(message, level)
        etc_result = 1
    else:
        etc_result = 0
        return_text = url_for("index")
    return jsonify({
        'text': return_text,
        'result': etc_result})


@etcconnect_bp.route('/fireCueRest', methods=['POST'])
def fire_cue_rest():
    """Address level setting via REST route."""

    qlab_ext_ip = get_setting(current_app.config,'qlab_ext_ip')
    qlab_ext_key = get_setting(current_app.config,'qlab_ext_key')

    if request.remote_addr != str(qlab_ext_ip):
        log.warning("Unauthorized access attempt from IP %s", request.remote_addr)
        abort(403)

    api_key = request.headers.get('X-Api-Key')

    if api_key != str(qlab_ext_key):
        log.warning("Unauthorized access attempt with API key")
        abort(403)


    # Get JSON data - silent=True prevents 400 on parse failure
    json_data = request.get_json(silent=True)

    if json_data and 'command' in json_data:
        etc_ip = str(get_setting(current_app.config, 'etc_ip'))
        etc_port = int(get_setting(current_app.config, 'etc_port'))
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
        log.info("QLab trigger: %s from %s to %s", command, request.remote_addr, etc_ip)

        return jsonify({
            'text': "Cue fired via REST endpoint with command: " + command,
            'result': 1
        })
    #if not input_command:
    #    return jsonify({'error': 'Missing command parameter'}), 400



    log.info("Cue fired via REST endpoint with command: %s", command)
    log.info("Allowed IP: %s", qlab_ext_ip)
    return jsonify({
        'text': "Cue fired via REST endpoint with command: " + command,
        'result': 1
    })

def get_qlab_command_db(command_name):
    '''Fetch QLab command parameters from the database based on the command name.'''
    with get_db(current_app.config) as db:
        cursor = db.cursor(dictionary=True)
        query = "SELECT * FROM qlab_commands WHERE name = %s and active = 'Y'"
        cursor.execute(query, (command_name,))
        qlab_commands_data = cursor.fetchone()
        return qlab_commands_data
