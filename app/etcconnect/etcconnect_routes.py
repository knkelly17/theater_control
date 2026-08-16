"""Routes for the Flask web application handling lighting and QLab control via OSC."""
import logging
import datetime
from flask import (
    render_template,
    request,
    jsonify,
)
from flask_login import login_required

from app.functions import group_required, get_setting

from app.forms import SiteForm
from .etcconnect_forms import ETCForm

from .services.etcconnect_services import (
    ETCConnectService
)
from . import etcconnect_bp # pylint: disable=cyclic-import

log = logging.getLogger(__name__)


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
        site_name=get_setting('name'),
        title='Lighting Control',
        form=form,
        version=ver,
        main_menu='etcconnect')

@etcconnect_bp.route('/api/level_set', methods=['POST'])
@login_required
@group_required("etcconnect")
def level_set():
    """Channel/Address level setting or Cue fire."""

    result = ETCConnectService.set_level(request.get_json())
    return jsonify(result)

@etcconnect_bp.route('/etc_api_commands', methods=['POST', 'GET'])
@login_required
@group_required("admin")
def etc_api_commands():
    """Admin Settings page route."""
    return render_template(
        'etcconnect/etc_api_commands.html', 
        form=ETCForm(),
        site_form = SiteForm(),
        title='Admin Tasks',
        sub_title='ETC API Commands',
        site_name=get_setting('name'),
        version=ver,
        main_menu='admin',
        base='etc_api_commands'
    )

@etcconnect_bp.route('/api/get_etc_api_commands', methods=['GET']) #this is probably a post
@login_required
@group_required("admin")
def get_qlab_commands():
    '''Fetches the list of ETC API commands from the database and returns it as JSON.'''
    qlab_commands = ETCConnectService.list_all()
    return jsonify (qlab_commands)

@etcconnect_bp.route('/api/update_etc_api_command', methods=['PUT'])
@login_required
@group_required("admin")
def update_etc_api_command():
    '''Update command details'''
    update_response =  ETCConnectService.update_command(request.get_json())
    return jsonify(update_response)

@etcconnect_bp.route('/api/add_etc_api_command', methods=['POST'])
@login_required
@group_required("admin")
def add_etc_api_command():
    '''Add a command'''
    add_response =  ETCConnectService.add_command(request.get_json())
    return jsonify(add_response)

@etcconnect_bp.route('/api/fireCueRest', methods=['POST'])
def fire_cue_rest():
    """Address level setting via REST route."""

    cue_response = ETCConnectService.fire_cue_rest(
        request.remote_addr,
        request.headers.get('X-Api-Key'),
        request.get_json(silent=True)
    )

    return jsonify(cue_response)
