# Libraries
# Standard library
import linecache
import logging
import sys

# Local
from lemur import models as m
from lemur.lemur import db
from lemur.utility_decorators import failure_handler
from lemur.utility_generate_and_convert import (
    serialize_lab_list,
    change_observation_organization
)
ds = db.session

logger = logging.getLogger(__name__)


# --- Check existence ---
# This group of functions check the existence of an object and
# return True/False accordingly
def lab_exists(lab_id):
    return ds.query(m.Lab).filter(m.Lab.id == lab_id).count() > 0


def experiment_exists(experiment_id):
    return ds.query(m.Experiment).filter(m.Experiment.id == experiment_id).count() > 0


def observation_exists(observation_id):
    return ds.query(m.Observation).filter(m.Observation.id == observation_id).count() > 0


def class_exists(class_id):
    return ds.query(m.Class).filter(m.Class.id == class_id).count() > 0


# username is id of a User in database
def user_exists(username):
    return ds.query(m.User).filter(m.User.id == username).count() > 0


# --- Get an object from database ---
# This group of functions gets an object from the database by the unique
# key associated with that object. It will return the object found and None if
# such a object doesn't exist.

@failure_handler
def get_lab(lab_id):
    return ds.query(m.Lab).filter(m.Lab.id == lab_id).one()


@failure_handler
def get_experiment(experiment_id):
    return ds.query(m.Experiment).filter(m.Experiment.id == experiment_id).one()


@failure_handler
def get_observation(observation_id):
    return ds.query(m.Observation).filter(m.Observation.id == observation_id).one()


@failure_handler
def get_user(username):
    return ds.query(m.User).filter(
        m.User.id == username).one()


@failure_handler
def get_power(power_id):
    return ds.query(m.Power).filter(
        m.Power.id == power_id).one()


@failure_handler
def get_role(role_name):
    return ds.query(m.Role).filter(
        m.Role.name == role_name).one()


@failure_handler
def get_class(class_id):
    return ds.query(m.Class).filter(m.Class.id == class_id).one()


# --- Get a list of objects from database ---
# This group of functions returns a list of objects of a certain class
# that reaches a certain criteria

def get_all_lab():
    return ds.query(m.Lab).all()


def get_all_experiment():
    return ds.query(m.Experiment).all()


def get_all_class():
    return ds.query(m.Class).all()


def get_all_user():
    return ds.query(m.User).all()


def get_all_admin():
    return ds.query(m.User).filter(
        m.User.role_name == 'Admin').all()


def get_all_superadmin():
    return ds.query(m.User).filter(
        m.User.role_name == 'SuperAdmin').all()


# --- Get a list of objects for an object of another class from database ---
# This group of functions returns a list of objects of a class for
# an entered object of a related class(i.e. a relationship exists between the
# two classes)

# Get lab query for the user according to user's role
# A SuperAdmin can select among all the labs
# A student/Admin can only select his/her own labs
# Docstring-- RMD 2017-08-26
def get_available_labs_for_user(user):
    available_labs = [lab for lab in user.labs if lab.status == 'Activated']
    if user.role_name == 'SuperAdmin':
        lab_query = get_all_lab()
        available_labs = [lab for lab in lab_query if lab.status == 'Activated']
    return available_labs


def get_experiments_for_lab(lab_id):
    return ds.query(m.Experiment).filter(
        m.Experiment.lab_id == lab_id).order_by(m.Experiment.order).all()


def get_observations_for_experiment(experiment_id):
    return ds.query(m.Observation).filter(
        m.Observation.experiment_id == experiment_id).order_by(
            m.Observation.id).all()


# Return the the professor of a class
# We assume that a class only has one professor
# Return None if the class cannot be found or the class
# doesn't have a professor
# Docstring-- RMD 2017-08-26
def get_professors_for_class(class_id):
    professors = []
    the_class = get_class(class_id)
    for u in the_class.users:
        if u.role_name == 'Admin' or u.role_name == 'SuperAdmin':
            professors.append(u)
    return professors


# This one is a bit different:
# It returns the number of observations for a certain experiment
def find_observation_number_for_experiment(experiment_id):
    return db.session.query(m.Observation).filter(
        m.Observation.experiment_id == experiment_id).count()


# --- This group of functions returns a list of a certain attribute
# of all the objects in this class ----
# return the list of all class ids
def get_class_id_list(user):
    if user.role_name == 'SuperAdmin':
        return [c.id for c in get_all_class()]
    else:
        return [c.id for c in user.classes]


# --- Find the information of labs ---
# return all the list of labs with basic information according to
# the current user's role(SupderAdmin/Admin)
def find_lab_list_for_user(user):
    lab_list = []
    labs_query = []
    # query labs according to the user's role
    if user.role_name == 'SuperAdmin':
        labs_query = ds.query(m.Lab).all()
    elif user.role_name == 'Admin':
        labs_query = user.labs
        # get all the info of the labs
    for lab in labs_query:
        data_num = 0
        experiments_query = get_experiments_for_lab(lab.id)
        # We assume every group enters the same number of data for each lab
        # data_num represents the number of groups that have submitted data for
        # a lab
        if len(experiments_query) > 0:
            data_num += find_observation_number_for_experiment(experiments_query[0].id)
            lab_list.append({'lab_id': lab.id, 'lab_name': lab.name,
                             'class_id': lab.class_id,
                             'lab_status': lab.status,
                             'data_num': data_num})
    return lab_list


# Return all the current labs with basic info in JSON Format
def find_all_labs(user):
    get_activated = None
    get_downloadable = None
    get_unactivated = None
    # check if user is admin to limit their access to their own labs
    if user.role_name == 'Admin':
        get_activated = [lab for lab in user.labs if lab.status == 'Activated']
        get_downloadable = [lab for lab in user.labs if lab.status == 'Downloadable']
        get_unactivated = [lab for lab in user.labs if lab.status == 'Unactivated']
    else:
        get_activated = ds.query(m.Lab).filter(m.Lab.status == 'Activated').all()
        get_downloadable = ds.query(m.Lab).filter(m.Lab.status == 'Downloadable').all()
        get_unactivated = ds.query(m.Lab).filter(m.Lab.status == 'Unactivated').all()

    # convert lab info, class names and professor names into json format
    return {'activated': serialize_lab_list(get_activated),
            'downloadable': serialize_lab_list(get_downloadable),
            'unactivated': serialize_lab_list(get_unactivated)}


# Find a new lab id for the lab to copied from the old lab
def find_lab_copy_id(old_lab_id):
    for index in range(1, 10000):
        # Name new lab based on old lab and check if name is repeat
        if not lab_exists('copy'+str(index)+'-'+old_lab_id):
            break
    return 'copy'+str(index)+'-'+old_lab_id


# Query data entered by students for lab with lab_ids
def find_all_observations_for_labs(lab_ids):
    observations_group_by_experiment_name = []
    observations_group_by_student = []
    experiment_names = []
    err_msg = ''
    undownloadable_labs = ''
    try:
        # Group observations according to experiment_name
        experiments_query = get_experiments_for_lab(lab_ids[0])
        for e in experiments_query:
            observations_group_by_experiment_name.append({'experiment_name': e.name, 'observations': []})
            experiment_names.append(e.name)
        for lab_id in lab_ids:
            lab_status = get_lab(lab_id).status
            if lab_status != 'Downloadable':
                undownloadable_labs += (str(lab_id)+',')

            experiments_query = get_experiments_for_lab(lab_id)
            index = 0
            # Check whether these labs are compatible with each other
            # (the number of experiments and the names of experiments must
            # be the same)
            if len(experiments_query) != len(experiment_names):
                err_msg = (lab_ids[0]+' and '+lab_id +
                           ' are incompatible: the number of rows is different-' +
                           str(experiments_query.count()) +
                           ' and '+str(len(experiment_names)))
            else:
                for e in experiments_query:
                    if (experiment_names[index] != e.name):
                        err_msg = (lab_ids[0]+' and '+lab_id +
                                   ' are incompatible:' +
                                   experiment_names[index]+' and ' +
                                   e.name+' are different row names')
                        break
                    else:
                        observations_query = get_observations_for_experiment(e.id)
                        for observation in observations_query:
                            observations_group_by_experiment_name[index]['observations'].append({
                                'lab_id': lab_id,
                                'student_name': observation.student_name,
                                'experiment_id': observation.experiment_id,
                                'observation_id': observation.id,
                                'observation_data': observation.datum})
                            index += 1
                            observations_group_by_student = change_observation_organization(observations_group_by_experiment_name)

    except Exception:
        exc_type, exc_obj, tb = sys.exc_info()
        frame = tb.tb_frame
        lineno = tb.tb_lineno
        filename = frame.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, frame.f_globals)
        err_msg = 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)
    return (observations_group_by_experiment_name,
            observations_group_by_student,
            experiment_names, err_msg, undownloadable_labs)
