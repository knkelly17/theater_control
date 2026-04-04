"""Build the webpages"""

from flask_wtf import FlaskForm
from wtforms import (
    SubmitField,
    IntegerField
)

from wtforms.widgets import NumberInput


class ETCForm(FlaskForm):
    """ETC_Control Form"""
    channel_full_out = IntegerField('Channel',
        widget=NumberInput(min=0, max=1000),
        render_kw={
            'class':
                'w3-border-black w3-round '
        }
    )

    channelFull = SubmitField('Channel @ Full',
        render_kw={
            'class':
                'channel_set_button '
                'w3-button w3-blue '
                'w3-round w3-hover-aqua '
                'w3-xlarge '
        }
    )

    channelOut = SubmitField('Channel @ Out',
        render_kw={
            'class':
                'channel_set_button '
                'w3-button '
                'w3-blue '
                'w3-round '
                'w3-hover-aqua '
                'w3-xlarge '
        }
    )
    
    channelLevel = IntegerField('Channel', id='channel_level',
        render_kw={
            'class':
                'w3-border-black w3-round '
        },
        widget=NumberInput(min=0, max=1000)
    )

    setLevel = IntegerField('Level', id='set_level',
        render_kw={
            'class':
                'w3-border-black w3-round '
        },
        widget=NumberInput(min=0, max=1000)
    )

    channelLevelButton = SubmitField('Set Channel Level',
        render_kw={
            'class':
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
            'class':
                'w3-button '
                'w3-blue '
                'w3-round '
                'w3-hover-aqua '
                'w3-xlarge '
        }
    )
