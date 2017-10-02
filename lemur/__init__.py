# You might be thinking: this is a pretty weird place for this to live. If you
# were to look in other modules, in fact, you might pretty quickly spot
# circular imports -- you're entirely right. We've got lots of them.
#
# The problem is that Flask is pretty much built to work this way, if you use
# decorators to define routes (which this app does). Is this gross? Yes. Is it
# fine enough for now? I sure hope so. RMD 2017-10-01

import logging
from logging.handlers import RotatingFileHandler

# Third-party libraries
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
# Flask Login Manager allows for multiple users with different access
# rights
from flask.ext.login import LoginManager

app = Flask(__name__)

logger = logging.getLogger('__name__')

db = SQLAlchemy(app)

app.config.from_envvar('LEMUR_CONFIG')


def create_login_manager(app):
    login_manager = LoginManager()
    login_manager.session_protection = app.config['SESSION_PROTECTION']
    login_manager.login_view = app.config['LOGIN_VIEW']
    login_manager.init_app(app)

    return login_manager


# Log errors that occur when the app is not in debug mode
def log_errors(app):
    filepath = app.config['FILEPATH']
    level = app.config['LEVEL']
    # Handler we choose depends on whether the app is deployed on Heroku
    file_handler = RotatingFileHandler(filepath, 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.addHandler(file_handler)
    file_handler.setLevel(level)
    app.logger.setLevel(level)
    app.logger.info('lemur startup')


login_manager = create_login_manager(app)

# Required to load the actual app routes; must be imported after the "real" app
# is declared.
from lemur import views
