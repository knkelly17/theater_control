"""Build the webpages"""

from flask_wtf import FlaskForm
from wtforms import (
    SubmitField,
    IntegerField,
    StringField,
    PasswordField
)
from wtforms.validators import DataRequired
from wtforms.widgets import NumberInput

class LoginForm(FlaskForm):
    """Login Form"""
    username = StringField('Username', 
        validators=[DataRequired()],
        render_kw={
            'class':
            'w3-border-black w3-round '
        })
    
    password = PasswordField('Password', validators=[DataRequired()],
        render_kw={
            'class':
            'w3-border-black w3-round '
        })
    
    new_password = PasswordField('New Password', 
        validators=[DataRequired()], 
        render_kw={
        'class':
        'w3-border-black w3-round '
    })

    confirm_password = PasswordField('Confirm New Password', 
        validators=[DataRequired()], 
        render_kw={
        'class':
        'w3-border-black w3-round '
    })

    submit_login = SubmitField('Login', render_kw={
        'class':
            'w3-button '
            'w3-blue '
            'w3-round '
            'w3-hover-aqua '
            'w3-medium '
    })

    submit_change_password = SubmitField('Change Password', render_kw={
        'class':
            'w3-button '
            'w3-blue '
            'w3-round '
            'w3-hover-aqua '
            'w3-medium '
    })

