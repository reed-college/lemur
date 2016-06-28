# Bio Data Collector
# File for initializing the application when run
import logging
from logging import WARNING
from logging.handlers import RotatingFileHandler
from configparser import ConfigParser
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
# Flask Login Manager allows for multiple users with different access
# rights
from flask.ext.login import LoginManager
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CsrfProtect


CONFIG_FILE = 'config.cfg'


# Instantiate the application and initializes the login manager.
def create_app(config):
    app = Flask(__name__)
    app.config.update(CSRF_ENABLED=config['app']['CSRF_ENABLED'],
                      SECRET_KEY=config['app']['SECRET_KEY'],
                      SQLALCHEMY_DATABASE_URI=config['app']['SQLALCHEMY_DATABASE_URI'],
                      DEBUG=config['app']['DEBUG'])

    login_manager = LoginManager()
    login_manager.session_protection = config['login_manager']['SESSION_PROTECTION']
    login_manager.login_view = config['login_manager']['LOGIN_VIEW']
    login_manager.init_app(app)

    # enable CSRF protection
    csrf = CsrfProtect()
    csrf.init_app(app)

    Bootstrap(app)
    return (login_manager, csrf, app)


def setup_time(config):
    class_time = config['class_time_info']['CLASS_TIME'].split(',')
    current_time = config['class_time_info']['CURRENT_TIME']
    return (class_time, current_time)


# Log errors that occur when the app is not in debug mode
def log_errors(app, config):
    filepath = config['logger']['FILEPATH']
    level = config['logger']['LEVEL']
    file_handler = RotatingFileHandler(filepath,
                                       'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(level)
    file_handler.setLevel(level)
    app.logger.addHandler(file_handler)
    app.logger.info('lemur startup')


# Read configuration
config = ConfigParser()
config.read(CONFIG_FILE)
login_manager, csrf, app = create_app(config)
db = SQLAlchemy(app)
(class_time, current_time) = setup_time(config)

# These imports are useful and they used to avoid cyclic import
from myapp import views, models
log_errors(app, config)