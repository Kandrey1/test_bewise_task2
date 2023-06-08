from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import ConfigDevelopment

db = SQLAlchemy()


def create_app(config_mode=ConfigDevelopment):
    app = Flask(__name__)
    app.config.from_object(config_mode)

    db.init_app(app)

    return app
