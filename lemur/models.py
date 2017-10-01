# This file contains all the sqlalchemy tables and their relationship
# in the database
# Libraries
# Standard library
from datetime import datetime

# Third-party libraries
from flask.ext.login import UserMixin, AnonymousUserMixin

# Other modules
from lemur.lemur import db, login_manager

# Association tables for Many-To-Many relationships between various tables
association_table_class_user = db.Table('association_class_user',
                                        db.Column('class_id', db.String(128),
                                                  db.ForeignKey('Class.id')),
                                        db.Column('user_id', db.String(64),
                                                  db.ForeignKey('User.id')))
association_table_user_lab = db.Table('association_user_lab',
                                      db.Column('user_id', db.String(64),
                                                db.ForeignKey('User.id')),
                                      db.Column('lab_id', db.String(128),
                                                db.ForeignKey(
                                                    'Lab.id')))
association_table_role_power = db.Table('association_role_power',
                                        db.Column('role_name', db.String(64),
                                                  db.ForeignKey('Role.name')),
                                        db.Column('power_id', db.String(64),
                                                  db.ForeignKey(
                                                      'Power.id')))


# set up class to track the date and time information for an object
class DateTimeInfo(object):
    created_on = db.Column(db.DateTime, default=datetime.now)
    updated_on = db.Column(db.DateTime, default=datetime.now,
                           onupdate=datetime.now)


# A Lab is in reality a form which consists a list of questions(Experiment)
class Lab(db.Model):
    __tablename__ = 'Lab'
    id = db.Column(db.String(128), nullable=False, unique=True,
                   primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    # lab description contained in description variable
    description = db.Column(db.String(4096))
    status = db.Column(db.Enum('Activated', 'Downloadable', 'Unactivated',
                               name='status'))
    # one-to-many: a lab can have multiple experiments
    experiments = db.relationship('Experiment', back_populates='lab',
                                  cascade="all, delete, delete-orphan")
    # Many-to-One: a class can have multiple labs
    class_id = db.Column(db.String(128), db.ForeignKey('Class.id'))
    the_class = db.relationship("Class", back_populates="labs")
    # Many-to-Many: a user can have multiple labs and a lab can have multiple
    # users
    users = db.relationship("User", secondary=association_table_user_lab,
                            back_populates="labs")

    def __repr__(self):
        # Representation of class object in string format
        tpl = ('Lab<id: {id}, name: {name}'
               ', class_id: {class_id},'
               ', description: {description}, status: {status}'
               ', experiments: {experiments}, the_class: {the_class}'
               ', users: {users}>')
        formatted = tpl.format(id=self.id, name=self.name,
                               class_id=self.class_id,
                               description=self.description,
                               status=self.status,
                               experiments=[e.name for e in self.experiments],
                               the_class=self.the_class.id,
                               users=[u.id for u in self.users])
        return formatted


# An experiment represents a question in a lab form
class Experiment(db.Model):
    __tablename__ = 'Experiment'
    id = db.Column(db.String(192), nullable=False, unique=True,
                   primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(1024))
    order = db.Column(db.Integer, nullable=False)
    # Type of value expected for this experiment
    value_type = db.Column(db.Enum('Number', 'Text', name='value_type'))
    # Value range only applies when the type is a number
    value_range = db.Column(db.String(64))
    # Value candidates only applies when the type is text
    value_candidates = db.Column(db.String(512))

    # Many-to-One: a lab can have multiple experiments
    lab_id = db.Column(db.String(128), db.ForeignKey('Lab.id'))
    lab = db.relationship("Lab", back_populates="experiments")

    # One-to-Many: a experiment can have multiple data
    observations = db.relationship('Observation', back_populates='experiment',
                                   cascade="all, delete, delete-orphan")

    def __repr__(self):
        tpl = ('Lab<id: {id}, name: {name}, description: {description}'
               ', order: {order}, value_type: {value_type}'
               ', value_range: {value_range}'
               ', value_candidates: {value_candidates}'
               ', lab_id: {lab_id}, lab:{lab}'
               ', observations: {observations}>')
        formatted = tpl.format(id=self.id, name=self.name,
                               description=self.description,
                               order=self.order,
                               value_type=self.value_type,
                               value_range=self.value_range,
                               value_candidates=self.value_candidates,
                               lab_id=self.lab_id,
                               lab=self.lab.name,
                               observations=[ob.id for ob in self.observations])
        return formatted


# An Observation a group of students' response towards a question(Experiment)
# in a lab
class Observation(db.Model, DateTimeInfo):
    __tablename__ = 'Observation'
    id = db.Column(db.String(320), nullable=False, unique=True,
                   primary_key=True)
    student_name = db.Column(db.String(128), nullable=False)
    datum = db.Column(db.String(512), nullable=False)

    # Many-to-One: an experiment can have mulitple datasets inputted by
    # different students
    experiment_id = db.Column(db.String(192), db.ForeignKey('Experiment.id'))
    experiment = db.relationship("Experiment", back_populates="observations")

    def __repr__(self):
        tpl = ('Observation<experiment_id: {experiment_id}, id: {id},'
               'datum: {datum}>')
        formatted = tpl.format(experiment_id=self.experiment_id, id=self.id,
                               datum=self.datum)
        return formatted


class Class(db.Model):
    __tablename__ = 'Class'
    id = db.Column(db.String(128), nullable=False, unique=True,
                   primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    time = db.Column(db.String(128), nullable=False)
    # Many-to-Many: A Class can have multiple users(both professors and
    # students)
    users = db.relationship("User", secondary=association_table_class_user,
                            back_populates="classes")
    # One-to-Many: A Class can have multiple labs
    labs = db.relationship("Lab", back_populates='the_class')

    def __repr__(self):
        tpl = ('Class<id: {id}, time: {time}, name: {name}, users: {users},'
               'labs: {labs}>')
        formatted = tpl.format(id=self.id, time=self.time,
                               name=self.name,
                               users=[u.name for u in self.users],
                               labs=[lab.name for lab in self.labs])
        return formatted


class User(UserMixin, db.Model):
    __tablename__ = 'User'
    id = db.Column(db.String(64), nullable=False, unique=True, primary_key=True)
    name = db.Column(db.String(128))
    # Many-to-One: A role can have multiple users
    role_name = db.Column(db.String(64), db.ForeignKey('Role.name'))
    role = db.relationship("Role", back_populates="users")
    # Many-to-Many: A User can have multiple classes
    classes = db.relationship("Class", secondary=association_table_class_user,
                              back_populates="users")
    # Many-to-Many: A User can have multiple labs
    labs = db.relationship("Lab", secondary=association_table_user_lab,
                           back_populates="users")

    # Return the ids of all the powers a user has
    def get_power(self):
        return [p.id for p in self.role.powers]

    # can function checks if user is allowed to peform an operation
    def can(self, power):
        return self.role is not None and power in self.get_power()

    def __repr__(self):
        tpl = ('User<id: {id},'
               ' role_name: {role_name}, classes: {classes}, labs: {labs}>')
        formatted = tpl.format(id=self.id,
                               role_name=self.role_name,
                               classes=[c.id for c in self.classes],
                               labs=[l.id for l in self.labs])
        return formatted


# Function for use when user is not logged in
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False


# Associate the LoginManager with the anonymous user class
login_manager.anonymous_user = AnonymousUser


# Function accepts a user id and returns the user object of that id
@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


class Role(db.Model):
    __tablename__ = 'Role'
    name = db.Column(db.String(64), nullable=False, unique=True,
                     primary_key=True)
    # Many-to-Many: A Role can have multiple power; a power can belong to
    # roles
    powers = db.relationship("Power", secondary=association_table_role_power,
                             back_populates="roles")

    # One-to-Many: A Role can have multiple users
    users = db.relationship('User', back_populates='role', lazy='dynamic')

    # For database initialization, no object needed to use this method
    # Load all the Powers and Roles into the database
    @staticmethod
    def insert_roles():
        for p in Permission.all_permissions():
            if db.session.query(Power).filter(Power.id == p).count() == 0:
                db.session.add(Power(id=p))

        roles = {
            'Student': [Permission.DATA_ENTRY],
            'Admin': [
                Permission.DATA_ENTRY,
                Permission.DATA_EDIT,
                Permission.LAB_SETUP,
                Permission.ADMIN
            ],
            'SuperAdmin': [
                Permission.DATA_ENTRY,
                Permission.DATA_EDIT,
                Permission.LAB_SETUP,
                Permission.ADMIN,
                Permission.LAB_MANAGE,
                Permission.USER_MANAGE,
                Permission.SUPERADMIN
            ]
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            for p in roles[r]:
                role.powers.append(db.session.query(Power).filter(
                    Power.id == p
                ).one())

            db.session.add(role)

        db.session.commit()

    def __repr__(self):
        tpl = ('Role<name: {name},'
               ' powers: {powers}>')
        formatted = tpl.format(name=self.name,
                               powers=self.powers)
        return formatted


class Power(db.Model):
    __tablename__ = 'Power'
    id = db.Column(db.String(64), nullable=False, unique=True,
                   primary_key=True)
    # Many-to-Many: A Role can have multiple power; a power can belong to
    # roles
    roles = db.relationship("Role", secondary=association_table_role_power,
                            back_populates="powers")

    def __repr__(self):
        tpl = ('Power<id: {id}')
        formatted = tpl.format(id=self.id)
        return formatted


# A class which consists of all the ids of Power
class Permission:
    DATA_ENTRY = 'DATA_ENTRY'
    DATA_EDIT = 'DATA_EDIT'
    LAB_SETUP = 'LAB_SETUP'
    ADMIN = 'ADMIN'
    LAB_ACCESS = 'LAB_ACCESS'
    LAB_MANAGE = 'LAB_MANAGE'
    USER_MANAGE = 'USER_MANAGE'
    SUPERADMIN = 'SUPERADMIN'

    # Return all the permissions as a list
    @staticmethod
    def all_permissions():
        permissions_list = [Permission.DATA_ENTRY,
                            Permission.DATA_EDIT,
                            Permission.LAB_SETUP,
                            Permission.ADMIN,
                            Permission.LAB_ACCESS,
                            Permission.LAB_MANAGE,
                            Permission.USER_MANAGE,
                            Permission.SUPERADMIN]
        return permissions_list
