'''Hooks used throughout the app'''
import threading
from flask import request
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
