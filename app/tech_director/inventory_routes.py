"""Routes for the Flask web application handling AV Club Administration."""
import logging
import datetime
from mysql.connector import (
    errorcode,
    IntegrityError,
)
from flask import (
    render_template,
    request,
    jsonify)
from flask_login import login_required

from app.functions import (
    get_setting,
    group_required,
)

from .services.show_services import ShowService
from .services.student_services import StudentService
from .services.tech_director_services import InventoryService

from .tech_director_forms import TechDirectorForm


from .tech_director_routes import (
    VALID_STATES
)

from . import tech_director_bp # pylint: disable=cyclic-import

log = logging.getLogger(__name__)

currentDT = datetime.datetime.now()
ver = currentDT.strftime("%Y-%m-%d-%H:%M:%S")

@tech_director_bp.route('/inventory', methods=['GET'])
@login_required
@group_required("tech_director_admin")
def inventory():
    """List Shows"""
    form = TechDirectorForm()
    return render_template(
        'tech_director/inventory.html', 
        form=form,
        version=ver,
        main_menu='tech_director',
        base='inventory',
        sub_base='list_inventory'
    )

@tech_director_bp.route('/inventory_check_out', methods=['GET'])
@login_required
@group_required("tech_director_admin")
def inventory_check_out():
    """List Show Assignment"""
    form = TechDirectorForm()
    exclude = None
    form.student_id.choices = StudentService.get_students_active_names_options(exclude)
    return render_template(
        'tech_director/inventory_check_out.html', 
        site_name=get_setting('name'),
        form=form,
        version=ver,
        main_menu='tech_director',
        base='inventory',
        sub_base='inventory_check_out',
        assignment_group='inventory',
    )


@tech_director_bp.route('/api/list_inventory/<string:status>', methods=['GET'])
@login_required
@group_required("tech_director_admin")
def list_inventory(status):
    '''List all Shows'''
    if status not in (['all', 'active']):
        return jsonify({
            "message": "State (all/active) is missing or invalid."
        }), 422
    all_shows =  InventoryService.list_all(status)
    return jsonify(all_shows)

@tech_director_bp.route('/api/update_inventory', methods=['PUT', 'POST'])
@login_required
@group_required("tech_director_admin")
def update_inventory():
    '''Update inventory details'''
    update_response =  InventoryService.update_inventory(request.get_json())
    return jsonify(update_response)

@tech_director_bp.route('/api/add_inventory', methods=['POST'])
@login_required
@group_required("tech_director_admin")
def add_inventory():
    '''Add inventory'''
    add_response =  InventoryService.add_inventory(request.get_json())
    return jsonify(add_response)

@tech_director_bp.route(
        '/api/list_inventory_assignments/<string:status>/',
        methods=['GET']
    )
@login_required
@group_required("tech_director_admin")
def list_inventory_assignments(status):
    '''Fetches the list of inventory that has been checked out.'''
    if status not in (['all', 'active']):
        return jsonify({
            "message": "State (all/active) is missing or invalid."
        }), 422
    all_students =  InventoryService.list_inventory_assignments(status)
    return jsonify(all_students)

@tech_director_bp.route(
        '/api/sign_out_inventory/<string:state>/',
        methods=['POST', 'PUT']
    )
@login_required
@group_required("tech_director_admin")
def sign_out_inventory(state):
    '''Assign inventory to a student.'''

    if state not in VALID_STATES:
        return jsonify({
            "message": "State (new/existing) is missing or invalid."
        }), 422

    try:
        add_response = ShowService.assign_student_show(
            request.get_json(),
            state
        )
    except IntegrityError as error:
        if error.errno == errorcode.ER_DUP_ENTRY:
            # this contains the actual message: error.msg
            message = "Error completing task.  Contact Administrator."
            if 'email' in error.msg:
                message = "A student with that email address already exists."
            return jsonify({
                "message": message,
                "field": "email",
            }), 409

        log.exception("Database integrity error while creating student")
        return jsonify({
            "message": "The student could not be saved."
        }), 500

    return jsonify(add_response)

@tech_director_bp.route('/api/list_inventory_type_options/', methods=['GET'])
@login_required
@group_required("tech_director_admin")
def list_inventory_type_options():
    '''get a list of teams for drop down selction'''
    all_types =  InventoryService.list_types('active')
    return jsonify(all_types)

@tech_director_bp.route(
        '/api/assign_student_inventory/',
        methods=['POST']
    )
@login_required
@group_required("tech_director_admin")
def assign_student_inventory():
    '''Check out inventory to a student.'''

    try:
        add_response = InventoryService.assign_student_inventory(
            request.get_json()
        )
    except IntegrityError as error:
        if error.errno == errorcode.ER_DUP_ENTRY:
            # this contains the actual message: error.msg
            message = "Error completing task.  Contact Administrator."
            return jsonify({
                "message": message,
                "field": "email",
            }), 409

    return jsonify(add_response)
