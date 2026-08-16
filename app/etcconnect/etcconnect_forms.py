"""Build the webpages"""

from flask_wtf import FlaskForm
from wtforms import (
    IntegerField,
    SelectField,
    DecimalField,
    SubmitField
)

from wtforms.widgets import NumberInput

class ETCForm(FlaskForm):
    """ETC_Control Form"""

    choose_channel_address = SelectField('Choose Channel, Address or Cue',
        choices=[
            ('channel', 'Channel'),
            ('address', 'Address'),
            ('cue', 'Cue')
        ],
        render_kw={
            'data_role': 'mode',
            'class':
                'w3-border-black w3-round '
        }
    )

    channel_number = IntegerField('Channel',
        render_kw={
            'data-role': 'target',
            'class':
                'w3-border-black w3-round '
        },
        widget=NumberInput(min=0, max=1000)
    )

    relative_channel_level = IntegerField('Level', id='set_level',
        render_kw={
            'data-role': 'channel_level',
            'class':
                'w3-border-black w3-round '
        },
        widget=NumberInput(min=0, max=1000)
    )

    cue = DecimalField('Cue', id='cue',
        render_kw={
            'data-role': 'cue_level',
            'class':
                'w3-border-black w3-round '
        },
        widget=NumberInput(
                min=1.0,
                max=1000
            )
    )

    channel_at_full = SubmitField('Channel @ Full',
            render_kw= {
                'data-action': 'set_level_full',
                'data-channel': 'Channel @ Full',
                'data-address':  'Address @ Full',
                'class':
                    'etc_action '
                    'w3-button '
                    'w3-blue '
                    'w3-round '
                    'w3-hover-aqua '
                    'w3-large ' 
            }
        )


    add_etc_api_command = SubmitField('Add ETC API Command',
            render_kw={
                'class':
                    'admin_action '
                    'w3-button '
                    'w3-blue '
                    'w3-round '
                    'w3-hover-aqua '
                    'w3-small '
                    'w3-show '
                }
            )
