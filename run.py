# This file is used to migrate database for the app
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
from lemur import app, db


migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
