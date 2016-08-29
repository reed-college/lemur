# activate our virtualenv
activate_this = "/home/lemur/lemur/venv/bin/activate_this.py"
execfile(activate_this, dict(__file__=activate_this))

# prepend our path
import sys
sys.path.insert(0, "/home/lemur/lemur")

# populate the db with superadmins
from lemur import db
from lemur import models as m
from lemur.find_and_get import (user_exists, get_role)
ds = db.session
def add_user(id, name, role_name):
    if not user_exists(id):
        role = ds.query(m.Role).filter(m.Role.name==role_name).one()
        user = m.User(id=id,name=name,role=role)
        ds.add(user)
        ds.commit()


# initialize db by creating tables and add roles and users
def initialize_db():
    db.create_all()
    m.Role.insert_roles()
    add_user('boothr','Carey Booth','SuperAdmin')
    add_user('zhongzi','Ziyuan Zhong','SuperAdmin')
    add_user('howelle','Erin Howell','SuperAdmin')


initialize_db()

# wsgi hook
from lemur import app as application
