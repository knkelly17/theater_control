"""Build the webpages"""

from flask_wtf import FlaskForm
from wtforms import (
    SubmitField,
    IntegerField,
    PasswordField
)
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import NumberInput

class AdminForm(FlaskForm):
    '''Form for admin actions'''

    row_id = IntegerField('Row ID',
            widget=NumberInput(),
            render_kw={
                'readonly': True,
                'hidden': True
            }
    )

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
                'w3-show '
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
                'w3-show '
            }
        )

    add_group = SubmitField('Add Group',
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

    new_password = PasswordField('New Password',
        validators=[
            DataRequired(),
            Length(min=6)
        ],
        render_kw={
        'class':
        'w3-border-black w3-round '
    })

    confirm_password = PasswordField('Confirm New Password',
        validators=[
            DataRequired(),
            EqualTo("new_password", message="Passwords must match")
        ],
        render_kw={
        'class':
        'w3-border-black w3-round '
    })

    admin_change_password = SubmitField('Change Password', render_kw={
        'class':
            'w3-button '
            'w3-blue '
            'w3-round '
            'w3-hover-aqua '
            'w3-medium ',
        'data-action': 'admin_change_password'
    })

    cancel_change_password = SubmitField('Cancel', render_kw={
        'class':
            'w3-button '
            'w3-red '
            'w3-round '
            'w3-hover-pale-red '
            'w3-medium '
    })
