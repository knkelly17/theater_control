"""Build the webpages"""

from flask_wtf import FlaskForm
from wtforms import (
    SubmitField,
    IntegerField,
    SelectField
)

from wtforms.widgets import NumberInput

BLUE_BUTTON_CLASS = 'w3-button w3-blue w3-round w3-hover-aqua w3-xlarge'


class ETCForm(FlaskForm):
    """ETC_Control Form"""

    choose_channel_address = SelectField('Choose Channel or Address',
        choices=[
            ('channel', 'Channel'),
            ('address', 'Address')
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

    relative_channel_number = IntegerField('Channel',
        render_kw={
            'data-role': 'target',
            'class':
                'w3-border-black w3-round '
        },
        widget=NumberInput(min=0, max=1000)
    )

    channel_full = SubmitField('Channel @ Full',
        render_kw={
            'data-action': 'set_channel_full',
            'class':
                'channel_set_button '
                'w3-button w3-blue '
                'w3-round w3-hover-aqua '
                'w3-xlarge '
        }
    )

    channel_out = SubmitField('Channel @ Out',
        render_kw={
            'data-action': 'set_channel_out',
            'class':
                'channel_set_button '
                'w3-button '
                'w3-blue '
                'w3-round '
                'w3-hover-aqua '
                'w3-xlarge '
        }
    )

    relative_channel_level = IntegerField('Level', id='set_level',
        render_kw={
            'data-role': 'level',
            'class':
                'w3-border-black w3-round '
        },
        widget=NumberInput(min=0, max=1000)
    )

    channel_level_set = SubmitField('Set Channel Level',
        render_kw={
            'data-action': 'set_level',
            'data-channel': 'Set Channel Level',
            'data-address': 'Set Address Level',
            'class':
                'etc_action'
                'channel_set_button '
                'w3-button '
                'w3-blue '
                'w3-round '
                'w3-hover-aqua '
                'w3-xlarge '
        }
    )

    address = IntegerField('Address',
        render_kw={
            'class':
                'w3-border-black w3-round '
        },
        widget=NumberInput(min=0, max=1000)
    )

    addressLevel = IntegerField('Level',
        render_kw={
            'class':
                'w3-border-black w3-round '
        },
        widget=NumberInput(min=0, max=1000)
    )

    addressLevelButton = SubmitField('Set Address Level',
        render_kw={
            'class':
                'address_set_button '
                'w3-button w3-blue '
                'w3-round '
                'w3-hover-aqua '
                'w3-xlarge '
        }
    )

    cue = IntegerField('Cue', id='cue',
        render_kw={
            'class':
                'w3-border-black w3-round '
        },
        widget=NumberInput(min=0, max=1000)
    )

    fire_cue = SubmitField('Go To Cue',
        render_kw={
            'data-action': 'fire_cue',
            'class': BLUE_BUTTON_CLASS
        }
    )
