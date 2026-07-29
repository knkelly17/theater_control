"""Build the webpages"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import (
    SubmitField,
    IntegerField,
    StringField
)

from wtforms.widgets import NumberInput

class AVClubForm(FlaskForm):
    """AV Club Control Form"""
    add_student = SubmitField('Add Student',
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

    panic = SubmitField('Stop All Cues',
        render_kw={
            'class':
                'qlab_action '
                'w3-button '
                'w3-blue '
                'w3-round '
                'w3-hover-aqua '
                'w3-xxlarge ',
            'data-action': 'panic'
            }
        )

    cue = IntegerField('Cue', id='cue',
        render_kw={
            'class':
                'w3-border-black w3-round '
        },
        widget=NumberInput(min=0, max=1000))

    fire_qlab_cue = SubmitField('Fire Cue',
        render_kw={
            'class':
                'qlab_action '
                'w3-button '
                'w3-blue '
                'w3-round '
                'w3-hover-aqua '
                'w3-xlarge ',
            'data-action': 'fire_qlab_cue'
            }
        )

    stop_qlab_cue = SubmitField('Stop Cue',
        render_kw={
            'class':
                'qlab_action '
                'w3-button '
                'w3-blue '
                'w3-round '
                'w3-hover-aqua '
                'w3-xlarge ',
            'data-action': 'stop_qlab_cue'
            }
        )
