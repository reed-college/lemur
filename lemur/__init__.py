# File for initializing the application and set up global variables(app, db)
import logging
from logging.handlers import RotatingFileHandler
from configparser import ConfigParser

# Third-party libraries
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
# Flask Login Manager allows for multiple users with different access
# rights
from flask.ext.login import LoginManager
CONFIG_FILE = 'config.cfg'
KEY_FILE = 'secret_key.cfg'


# Instantiate the application and initializes the login manager.
def create_app(secret_key, config):
    app = Flask(__name__)
    app.config.update(SECRET_KEY=secret_key['key']['SECRET_KEY'], SQLALCHEMY_DATABASE_URI=config['app']['SQLALCHEMY_DATABASE_URI'],
                      DEBUG=config['app']['DEBUG'])

    login_manager = LoginManager()
    login_manager.session_protection = config['login_manager']['SESSION_PROTECTION']
    login_manager.login_view = config['login_manager']['LOGIN_VIEW']
    login_manager.init_app(app)

    return (login_manager, app)


# Log errors that occur when the app is not in debug mode
def log_errors(app, config):
    filepath = config['logger']['FILEPATH']
    level = config['logger']['LEVEL']
    # Handler we choose depends on whether the app is deployed on Herok
    file_handler = RotatingFileHandler(filepath,
                                       'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.addHandler(file_handler)
    file_handler.setLevel(level)
    app.logger.setLevel(level)
    app.logger.info('lemur startup')


# Read configuration
config = ConfigParser()
secret_key = ConfigParser()
config.read(CONFIG_FILE)
secret_key.read(KEY_FILE)
student_api_url = secret_key['key']['STUDENT_API_URL']
class_api_url = secret_key['key']['CLASS_API_URL']
login_manager, app = create_app(secret_key, config)
db = SQLAlchemy(app)

# These imports are useful. They help to avoid cyclic import
from lemur import views, models
log_errors(app, config)
