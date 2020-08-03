import subprocess

import atexit
from flask import Flask

from .config import Config
from .commands import create_tables
from .extensions import db,jobmanager
from .models import Jobs
from .routes.main import main 

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    
    jobmanager.init_app(app)
    jobmanager.start()

    app.register_blueprint(main)
    app.cli.add_command(create_tables)

    atexit.register(lambda: jobmanager.shutdown())

    return app
    