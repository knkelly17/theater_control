"""Build the webpages"""

from flask_wtf import FlaskForm
from wtforms import (
    SubmitField,
    StringField,
    PasswordField
)
from wtforms.validators import DataRequired, EqualTo, Length

class ChangePasswordForm(FlaskForm):
    '''Change Password Form'''
    current_password = PasswordField("Current Password", validators=[DataRequired()])
    new_password = PasswordField("New Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("new_password", message="Passwords must match")]
    )

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
            'w3-round '
            'w3-blue '
            'w3-hover-aqua '
            'w3-medium ',
        'data-action': 'submit_login'
    })

    submit_change_password = SubmitField('Change Password', render_kw={
        'class':
            'w3-button '
            'w3-blue '
            'w3-round '
            'w3-medium '
            'w3-hover-aqua ',
        'data-action': 'submit_change_password'
    })
