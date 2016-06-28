
# Configuation file
import os
basedir = os.path.abspath(os.path.dirname(__file__))

# Attributes of the database:
CSRF_ENABLED = True
DEBUG = True
# This key will be regenerated and hidden at the end of this project
SECRET_KEY = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
SQLALCHEMY_DATABASE_URI = 'postgres://localhost/lemur'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')