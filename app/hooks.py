'''Hooks used throughout the app'''
import threading
from flask import (
    request,
    session
)
from flask_login import current_user
from app.services.device_service import track_device


def register_hooks(app):
    '''Resistering the hooks for the app'''

    @app.before_request
    def log_device():
        if request.remote_addr:
            ip = request.remote_addr
            threading.Thread(
                target=track_device,
                args=(ip,),
                daemon=True
            ).start()

    @app.before_request
    def refresh_session_timeout():
        if current_user.is_authenticated:
            session.permanent = True
            session.modified = True
