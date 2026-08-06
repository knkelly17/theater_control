'''Serices for processing AV Club Items'''
import logging
from app.google_drive_user import (
    get_credentials,
    read_sheet
)

from app.functions import (
    get_current_academic_year_start
)

from ..repositories import tech_director_repository # pylint: disable=relative-beyond-top-level

log = logging.getLogger(__name__)

def upload_student_gsheet(spreadsheet_id, range_name):
    '''upload sheet and insert into db'''
    creds = get_credentials()
    student_data = read_sheet(creds, spreadsheet_id, range_name)
    columns = student_data[0]
    for student in student_data[1:]:
        email = student[columns.index("email")]
        student_exists = tech_director_repository.check_for_student(email)
        data_values = {
            "ID": student[columns.index("indexId")],
            "studentId": student[columns.index("studentId")],
            "firstName": student[columns.index("firstName")],
            "lastName":student[columns.index("lastName")],
            "graduationYear": student[columns.index("graduationYear")],
            "parentName": student[columns.index("parentName")],
            "parentEmail": student[columns.index("parentEmail")],
            "email": student[columns.index("email")],
            "archived": student[columns.index("archived")]
        }
        if student_exists:
            # Need to decide if we want updates to come from the google sheet
            # output = update_student(data_values['ID'], data_values)
            log.warning("Update for %s is  %s", email, student_exists)
        else:
            this_id = tech_director_repository.add_student(data_values)
            log.warning("insert %s with ID %s", email, this_id)

    return columns

def get_students(active):
    '''Fetches the list of students from the database.'''
    data_needed = "all"
    sorted_by = "graduationYear"
    exclude = None
    return tech_director_repository.get_students(
        active,
        get_current_academic_year_start(),
        data_needed,
        sorted_by,
        exclude
    )

def get_students_active():
    '''Fetches the list of students from the database.'''
    data_needed = "all"
    sorted_by = "grade"
    exclude = None
    return tech_director_repository.get_students(
        "Active",
        get_current_academic_year_start(),
        data_needed,
        sorted_by,
        exclude
    )

def get_students_active_names():
    '''Fetches the list of active student names and id's from the database.'''
    data_needed = "fullName"
    sorted_by = "fullName"
    exclude = None
    return tech_director_repository.get_students(
        "Active",
        get_current_academic_year_start(),
        data_needed,
        sorted_by,
        exclude
    )

def get_students_active_names_options(exclude):
    '''Generate a list of active students for a dropdown'''
    data_needed = "fullName"
    sorted_by = "fullName"
    student_object = tech_director_repository.get_students(
        "active",
        get_current_academic_year_start(),
        data_needed,
        sorted_by,
        exclude
    )
    option_list = [('','')]
    for student in student_object:
        this_option = (student['ID'], student['fullName'])
        option_list.append(this_option)
    return option_list

def get_group_members(assignment_group, active):
    '''Fetches the list of av club members'''
    return tech_director_repository.get_group_members(
        assignment_group,
        active,
        get_current_academic_year_start()
    )

def add_existing_student(data):
    '''Add an existing student to the AV Club'''
    insert_data = {
        'studentId':data['studentId']
    }
    inserted_id = tech_director_repository.add_club_member_db(insert_data)
    student_details = tech_director_repository.get_student_details(data['studentId'])
    student_details[0]['indexId'] = inserted_id
    return student_details[0]

def assign_student(data, state, assignment_group):
    '''Assign a student to a group (assignment_type)'''
    if state == 'new':
        student_id = tech_director_repository.add_student(data)
    else:
        student_id = data['studentId']

    insert_data = {
        'studentId':student_id
    }
    new_assignment_id = tech_director_repository.add_assignment(insert_data, assignment_group)
    student_details = tech_director_repository.get_student_details(student_id)
    student_details[0]['indexId'] = new_assignment_id
    return student_details[0]


def add_student(data):
    '''Add a new student'''
    new_student_id = tech_director_repository.add_student(data)
    return {'indexId':new_student_id}

def update_member_info(data):
    '''Update membership info'''
    return tech_director_repository.update_member_info_db(data)

def update_student(data):
    '''Update membership info'''
    return tech_director_repository.update_student(data)
