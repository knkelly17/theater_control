"""Routes for the Flask web application handling DM7 control via OSC."""
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
from app.functions import (
    get_db,
    #get_db_value,
    get_setting,
    group_required,
    update_db,
    insert_db
)
from .dm7_forms import Dm7Form
from . import dm7_bp # pylint: disable=cyclic-import

log = logging.getLogger(__name__)

currentDT = datetime.datetime.now()
ver = currentDT.strftime("%Y-%m-%d-%H:%M:%S")

@dm7_bp.route('/', methods=['GET', 'POST'])
@login_required
@group_required("dm7")
def dm7_control():
    """DM7 Control page route."""
    form = Dm7Form()
    return render_template(
        'dm7/dm7.html', 
        title='DM7 Control',
        site_name=get_setting(current_app.config, 'name'),
        form=form,
        version=ver,
        main_menu='dm7'
    )

@dm7_bp.route('/actors', methods=['POST', 'GET'])
@login_required
@group_required("dm7")
def admin_actors():
    """Admin Groups page route."""
    contents = "Admin Groups"
    form = Dm7Form()
    return render_template(
        'dm7/actors.html', 
        title='Admin Tasks',
        sub_title='Actors',
        site_name=get_setting(current_app.config,'name'),
        form=form,
        version=ver,
        main_menu='dm7',
        base='actors',
        page_content=contents
    )

@dm7_bp.route('/get_actors', methods=['POST', 'GET'])
@login_required
def get_actors():
    '''Fetches the list of actors from the database and returns it as JSON.'''
    actors = get_actors_db()
    return actors

def get_actors_db():
    '''Fetches the list of actors from the database.'''
    with get_db(current_app.config) as db:
        cursor = db.cursor(dictionary=True)
        actor_fields = 'ID, name, year, notes, active'
        query = "SELECT " + actor_fields + " FROM actors ORDER BY name"
        cursor.execute(query)
        actors_data = cursor.fetchall()
        return actors_data

@dm7_bp.route('/mic_checks', methods=['POST', 'GET'])
@login_required
@group_required("dm7")
def mic_checks():
    """Admin Settings page route."""
    form = Dm7Form()
    return render_template(
        'dm7/mic_checks.html', 
        form=form,
        title='DM7 Control',
        sub_title='Mic Checs',
        site_name=get_setting(current_app.config, 'name'),
        version=ver,
        main_menu='dm7',
        base='mic_checks',
        page_content="TDB"
    )

@dm7_bp.route('/update_db_field', methods=['POST'])
@login_required
@group_required("dm7")
def update_field_db():
    '''Update a specific field in the specified table for the given ID. 
    The sessionid of the current user is automatically included in the update.'''
    edit_row = request.get_json()
    table = edit_row['table']
    update_fields = {
        edit_row['field']: edit_row['value'],
        'sessionid': current_user.sessionid
    }
    update_result = update_db(current_app.config, table, edit_row['ID'], update_fields)
    current_app.settings_last_loaded = currentDT.strftime("%Y-%m-%d-%H:%M:%S")
    return jsonify({
        "status": "ok",
        "value": update_result
    })

@dm7_bp.route('/update_channel', methods=['POST'])
@login_required
@group_required("dm7")
def update_channel():
    '''Update a channel setting'''
    ip = str(get_setting(current_app.config,'dm7_ip'))
    port = int(get_setting(current_app.config,'dm7_port'))
    log.warning("DM7 IP: %s", ip)
    client = SimpleUDPClient(ip, port)
    parameters = request.get_json()
    log.warning(parameters['channel'])
    log.warning(parameters['field'])
    log.warning(int(parameters['value']))
    message = ""
    if parameters['field'] == "on":
        message = "/yosc:req/set/MIXER:Current/InCh/Fader/On/" + str(parameters['channel'])
    elif parameters['field'] == "cue":
        message = "/yosc:req/set/MIXER:Current/Cue/On/"+str(parameters['channel'])+"/1"
    log.warning (message)
    client.send_message(message, int(parameters['value']))
    #/yosc:req/set/MIXER:Current/InCh/Fader/On/1 0
    return jsonify({
        "status": "ok",
        "value": "testing"
    })


@dm7_bp.route('/insert_db_row', methods=['POST'])
@login_required
@group_required("dm7")
def insert_row_db():
    '''Insert a new row into the specified table 
    with the provided data. The sessionid of the current user 
    is automatically included in the inserted data.'''

    insert_values = request.get_json()
    insert_row = insert_values['rowData']
    table = insert_values['table']
    insert_row['sessionid'] = current_user.sessionid
    inserted_id = insert_db(current_app.config, table, insert_row)
    current_app.settings_last_loaded = currentDT.strftime("%Y-%m-%d-%H:%M:%S")
    return jsonify({
        "status": "ok",
        "value": inserted_id
    })

@dm7_bp.route('/get_actor_channels', methods=['POST', 'GET'])
@login_required
@group_required("dm7")
def get_actor_channels():
    '''Get Channel and actor name if assigned'''
    with get_db(current_app.config) as db:
        cursor = db.cursor(dictionary=True)
        query = "SELECT c.ID, c.channel, a.name as actor " \
                "FROM `channels` c " \
                "LEFT JOIN actors a on " \
	            "c.actor = a.ID;"
        log.warning(query)
        cursor.execute(query)
        actors_data = cursor.fetchall()
        return jsonify(actors_data)
