"""Build the webpages"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import (
    SubmitField,
    StringField,
    SelectField
)

class TechDirectorForm(FlaskForm):
    """Tech Director Control Form"""

    studentId = SelectField(
        "Choose Student",
        choices=[],
        render_kw={
            'class':
                'submit_assignment_fields '
        })

    firstName = StringField('First Name',
        render_kw={
            'class':
              'submit_assignment_fields '
        })

    lastName = StringField('Last Name',
        render_kw={
            'class':
              'submit_assignment_fields '
        })
    email = StringField('School Email',
        render_kw={
            'class':
              'submit_assignment_fields '
        })

    graduationYear = StringField('Graduation Year (4 digits)',
        render_kw={
            'class':
                'submit_assignment_fields '
        }
    )

    add_student = SubmitField('+ Add Student',
        render_kw={
            'class':
                'admin_action '
                'w3-button '
                'w3-blue '
                'w3-round '
                'w3-hover-aqua '
                'w3-small '
            }
        )

    add_member = SubmitField('+ Add Existing Student',
        render_kw={
            'data-add-member':'existing',
            'class':
                'admin_action '
                'w3-button '
                'w3-blue '
                'w3-round '
                'w3-hover-aqua '
                'w3-small '
            }
        )

    add_new_member = SubmitField('+ Add New Student',
        render_kw={
            'data-add-member':'new',
            'class':
                'admin_action '
                'w3-button '
                'w3-purple '
                'w3-round '
                'w3-hover-aqua '
                'w3-small '
            }
        )

    # DELETE
    submit_student_av = SubmitField('Add to AV Club',
        render_kw={
            'data-submit-av':'submit',
            'class':
                'admin_action '
                'w3-button '
                'w3-blue '
                'w3-round '
                'w3-hover-aqua '
                'w3-small '
            }
        )


    # DELETE
    existing_submit_student_av = SubmitField('Add to AV Club',
        render_kw={
            'data-submit-av':'submit',
            'class':
                'admin_action '
                'w3-button '
                'w3-blue '
                'w3-round '
                'w3-hover-aqua '
                'w3-small '
            }
        )

    see_all_records = SubmitField(
        'See All Records (including inactive)',
        render_kw={
            'data-span-label':'label-all',
            'class':
                'w3-button '
                'w3-aqua '
                'w3-round '
                'w3-hover-aqua '
                'w3-medium '
                'w3-show '
                'active-selector'
        }
    )

    see_active_records = SubmitField(
        'See Active Records Only',
        render_kw={
            'data-span-label':'label-active',
            'class':
                'w3-button '
                'w3-aqua '
                'w3-round '
                'w3-hover-aqua '
                'w3-medium, '
                'w3-hide '
                'active-selector ' 
        }
    )

    google_sheet_id = StringField('Google Sheet ID',
            render_kw={
                "size": "50"
            }
        )

    google_sheet_range = StringField('Google Sheed Range',
            render_kw={
                "size": "50"
            }
        )

    upload_students = SubmitField('Upload And Process',
        render_kw={
            'class':
                'dm7_action '
                'w3-button '
                'w3-blue '
                'w3-round '
                'w3-hover-aqua '
                'w3-small '
            }
        )

    tmix_file = FileField('Select Theatremix File',
        render_kw={
            'class': (
                'actor_upload '
                'w3-small '
            ),
            'accept': '.tmix',
            'required': True
        },
        validators=[
            FileRequired(),
            FileAllowed(['tmix'], 'Only Theatremix Files allowed!')
        ]
    )
