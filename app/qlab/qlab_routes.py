"""Routes for the Flask web application handling QLab control via OSC."""
import logging
import datetime
from flask import(
    render_template,
    request,
    jsonify,
    url_for
)
from flask_login import login_required, current_user
from pythonosc.udp_client import SimpleUDPClient
from app.functions import group_required, get_setting
from .qlab_forms import QlabForm
from . import qlab_bp # pylint: disable=cyclic-import

log = logging.getLogger(__name__)

currentDT = datetime.datetime.now()
ver = currentDT.strftime("%Y-%m-%d-%H:%M:%S")

@qlab_bp.route('/', methods=['GET', 'POST'])
@login_required
@group_required("qlab")
def qlab_control():
    """QLab Control page route."""
    form = QlabForm()
    return render_template(
        'qlab/qlab.html', 
        title='QLab Control',
        site_name=get_setting('name'),
        form=form,
        version=ver,
        main_menu='qlab'
    )


@qlab_bp.route('/qlabAJAX', methods=['POST', 'GET'])
@login_required
@group_required("qlab")
def qlab_remote_ajax():
    """QLab control via AJAX route."""
    if current_user.is_authenticated:
        output_result = 1
        this_text = "All Cues stopped"
        ip = str(get_setting('qlab_ip'))
        port = int(get_setting('qlab_port'))
        client = SimpleUDPClient(ip, port)
        action = request.get_json()['action']
        if action == 'fire_qlab_cue':
            cue_number = str(request.get_json()['cue_number'])
            message = '/cue/'+cue_number+'/start'
            this_text = 'Cue '+cue_number+' has been triggered'
        elif action == 'stop_qlab_cue':
            cue_number = str(request.get_json()['cue_number'])
            message = '/cue/' + cue_number + '/stop'
            this_text = 'Cue ' + cue_number + ' has been stopped'
        else:
            message = '/'+action
        client.send_message(message, 1)
        if action == 'go':
            this_text = 'GO button pressed'
    else:
        output_result = 0
        this_text = url_for("index")
    return jsonify({
        'text': this_text,
        'result': output_result
    })
