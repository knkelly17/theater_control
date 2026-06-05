"""Build the webpages"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import (
    SubmitField,
    IntegerField
)

from wtforms.widgets import NumberInput

class Dm7Form(FlaskForm):
    """DM7 Control Form"""
    add_actor = SubmitField('Add actor',
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

    upload_actors = SubmitField('Upload And Process',
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
