"""Routes for the Flask web application handling QLab control via OSC."""
import logging
import datetime
from flask import(
    render_template,
    request,
    jsonify
)

from flask_login import login_required

from app.functions import group_required, get_setting

from .services.qlab_services import (
    QlabService
)

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


@qlab_bp.route('/api/qlab_cue_action', methods=['POST', 'GET'])
@login_required
@group_required("qlab")
def qlab_remote_ajax():
    """QLab control via AJAX route."""
    result = QlabService.activate_cue(request.get_json())
    return jsonify(result)
