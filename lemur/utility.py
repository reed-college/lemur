# This is file contains all the utility functions used by view
# functions in view.py
# The reasons of using these functions instead of directly writing the code
# into view functions are: code readability of view functions;
# easier unit testing for different features a view function supports

# Libraries
# Standard library
from functools import wraps
import linecache
import sys

# Third-party libraries
from flask import make_response, render_template, jsonify, redirect, url_for
from flask.ext.login import current_user

# Other modules
from lemur import models as m
from lemur import (app, db)
ds = db.session


# --- Decorators ---

# This handler has not been added to view functions.
# This is a decorator used to handle exceptions
# It will not be activated if the app is in debug mode
# since debug mode can generate more detailed error feedback
# already
def db_exception_handler(request_type, msg="Unknown bug. "):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if app.debug is True:
                ret = f(*args, **kwargs)
                return ret
            else:
                try:
                    ret = f(*args, **kwargs)
                    return ret
                except Exception:
                    db.session.rollback()
                    exc_type, exc_obj, tb = sys.exc_info()
                    frame = tb.tb_frame
                    lineno = tb.tb_lineno
                    filename = frame.f_code.co_filename
                    linecache.checkcache(filename)
                    line = linecache.getline(filename, lineno, frame.f_globals)
                    err_msg = 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno,
                                                                           line.strip(), exc_obj)
                    if request_type == 'POST':
                        return jsonify(success=False, data=err_msg)
                    else:
                        return render_template('error_400.html',
                                               err_msg=err_msg), 400
        return wrapped
    return decorator


# A decorator used to check the user's permission to access the current page
# If the user doesn't have access, redirect to the login page
def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# A decorator that avoids the function to raise an exception but return
# a None instead
def failure_handler(f):
    def f_try(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except:
            return None
    return f_try


# --- Message/ID generator/decomposer ---

# Check the existence of args in a form
# and generate an error message accordingly
def check_existence(form, *expectedArgs):
    err_msg = ''
    for a in expectedArgs:
        if not(a in form):
            err_msg += (a+' is not defined'+'\n')
    if err_msg != '':
        app.logger.error(err_msg)
    return err_msg


# generate the error message by receiving error info
def generate_err_msg(name1, value1, name2, value2):
    return '{0}:{1} and {2}:{3} are different'.format(name1, value1, name2,
                                                      value2)


# --- ID generators/decomposers ---
def generate_lab_id(lab_name, class_id):
    return lab_name+':'+class_id


def generate_experiment_id(lab_id, experiment_name):
    return lab_id+':'+experiment_name


def generate_observation_id(experiment_id, student_name):
    return experiment_id+':'+student_name


def generate_class_id(class_name, class_time):
    return class_name+'_'+class_time


def decompose_lab_id(lab_id):
    return {'lab_name': lab_id.split(':')[0],
            'class_id': lab_id.split(':')[1]}


def decompose_class_id(class_id):
    return {'class_name': class_id.split('_')[0],
            'class_time': class_id.split('_')[1]}


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
def get_professors_for_class(class_id):
    professors = []
    the_class = get_class(class_id)
    for u in the_class.users:
        if u.role_name == 'Admin' or u.role_name == 'SuperAdmin':
            professors.append(u)
    return professors


# This one is a bit different:
# It returns the number of observations for a certain experiment
def observation_number_for_experiment(experiment_id):
    return db.session.query(m.Observation).filter(
        m.Observation.experiment_id == experiment_id).count()


# --- Serialization/Deserialization ---
# These the types of parameters/return values of these functions
# are relatively flexible. This group of functions receives a list
# of objects and convert it into a python list of dictionaries
# (close to JSON format) with the info contained by these objects

def serialize_lab_list(lab_list):
    labs = []

    for lab in lab_list:
        if lab.the_class:
            class_id = lab.the_class.id
        else:
            class_id = None
        prof_name = ','.join([u.name for u in lab.users if ((u.role_name == 'SuperAdmin') or (u.role_name == 'Admin'))])
        labs.append({'lab_id': lab.id,
                     'lab_name': lab.name,
                     'description': lab.description,
                     'class_id': class_id,
                     'prof_name': prof_name,
                     'status': lab.status,
                     'experiments': len(lab.experiments)})
    return labs


def serialize_experiment_list(experiment_list):
    experiments = []
    for experiment in experiment_list:
        experiments.append({'experiment_id': experiment.id,
                            'experiment_name': experiment.name,
                            'description': experiment.description,
                            'order': experiment.order,
                            'value_type': experiment.value_type,
                            'value_range': experiment.value_range,
                            'value_candidates': experiment.value_candidates})
    return experiments


def serialize_user_list(user_list):
    user_list = []
    for user in user_list:
        classes = [c.id for c in user.classes]
        labs = [lab.id for lab in user.labs]
        user_list.append({'username': user.id,
                          'name': user.name,
                          'role_name': user.role_name,
                          'classes': classes,
                          'labs': labs})
    return user_list


def serialize_class_list(class_list):
    current_classes = []
    for c in class_list:
        professors = [p.id for p in c.users if (p.role_name == 'Admin' or p.role_name == 'SuperAdmin')]
        students = [s.id for s in c.users if s.role_name == 'Student']
        labs = [lab.id for lab in c.labs]
        current_classes.append({'id': c.id,
                                'name': c.name,
                                'time': c.time,
                                'professors': professors,
                                'students': students,
                                'labs': labs})
    return current_classes


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
            data_num += observation_number_for_experiment(experiments_query[0].id)
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


# --- Manage labs ---

# Delete a lab's basic info, experiments info and observations info
def delete_lab(lab_id):
    ds.delete(get_lab(lab_id))
    experiments_query = get_experiments_for_lab(lab_id)
    for e in experiments_query:
        ds.delete(e)
    ds.commit()


# Modify a lab
def modify_lab(lab_json):
    the_class = None
    class_users = []
    experiments_for_lab = []
    lab_status = 'Activated'
    lab_id = None

    err_msg = check_existence(lab_json, 'labName', 'classId', 'labDescription',
                                        'experiments', 'oldLabId')
    if lab_exists(lab_json['oldLabId']):
        lab_status = get_lab(lab_json['oldLabId']).status
        delete_lab(lab_json['oldLabId'])
    if not class_exists(lab_json['classId']):
        err_msg += 'class id: {0} doesn\' exist in the database'.format(lab_json['classId'])
    if err_msg != '':
        return err_msg
    the_class = get_class(lab_json['classId'])
    # Build connection between the current lab and the existing users/class
    if the_class is not None:
        class_users = the_class.users
    lab_id = generate_lab_id(lab_json['labName'], lab_json['classId'])
    if lab_exists(lab_id):
        return 'lab id:{0} already exists'.format(lab_id)
    for e in lab_json['experiments']:
        err_msg = check_existence(e, 'name', 'description', 'order',
                                     'valueType', 'valueRange',
                                     'valueCandidates')

        if err_msg != '':
            return err_msg
    for e in lab_json['experiments']:
            experiment_name = e['name']
            # Check if the experiment name already repetes among all the
            # experiments to be added into the current lab
            for i in range(len(lab_json['experiments'])):
                if [exp['name'] for exp in lab_json['experiments']].count(experiment_name) > 1:
                    lab_json['experiments'] = (lab_json['experiments'][0:i] +
                                               lab_json['experiments'][i+1:len(lab_json['experiments'])])
                    warning_msg = 'repeted experiment name:{} in this lab'.format(experiment_name)
                    app.logger.warning(warning_msg)
                    continue
            experiment_id = generate_experiment_id(lab_id, experiment_name)

            if experiment_exists(experiment_id):
                warning_msg = 'The same experiment name has already exist in the same lab'
                app.logger.warning(warning_msg)
                continue
            else:
                experiments_for_lab.append(m.Experiment(lab_id=lab_id,
                                                        id=experiment_id,
                                                        name=experiment_name,
                                                        description=e['description'],
                                                        order=e['order'],
                                                        value_type=e['valueType'],
                                                        value_range=e['valueRange'],
                                                        value_candidates=e['valueCandidates']))
    the_lab = m.Lab(id=lab_id, name=lab_json['labName'],
                    description=lab_json['labDescription'],
                    status=lab_status,
                    the_class=the_class,
                    experiments=experiments_for_lab,
                    users=class_users)
    ds.add(the_lab)
    ds.commit()
    return ''


# Find a new lab id for the lab to copied from the old lab
def find_lab_copy_id(old_lab_id):
    for index in range(1, 10000):
        # Name new lab based on old lab and check if name is repeat
        if not lab_exists('copy'+str(index)+'-'+old_lab_id):
            break
    return 'copy'+str(index)+'-'+old_lab_id


# copy a old lab and rename the new lab with 'copy'+index+'-'+old_lab_name
def duplicate_lab(old_lab_id):
    # Find a new lab id according to the old lab id
    new_lab_id = find_lab_copy_id(old_lab_id)
    # Copy info from old lab and add to new lab
    old_lab = get_lab(old_lab_id)
    # A lab can only belong to one class at this point
    old_class = get_class(old_lab.the_class.id)
    new_lab = m.Lab(
        id=new_lab_id, name=decompose_lab_id(new_lab_id)['lab_name'],
        description=old_lab.description, status=old_lab.status,
        the_class=old_class, users=old_class.users)

    new_experiments = []
    for e in old_lab.experiments:
        experiment_name = e.name
        new_experiment_id = generate_experiment_id(new_lab_id,
                                                   experiment_name)
        new_experiment = m.Experiment(lab_id=new_lab_id,
                                      id=new_experiment_id,
                                      name=experiment_name,
                                      description=e.description,
                                      order=e.order,
                                      value_type=e.value_type,
                                      value_range=e.value_range,
                                      value_candidates=e.value_candidates)
        new_experiments.append(new_experiment)
    new_lab.experiments = new_experiments
    ds.add(new_lab)
    ds.commit()


# Change a lab's status
def change_lab_status(lab_id, new_status):
    lab_query = get_lab(lab_id)
    lab_query.status = new_status
    ds.commit()


# Check and return lab information sent from the client
def pack_labinfo_sent_from_client(client_form):
    err_msg = check_existence(client_form, 'labName', 'classId',
                                           'labDescription',
                                           'labQuestions')
    if err_msg != '':
        return dict(), err_msg
    # to keep the interface consistent, assign empty string to lab_id
    lab_info = {'lab_id': '',
                'lab_name': client_form['labName'],
                'class_id': client_form['classId'],
                'description': client_form['labDescription']}
    # Add empty experiments to be consistent with the variables used in the
    # template admin_modify_lab.html
    lab_info['experiments'] = [{'experiment_name': '',
                                'description': '',
                                'order': r+1,
                                'value_type': '',
                                'value_range': '',
                                'value_candidates': ''} for r in range(int(client_form['labQuestions']))]
    return lab_info, ''


# --- Manage observations ---

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


def change_observation_organization(observations_group_by_experiment_name):
    # Group row data according to student_name
    observations_group_by_student = []
    for experiment in observations_group_by_experiment_name:
        # sort observation_data_list to make all the data across different
        # lists
        sorted(experiment['observations'], key=lambda observation: observation['observation_id'])
        # if list is empty, add student names into it
        if not observations_group_by_student:
            for observation in experiment['observations']:
                observations_group_by_student.append({
                    'student_name': observation['student_name'],
                    'lab_id': observation['lab_id'], 'observations': []})

        for i in range(len(experiment['observations'])):
            observation = experiment['observations'][i]
            observations_group_by_student[i]['observations'].append({
                'experiment_name': experiment['experiment_name'],
                'experiment_id': observation['experiment_id'],
                'observation_id': observation['observation_id'],
                'observation_data': observation['observation_data']})
    return observations_group_by_student


# delete observation from a list of observation ids sent from client
def delete_observation(old_observation_ids_list):
    # delete all the old data by old observation_id
    for observation_id in old_observation_ids_list:
        observations_query = get_observation(observation_id)
        ds.delete(observations_query)
    ds.commit()


# add observation from a list JSON format observations sent from client
def add_observation(new_observations_list):
    warning_msg = ''
    for d in new_observations_list:
        err_msg = check_existence(d, 'studentName', 'observationData',
                                  'experimentId', 'observationId')
        if err_msg != '':
            return err_msg
    count = len(new_observations_list)
    for i in range(count):
        d = new_observations_list[i]
        # Check if the observation name already repetes among all the
        # observations to be added into the database
        if [ob['observationId'] for ob in new_observations_list].count(d['observationId']) > 1:
            new_observations_list = (new_observations_list[0:i] +
                                     new_observations_list[i+1:len(new_observations_list)])
            warning_msg = 'repeted observation id:{} in this lab'.format(d['observationId'])
            count -= 1
            continue
        ds.add(m.Observation(experiment_id=d['experimentId'],
                             id=d['observationId'],
                             student_name=d['studentName'],
                             datum=d['observationData']))

    ds.commit()
    return warning_msg


# add observations sent by students into the database
def add_observations_sent_by_students(observations_group_by_student):
    # the data type of observations should be a list
    if not(isinstance(observations_group_by_student, list)):
        err_msg = 'The value of the key observations should be a list'
        return err_msg

    # check that all list elements have the right format
    for student in observations_group_by_student:
        err_msg = check_existence(student, 'studentName',
                                  'observationsForOneExperiment')
        if err_msg != '':
            return err_msg

        student_name = student['studentName']
        for ob in student['observationsForOneExperiment']:
            err_msg = check_existence(ob, 'labId', 'experimentName',
                                      'observation')
            if err_msg != '':
                return err_msg
            # If everything is correct add the data to the database
            lab_id = ob['labId']
            experiment_name = ob['experimentName']

            experiment_id = generate_experiment_id(lab_id, experiment_name)
            observation_id = generate_observation_id(experiment_id,
                                                     student_name)
            if not observation_exists(observation_id):
                ds.add(m.Observation(experiment_id=experiment_id,
                                     id=observation_id,
                                     student_name=student_name,
                                     datum=ob['observation']))
    ds.commit()
    return ''


# --- Manage admins ---

# add an admin into the database according to admin_info
def add_user(user_info):
    # Get role object from table
    user_role = get_role(user_info['role'])
    # id of the Admin must be unique before user can be created
    err_msg = check_existence(user_info, 'username', 'role')
    if err_msg != '':
        return err_msg
    classes = []
    labs = []
    if user_info['role'] == 'Student':
        for class_id in user_info.getlist('classIds'):
            if class_exists(class_id):
                the_class = get_class(class_id)
                classes.append(the_class)
                for lab in the_class.labs:
                    labs.append(lab)
            else:
                return 'the class with id:{} doesn\'t exist.'.format(class_id)
    if not user_exists(user_info['username']):
        new_user = m.User(id=user_info['username'],
                          name=user_info['name'],
                          role=user_role,
                          classes=classes,
                          labs=labs)
        ds.add(new_user)
        ds.commit()
    else:
        err_msg = 'The username:{} already exists'.format(user_info['username'])
    return err_msg


# change the user's info(including role and classes)
def change_user_info(username, role, class_ids):
    user = get_user(username)
    classes = []
    labs = []
    for c in class_ids:
        the_class = get_class(c)
        classes.append(the_class)
        for lab in the_class.labs:
            labs.append(lab)
    user.role = get_role(role)
    user.classes = classes
    user.labs = labs
    ds.commit()


# delete an admin from the database
def delete_user(username):
    user_to_be_removed = get_user(username)
    ds.delete(user_to_be_removed)
    ds.commit()


# add a class into the database according to class_info
def add_class(class_info):
    # Check the correctness of data format
    err_msg = check_existence(class_info, 'professors', 'students',
                              'className', 'classTime')
    if err_msg != '':
        return err_msg
    users = []
    usernames = []
    # create new class with data sent by client to be added to database
    new_class_id = generate_class_id(
        class_info['className'], class_info['classTime'])

    if not class_exists(new_class_id):
        for p in class_info.getlist('professors'):
            if not user_exists(p):
                err_msg = 'The professor with id:{} doesn\'t exist.'.format(p)
                return err_msg
            else:
                usernames.append(p)

        for s in class_info.getlist('students'):
            if not user_exists(s):
                err_msg = 'The student with id:{} doesn\'t exist.'.format(p)
                return err_msg
            elif get_user(s).role_name != 'Student':
                err_msg = s+(' already exists and is not a student.'
                             'You should not put their name into student name')
                return err_msg
            else:
                usernames.append(s)
        for username in usernames:
            users.append(get_user(username))
        new_class = m.Class(id=new_class_id,
                            name=class_info['className'],
                            time=class_info['classTime'],
                            users=users)
        ds.add(new_class)
        ds.commit()
    else:
        err_msg = "The class id already exists: {}".format(get_class(new_class_id))
    return err_msg


# ---Manage classes---

# remove a class from the database according to class_id
def delete_class(class_id):
    class_to_be_removed = get_class(class_id)
    # discard users not enrolled in any other class with labs
    # discard labs associated with the class to be deleted
    for s in class_to_be_removed.users:
        if s.role_name == 'Student' and len(s.classes) == 1:
            ds.delete(s)
    for l in class_to_be_removed.labs:
        if lab_exists(l.id):
            ds.delete(get_lab(l.id))
    ds.delete(class_to_be_removed)
    ds.commit()


# Change the users(both professors and students) in a class
def change_class_users(class_id, new_users):
    if not class_exists(class_id):
        return 'Class with id: {} doesn\'t exist'.format(class_id)
    the_class = get_class(class_id)
    old_users = the_class.users
    # Add new users to the class;
    # add the associated labs to these users lab list
    for u in new_users:
        if not user_exists(str(u)):
            ds.rollback()
            return 'User with username: {} doesn\'t exist'.format(u)
        else:
            user = get_user(u)
            if not (u in the_class.users):
                the_class.users.append(user)
                user.labs = the_class.labs
    # Delete the class and the associated labs from old users who
    # are not in the class anymore
    for u in old_users:
        if not(u in the_class.users):
            u.classes = [c for c in u.classes if c.id != class_id]
            new_lab_list = []
            for lab in u.labs:
                if lab.the_class.id != class_id:
                    new_lab_list.append(lab)
            u.labs = new_lab_list
    ds.commit()
    return ''


# --- Initialize Classes and Users by getting data from Iris ---

# Convert a term code into a semester name
# e.g. 201701 -> FALL2016
# e.g. 201703 -> SPRING2017
def tranlate_term_code_to_semester(term_code):
    convert_table = {'1': 'FALL',
                     '2': 'PAIDEIA',
                     '3': 'SPRING',
                     '4': 'SUMMER'}
    term_code_list = list(term_code)
    term_index = term_code_list[-1]
    year = ''.join(term_code_list[:4])
    if term_index == '1':
        year = str(int(year) - 1)
    if term_index in convert_table:
        return convert_table[term_index] + year
    return ''


# This method will remove all the 470 classes; for any of other class,
# combine the instructor field of all sections
def cleanup_class_data(class_data):
    cleaned_class_data = []
    course_number_set = set()
    for c in class_data:
        if c['course_number'] != '470':
            course_number_set.add(c['course_number'])
    course_number_list = list(course_number_set)
    for course_number in course_number_list:
        the_class_list = list(filter(lambda c: c['course_number'] == course_number, class_data))
        # the_class_list is impossible to be empty
        the_class = the_class_list[0]
        for c in the_class_list:
            for instructor in c['instructors']:
                if not (instructor in the_class['instructors']):
                    the_class['instructors'].append(instructor)
        cleaned_class_data.append(the_class)
    return cleaned_class_data


# Populate the database with classes and their corresponding professors
# Note: This needs to be invoked before update_users_by_data_from_iris
def populate_db_with_classes_and_professors(class_data):
    class_data = cleanup_class_data(class_data)
    for c in class_data:
        class_name = c['subject'] + c['course_number']
        class_time = tranlate_term_code_to_semester(c['term_code'])
        class_professor_ids = c['instructors']
        class_professors = []
        for p in class_professor_ids:
            if not user_exists(p):
                ds.add(m.User(id=p, role=get_role('Admin')))
                ds.commit()
            the_user = get_user(p)
            class_professors.append(the_user)
        print(class_name, class_time)
        if class_name and class_time:
            class_id = generate_class_id(class_name, class_time)
            # If the class already exists, update the professors and keep
            # the students
            if class_exists(class_id):
                the_class = get_class(class_id)
                # handle the change of class and the labs associated with it
                old_class_professors = [u for u in the_class.users if u.role_name != 'Student']
                for p in class_professors:
                    if not (class_id in [c.id for c in p.classes]):
                        p.classes.append(the_class)
                        for lab in the_class.labs:
                            if not (lab in p.labs):
                                p.labs.append(lab)
                ds.commit()
                for p in old_class_professors:
                    if not (p.id in class_professor_ids):
                        p.classes = [c for c in p.classes if c.id != class_id]
                        p.labs = [lab for lab in p.labs if lab.class_id != class_id]
            # otherwise create a class with the professors
            else:
                ds.add(m.Class(id=class_id, name=class_name, time=class_time,
                               users=class_professors))
        else:
            return 'class_time is not valid:{}'.format(class_time)
    ds.commit()
    return ''


# Update the users in the classes according to registration info
def update_users_by_data_from_iris(registration_data):
    all_classes = get_all_class()
    warning_msg = ''
    registration_by_class = {}
    # A registration_object looks like
    # {"user_name":"fake1","course_id":"10256","term_code":"201501",
    # "subject":"BIOL","course_number":"101","section":"FTN"}

    # Add the students in the received data into the database
    for registration_object in registration_data:
        username = registration_object['user_name']
        class_id = generate_class_id((registration_object['subject'] +
                                     registration_object['course_number']),
                                     tranlate_term_code_to_semester(registration_object['term_code']))
        # If the class exists in the database, update
        if class_exists(class_id):
            the_class = get_class(class_id)
            # If user already exists, add the class into the class list of the
            # user；
            # otherwise, create a user with the class
            if user_exists(username):
                the_user = get_user(username)
                if not (class_id in [c.id for c in the_user.classes]):
                    the_user.classes.append(the_class)
                    for lab in the_class.labs:
                        if not (lab in the_user.labs):
                            the_user.labs.append(lab)
            else:
                the_user = m.User(id=username, classes=[the_class],
                                  role=get_role('Student'), labs=the_class.labs)
                ds.add(the_user)
        # else return a warning message to notify the user
        else:
            warning_msg += ('class_id: ' + class_id +
                            ' doesn\'t exist in database\n')

        # for efficiency: otherwise we have to loop through
        if class_id in registration_by_class:
            registration_by_class[class_id].append(username)
        else:
            registration_by_class[class_id] = []

    # Check the students of the classes in the database and update them
    # according to the received data
    for c in all_classes:
        # If the class exists in the received data, compare
        # the users of the class in database and data
        if c.id in registration_by_class:
            # Keep the admins/superadmins of the class
            class_new_users = [u for u in c.users if u.role_name != 'Student']
            # Replace the students of the class with the students in the
            # received data
            for student_id in registration_by_class[c.id]:
                class_new_users.append(get_user(student_id))
            c.users = class_new_users
        else:
            warning_msg += ('class_id: ' + class_id +
                            ' doesn\'t exist in received data\n')
    ds.commit()
    return warning_msg


# --- Response object generators ---

# Format the string csv to be downloaded
def format_download(observations_by_student, experiment_names, lab_ids):
    # Add two additional columns besides experiment names
    experiment_names = ['Student Name', 'Lab ID'] + experiment_names

    dt = '\t\t'
    nl = '\n'
    csv = dt.join(experiment_names)+nl
    for student in observations_by_student:
        csv += (student['student_name']+dt+student['lab_id'])
        for data in student['observations']:
            csv += (dt+data['observation_data'])
        csv += nl
    lab_ids_str = '+'.join(lab_ids)
    # create a response out of the CSV string
    response = make_response(csv)
    # Set the right header for the response to be downloaded
    response.headers["Content-Disposition"] = ('attachment; filename=' +
                                               lab_ids_str+'.txt')
    return response


# generate normal json object(for POST request) for a view function to return
def normal_json(data='success', code=200):
    return (jsonify(success=True, data=data), code,
            {'Content-Type': 'application/json'})


# generate error json object(for POST request) for a view function to return
# error message
def err_json(err_msg='Client Error', code=400):
    app.logger.error(err_msg)
    return (jsonify(success=False, data=err_msg), code,
            {'Content-Type': 'application/json'})


# generate a response object(for GET request) for a view function to return
def err_html(err_msg='Client Error', template='error_400.html', code=400):
    app.logger.error(err_msg)
    return (render_template(template, err_msg=err_msg),
            code, {'Content-Type': 'text/html'})
