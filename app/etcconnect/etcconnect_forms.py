"""Build the webpages"""

from flask_wtf import FlaskForm
from wtforms import (
    IntegerField,
    SelectField,
    DecimalField
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
