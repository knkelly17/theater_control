"""Start the App"""
import logging
from datetime import timedelta
from flask import Flask
from app.extensions import login_manager
from app.hooks import register_hooks

def create_app(config_object="app.config.Config"):
    """Create the app"""
    app = Flask(__name__)

    # Load config
    app.config.from_object(config_object)

    #app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=1)
    #app.config['REMEMBER_COOKIE_DURATION'] = timedelta(minutes=1)

    # --- Initialize extensions here ---
    # e.g. db.init_app(app), login_manager.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'profile.login' # Where to redirect unauthorized users


    # --- Register blueprints ---
    # pylint: disable=import-outside-toplevel
    from app.admin import admin_bp
    from app.etcconnect import etcconnect_bp
    from app.profile import profile_bp
    from app.qlab import qlab_bp
    from app.main import main_bp
    from app.dm7 import dm7_bp

    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(etcconnect_bp, url_prefix="/etcconnect")
    app.register_blueprint(profile_bp, url_prefix="/profile")  # maybe handles "/login"
    app.register_blueprint(qlab_bp, url_prefix="/qlab")
    app.register_blueprint(main_bp, url_prefix="/")
    app.register_blueprint(dm7_bp, url_prefix="/dm7")

    # register hooks
    register_hooks(app)


    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )


    return app
