'''Serices for processing AV Club Items'''
import logging
from app.google_drive_user import (
    get_credentials,
    read_sheet
)

from app.functions import (
    get_current_academic_year_start
)

from app.tech_director.repositories.tech_director_repositories import (
    AVClubRepository,
    InventoryRepository,
    SkillsRepository,
    TeamRepository
)

from app.tech_director.repositories.student_repositories import StudentRepository

from app.tech_director.repositories.show_repositories import ShowRepository

log = logging.getLogger(__name__)

class AVClubService:
    '''Services for AVClub'''
    @staticmethod
    def assign_student_avclub(data, state):
        '''Assign a student to a group (assignment_type)'''
        assignment_group = "avclub"
        if state == 'new':
            student_id = StudentRepository.add_student(data)
        else:
            student_id = data['student_id']

        insert_data = {
            'student_id':student_id
        }
        new_assignment_id = StudentRepository.add_assignment(insert_data, assignment_group)
        student_details = StudentRepository.get_student_details(student_id)
        student_details[0]['index_id'] = new_assignment_id
        return student_details[0]

    @staticmethod
    def list_avclub_students(active):
        '''Fetches the list of av club members'''
        return AVClubRepository.list_avclub_students(
            active,
            get_current_academic_year_start()
        )

class SkillsService:
    '''Services for Skills and Students_Skills'''
    @staticmethod
    def list_all(status):
        '''Fetches the list of inventory.'''
        return SkillsRepository.list_all(
            status
        )

    @staticmethod
    def add_skill(data):
        '''Add new skill'''
        new_skill_id = SkillsRepository.add_skill(data)
        return {'index_id':new_skill_id}

    @staticmethod
    def update_skill(data):
        '''Update skill info'''
        return SkillsRepository.update_skill(data)

    @staticmethod
    def update_student_skill(data):
        '''Update student skill info'''
        update_data = {
            'student_id':data['index_id'],
            'skill_id':data['field'].replace('skill_',''),
            'level_id':data['value']
        }
        return SkillsRepository.update_student_skill(update_data)
        #return SkillsRepository.update_skill(data)

    @staticmethod
    def list_all_skill_levels():
        '''Fetches the list of teams from the database.'''
        return SkillsRepository.list_all_skill_levels()

    @staticmethod
    def get_student_skills_grid():
        '''build a matrix of students and skills'''
        data = {
            'student_list':AVClubService.list_avclub_students('active'),
            'skill_list':SkillsService.list_all('active'),
            'student_skills':SkillsRepository.get_students_skills_grid()
        }

        columns = []
        grid_skill_ids = set()
        skill_template = {}

        for skill in data['skill_list']:

            skill_id = skill["index_id"]

            if skill["in_grid"] == 1:
                grid_skill_ids.add(skill_id)
                columns.append({
                    "field": f"skill_{skill_id}",
                    "skill_id": skill_id,
                    "title": skill["name"],
                })
            else:
                skill_template[skill_id] = {
                    "skill_id": skill_id,
                    "level_id": None,
                    "achieved_date": None,
                    "assessed_by": None,
                }

        student_skill_lookup = {}

        student_details = {
            student["student_id"]: {
                skill_id: skill.copy()
                for skill_id, skill in skill_template.items()
            }
            for student in data["student_list"]
        }

        for student_skill in data["student_skills"]:
            student_id = student_skill["student_id"]
            skill_id = student_skill["skill_id"]

            if skill_id in grid_skill_ids:
                student_skill_lookup[(student_id, skill_id)] = (
                    student_skill["level_id"]
                )
            elif skill_id in student_details[student_id]:
                student_details[student_id][skill_id].update({
                    "level_id": student_skill["level_id"],
                    "achieved_date": student_skill["achieved_date"],
                    "assessed_by": student_skill["assessed_by"],
                })

        for student_id in student_details:
            student_details[student_id] = list(
                student_details[student_id].values()
            )

        rows = []

        for student in data['student_list']:

            row = {
                "student_id": student["student_id"],
                "name": student["full_name"]
            }

            for skill in data['skill_list']:
                if skill['in_grid'] == 1:
                    skills_id = skill["index_id"]

                    row[f"skill_{skills_id}"] = student_skill_lookup.get(
                        (student["student_id"], skills_id)
                    )

            rows.append(row)

            log.warning (student_details)

        return {
            'columns':columns,
            'rows': rows,
            'student_details': student_details
        }


class TeamService:
    '''Class for specific team items'''
    @staticmethod
    def list_all(active):
        '''Fetches the list of teams from the database.'''
        return TeamRepository.list_all(
            active
        )

    @staticmethod
    def list_all_tech_team(active):
        '''Fetches the list of tech_teams from the database.'''
        return TeamRepository.list_all_tech_teams(
            active
        )

class InventoryService:
    '''Services for Inventory'''

    @staticmethod
    def list_all(status):
        '''Fetches the list of inventory.'''
        return InventoryRepository.list_all(
            status
        )

    @staticmethod
    def list_types(status):
        '''Fetches the list of inventory.'''
        return InventoryRepository.list_types(status)

    @staticmethod
    def add_inventory(data):
        '''Add new inventory'''
        new_inventory_id = InventoryRepository.add_inventory(data)
        return {'index_id':new_inventory_id}

    @staticmethod
    def update_inventory(data):
        '''Update inventory info'''
        return InventoryRepository.update_inventory(data)

    @staticmethod
    def list_inventory_assignments(status):
        '''list inventory assignments'''
        return InventoryRepository.list_inventory_assignments(status)

    @staticmethod
    def assign_student_inventory(data):
        '''Assign a student to a group (assignment_type)'''
        assignment_group = "inventory"

        insert_data = {
            'student_id':data['student_id'],
            'inventory_id':data['inventory_id']
        }
        if 'show_id' in data:
            insert_data['show_id'] = data['show_id']

        new_assignment_id = StudentRepository.add_assignment(insert_data, assignment_group)
        return_row = {
            'index_id': new_assignment_id,
            'status_id': 1
        }
        return return_row


class UploadService:
    '''uploading services'''

    @staticmethod
    def upload_student_gsheet(spreadsheet_id, range_name):
        '''upload sheet and insert into db'''
        creds = get_credentials()
        student_data = read_sheet(creds, spreadsheet_id, range_name)
        columns = student_data[0]
        added = []
        already_exists = []
        for student in student_data[1:]:
            index_id = student[columns.index("index_id")]
            student_exists = StudentRepository.check_for_student(index_id)
            if student_exists:
                # Need to decide if we want updates to come from the google sheet
                data_values = {
                    "index_id": index_id,
                    "email": student[columns.index("email")],
                    "student_num": student[columns.index("student_num")],
                    "first_name": student[columns.index("first_name")],
                    "last_name":student[columns.index("last_name")],
                    "graduation_year": student[columns.index("graduation_year")],
                    "parent_name": student[columns.index("parent_name")],
                    "parent_email": student[columns.index("parent_email")],
                    "preferred_pronouns": student[columns.index("preferred_pronouns")],
                    "school":student[columns.index("school")]
                }
                StudentRepository.update_student(data_values)

                log.warning("Update for %s is  %s", student[columns.index("email")], student_exists)
                already_exists.append(student[columns.index("email")])
            else:
                data_values = {
                    "index_id": student[columns.index("index_id")],
                    "student_num": student[columns.index("student_num")],
                    "first_name": student[columns.index("first_name")],
                    "last_name":student[columns.index("last_name")],
                    "graduation_year": student[columns.index("graduation_year")],
                    "parent_name": student[columns.index("parent_name")],
                    "parent_email": student[columns.index("parent_email")],
                    "preferred_pronouns": student[columns.index("preferred_pronouns")],
                    "email": student[columns.index("email")],
                    "school":student[columns.index("school")]
                }
                this_id = StudentRepository.add_student(data_values)
                log.warning("insert %s with ID %s", student[columns.index("email")], this_id)
                added.append(student[columns.index("email")])


        response = f"{len(added)} were added and {len(already_exists)} already exist."
        return response

    @staticmethod
    def upload_show_assign_gsheet(spreadsheet_id, range_name, show_id):
        '''upload show assignments'''
        creds = get_credentials()
        show_assignments = read_sheet(creds, spreadsheet_id, range_name)
        columns = show_assignments[0]
        added = []
        already_exists = []
        for assignment in show_assignments[1:]:
            if show_id == assignment[columns.index("show_id")]:
                index_id = assignment[columns.index("index_id")]
                record_exists = ShowRepository.check_for_show_assignment(index_id)
                if record_exists:
                    log.warning("Update for %s is  %s", assignment[columns.index("index_id")],
                                record_exists)
                    already_exists.append(index_id)
                else :
                    data_values = {
                        "index_id": index_id,
                        "student_id": assignment[columns.index("student_id")],
                        "show_id": assignment[columns.index("show_id")],
                        "team_id":assignment[columns.index("team_id")],
                        "role_description": assignment[columns.index("role_description")],
                    }
                    #this_id = 2222
                    this_id = StudentRepository.add_assignment(data_values, 'show')
                    log.warning("insert %s with ID %s", show_id, this_id)
                    added.append(index_id)
        response = f"{len(added)} were added and {len(already_exists)} already exist."
        return response
