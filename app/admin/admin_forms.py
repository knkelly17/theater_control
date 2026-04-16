"""Build the webpages"""

from flask_wtf import FlaskForm
from wtforms import (
    SubmitField,
    IntegerField
)

from wtforms.widgets import NumberInput


class AdminForm(FlaskForm):
    update_setting = SubmitField('Update Setting',
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
    
    add_setting = SubmitField('Add Setting',
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
    
    add_user = SubmitField('Add User',
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
                'w3-xlarge '
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
                'w3-xlarge '
            }
        )
