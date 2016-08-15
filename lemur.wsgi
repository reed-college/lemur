# activate our virtualenv
activate_this = "/home/lemur/lemur/venv/bin/activate_this.py"
execfile(activate_this, dict(__file__=activate_this))

# prepend our path
import sys
sys.path.insert(0, "/home/lemur/lemur")

# populate the db with first user
from lemur import db
from lemur import models as m
from lemur.find_and_get import (user_exists, get_role)
ds = db.session
def add_first_user(id='boothr', name='Carey Booth', role_name='SuperAdmin'):
    if not user_exists(id):
        superadmin_role = ds.query(m.Role).filter(m.Role.name=='SuperAdmin').one()
        a_user = m.User(id=id,name=name,role=superadmin_role)
        ds.add(a_user)
        ds.commit()


def initialize_db():
    db.create_all()
    m.Role.insert_roles()
    add_first_user()


initialize_db()

# wsgi hook
from lemur import app as application