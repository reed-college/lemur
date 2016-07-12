# Libraries
# Standard library
from functools import wraps
import linecache
import sys
import re

# Third-party libraries
from flask import make_response, render_template, jsonify, redirect, url_for
from flask.ext.login import current_user

# Other modules
from lemur import models as m
from lemur import (app, db)
ds = db.session


# --- Decorators ---
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
def generate_lab_id(lab_name, class_name, prof_name):
    return lab_name+'_'+class_name+'_'+prof_name


def generate_experiment_id(lab_id, experiment_name):
    return lab_id+':'+experiment_name


def generate_observation_id(experiment_id, student_name):
    return experiment_id+':'+student_name


# The user_id is the same as username at this point,
# both of them must be unique
def generate_user_id(username):
    return username


def generate_class_id(class_name, class_time):
    return class_name+'_'+class_time


def decompose_lab_id(lab_id):
    return {'lab_name': lab_id.split('_')[0],
            'prof_name': lab_id.split('_')[1],
            'class_name': lab_id.split('_')[2]}


def decompose_class_id(class_id):
    return {'class_name': class_id.split('_')[0],
            'class_time': class_id.split('_')[1]}


# --- Check existence ---
def lab_exists(lab_id):
    return ds.query(m.Lab).filter(m.Lab.id == lab_id).count() > 0


def experiment_exists(experiment_id):
    return ds.query(m.Experiment).filter(m.Experiment.id == experiment_id).count() > 0


def observation_exists(observation_id):
    return ds.query(m.Observation).filter(m.Observation.id == observation_id).count() > 0


def class_exists(class_id):
    return ds.query(m.Class).filter(m.Class.id == class_id).count() > 0


def user_exists(user_id):
    return ds.query(m.User).filter(m.User.id == user_id).count() > 0


# --- Query data ---
# Get the Lab object from the database by lab_id
@failure_handler
def get_lab(lab_id):
    return ds.query(m.Lab).filter(m.Lab.id == lab_id).one()


@failure_handler
def get_experiment(experiment_id):
    return ds.query(m.Experiment).filter(m.Experiment.id == experiment_id).one()


# Get the Observation object from the database by observation_id
@failure_handler
def get_observation(observation_id):
    return ds.query(m.Observation).filter(m.Observation.id == observation_id).one()


@failure_handler
def get_user(user_id):
    return ds.query(m.User).filter(
        m.User.id == user_id).one()


@failure_handler
def get_class(class_id):
    return ds.query(m.Class).filter(m.Class.id == class_id).one()


@failure_handler
def get_role(role_name):
    return ds.query(m.Role).filter(
        m.Role.name == role_name).one()


def get_all_lab():
    return ds.query(m.Lab).all()


def get_all_experiment():
    return ds.query(m.Experiment).all()


# return the query for all the classes in the database
def get_all_class():
    return ds.query(m.Class).all()


# return the query for all the admins in the database
def get_all_admin():
    return ds.query(m.User).filter(
           m.User.role_name == 'Admin').all()


# return the query for all the admins in the database
def get_all_superadmin():
    return ds.query(m.User).filter(
           m.User.role_name == 'SuperAdmin').all()


# Get lab query for the user according to user's role
# A SuperAdmin can select among all the labs
    # A student/Admin can only select his/her own labs
def get_labs_for_user(user):
    if user.role_name == 'SuperAdmin':
        return ds.query(m.Lab).all()
    else:
        return [lab for lab in user.labs]


# Get all the experiments for a lab
def get_experiments_for_lab(lab_id):
    return ds.query(m.Experiment).filter(
        m.Experiment.lab_id == lab_id).order_by(m.Experiment.order).all()


# Get all the observations for an experiment
def get_observations_for_experiment(experiment_id):
    return ds.query(m.Observation).filter(
        m.Observation.experiment_id == experiment_id).order_by(
        m.Observation.id).all()


# --- Check number ---
def observation_number_for_experiment(experiment_id):
    return db.session.query(m.Observation).filter(
        m.Observation.experiment_id == experiment_id).count()


# ---serialization/deserialization---
# convert a query for labs into a python list of dictionaries
def serialize_lab_list(lab_list_query):
    labs = []
    for lab in lab_list_query:
        labs.append({'lab_id': lab.id,
                     'lab_name': lab.name,
                     'description': lab.description,
                     'class_name': lab.class_name,
                     'prof_name': lab.prof_name,
                     'status': lab.status,
                     'experiments': len(lab.experiments)})
    return {'lab_list': labs}


# convert a query for experiments into a list of JSON objects
def serialize_experiment_list(experiment_list_query):
    experiments = []
    for experiment in experiment_list_query:
        experiments.append({'experiment_id': experiment.id,
                            'experiment_name': experiment.name,
                            'description': experiment.description,
                            'order': experiment.order,
                            'value_type': experiment.value_type,
                            'value_range': experiment.value_range,
                            'value_candidates': experiment.value_candidates})
    return experiments


# return a list of class names
def serialize_class_name_list():
    return [c.name for c in get_all_class()]


# return a list of class ids
def serialize_class_ids_list():
    return [c.id for c in get_all_class()]


# return a list of professors' names
def serialize_prof_name_list():
    return [u.name for u in get_all_admin()] + [u.name for u in get_all_superadmin()]


# convert a query for admins into a list of JSON objects
def serialize_admin_list(admins_query):
    current_admins = []
    for admin in admins_query:
        classes = [c.id for c in admin.classes]
        labs = [lab.id for lab in admin.labs]
        current_admins.append({'id': admin.id,
                               'username': admin.username,
                               'password': admin.password,
                               'name': admin.name, 'classes': classes,
                               'labs': labs})
    return current_admins


# convert a query for classes into a list of JSON objects
def serialize_class_list(classes_query):
    current_classes = []
    for c in classes_query:
        professors = [p.username for p in c.users if (p.role_name == 'Admin' or p.role_name == 'SuperAdmin')]
        students = [s.username for s in c.users if s.role_name == 'Student']
        labs = [lab.id for lab in c.labs]
        current_classes.append({'id': c.id,
                                'name': c.name,
                                'time': c.time,
                                'professors': professors,
                                'students': students,
                                'labs': labs})
    return current_classes


# Cnovert a string in the format '[a,b,c]' into a python list
def deserialize_lab_id(lab_ids):
    lab_ids = lab_ids.lstrip('\"[').rstrip('\"]').split(',')
    lab_ids = [lab.lstrip('\'').rstrip('\'') for lab in lab_ids if
               lab.lstrip('\'').rstrip('\'') != '']
    if not(isinstance(lab_ids, list)):
        err_msg = 'The <lab_ids> does not have the right format. '
        +'lab_ids has the type '+str(type(lab_ids))
        return lab_ids, err_msg
    return lab_ids, ''


# --- Find the information of labs ---
# return all the list of labs with basic information according to
# the current user's role
def find_lab_list_for_user(user):
    lab_list = []
    # query labs according to the user's role
    labs_query = get_labs_for_user(user)
    if user.role_name == 'Admin':
        labs_query = user.labs

    # get all the info of the labs
    for lab in labs_query:
        data_num = 0
        experiments_query = get_experiments_for_lab(lab.id)
        for e in experiments_query:
            data_num += observation_number_for_experiment(e.id)
        lab_list.append({'lab_id': lab.id, 'lab_name': lab.name,
                         'class_name': lab.class_name,
                         'prof_name': lab.prof_name,
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
    return {'activated': serialize_lab_list(get_activated)['lab_list'],
            'downloadable': serialize_lab_list(get_downloadable)['lab_list'],
            'unactivated': serialize_lab_list(get_unactivated)['lab_list']}


# Admin can only edit labs in his/her own zone
def check_power_to_add_lab(user, prof_name, class_id):
    if user.role_name == 'Admin':
        if prof_name != user.name:
            err_msg = 'You cannot edit labs for other Admins'
            return err_json(err_msg)
        elif not (class_id in [c.id for c in user.classes]):
            err_msg = ('You cannot edit labs for classes that are'
                       'belong to other Admins\' class')
    return ''


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
    err_msg = check_existence(lab_json, 'labName', 'classId',
                                        'professorName', 'labDescription',
                                        'experiments', 'oldLabId')
    if lab_exists(lab_json['oldLabId']):
        delete_lab(lab_json['oldLabId'])
    if not class_exists(lab_json['classId']):
        err_msg += 'class id: {0} doesn\' exist in the database'.format(lab_json['classId'])
    if err_msg != '':
        return err_msg
    the_class = get_class(lab_json['classId'])
    # Build connection between the current lab and the existing users/classes
    class_users = []
    if the_class is not None:
        class_users = the_class.users
    class_name = decompose_class_id(lab_json['classId'])['class_name']
    lab_id = generate_lab_id(lab_json['labName'],
                             class_name,
                             lab_json['professorName'])
    if lab_exists(lab_id):
        return 'lab id:{0} already exists'.format(lab_id)
    experiments_for_lab = []

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
                    class_name=class_name,
                    prof_name=lab_json['professorName'],
                    description=lab_json['labDescription'],
                    status='Activated',
                    classes=[the_class],
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
    old_class = get_class(old_lab.classes[0].id)
    new_lab = m.Lab(
        id=new_lab_id, name=decompose_lab_id(new_lab_id)['lab_name'],
        class_name=old_lab.class_name, prof_name=old_lab.prof_name,
        description=old_lab.description, status=old_lab.status,
        classes=[old_class], users=old_class.users)

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
                                           'professorName',
                                           'labDescription',
                                           'labQuestions')
    if err_msg != '':
        return dict(), err_msg
    # to keep the interface consistent, assign empty string to lab_id
    class_info = decompose_class_id(client_form['classId'])
    lab_info = {'lab_id': '',
                'lab_name': client_form['labName'],
                'class_id': client_form['classId'],
                'prof_name': client_form['professorName'],
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
# This function is redundant and needs to be fixed at
# some point
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
                undownloadable_labs += (str(lab_id)+'\t')

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

            ds.add(m.Observation(experiment_id=experiment_id,
                                 id=observation_id,
                                 student_name=student_name,
                                 datum=ob['observation']))
    ds.commit()
    return ''


# --- Manage admins ---
# add an admin into the database according to admin_info
def add_admin(admin_info):
    # Get role object from table
    role_admin = get_role('Admin')
    # id of the Admin must be unique before user can be created
    err_msg = check_existence(admin_info, 'username')
    if err_msg != '':
        return err_msg
    new_admin_id = generate_user_id(admin_info['username'])
    if not user_exists(new_admin_id):
        new_admin = m.User(id=new_admin_id,
                           username=admin_info['username'],
                           password=admin_info['password'],
                           name=admin_info['name'],
                           role=role_admin)
        ds.add(new_admin)
        ds.commit()
    else:
        err_msg = 'The Admin_id already exists'
    return err_msg


# delete an admin from the database
def delete_admin(admin_id):
    admin_to_be_removed = get_user(admin_id)
    ds.delete(admin_to_be_removed)
    ds.commit()


# change admin's password
def change_admin_password(admin_id, new_password):
    get_user(admin_id).password = new_password
    ds.commit()


# add a class into the database according to class_info
def add_class(class_info):
    # get role objects from the Role table
    role_student = get_role('Student')
    role_admin = get_role('Admin')

    # Check the correctness of data format
    err_msg = check_existence(class_info, 'professors', 'students',
                              'className', 'classTime')
    if err_msg != '':
        return err_msg

    users = []
    user_ids = []
    professor_names = class_info['professors'].split(',')
    # Process the string to strip all the white space
    student_names_str = ''.join(class_info['students'].split())
    student_names = ''.join(class_info['students'].split()).split(',')
    # Check the correctness of the string to be strings delimited only
    # by comma
    pattern_for_student_names = '[a-zA-Z]((,[a-zA-Z])*)'

    if (re.match(pattern_for_student_names, student_names_str) is None):
        err_msg = 'The pattern for student names is not correct'
        return err_msg

    # create new class with data sent by client to be added to database
    new_class_id = generate_class_id(
        class_info['className'], class_info['classTime'])

    if not class_exists(new_class_id):
        for p in professor_names:
            p_id = generate_user_id(p)
            if not user_exists(p_id):
                ds.add(m.User(id=p_id, username=p,
                              password='data', role=role_admin))
            user_ids.append(p_id)

        for s in student_names:
            s_id = generate_user_id(s)
            if not user_exists(s_id):
                ds.add(m.User(id=s_id, username=s,
                              password='data', role=role_student))
            elif get_user(s_id).role_name != 'Student':
                err_msg = s+(' already exists and is not a student.'
                             'You should not put their name into student name')
                ds.rollback()
                return err_msg
            user_ids.append(s_id)

        for user_id in user_ids:
            users.append(get_user(user_id))
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


# change the students in a class with class id
def change_class_students(class_id, student_names):
    # clean up all the white space in the string
    student_names_str = ''.join(student_names.split())
    # get role objects from the Role table
    role_student = get_role('Student')
    # Process the string to strip all the white space;
    # then split it over commas and join with commas
    student_names = student_names_str.split(',')
    # Check the correctness of the string to be strings delimited only by comma
    pattern_for_student_names = '[a-zA-Z](,[a-zA-Z])*'
    if (re.match(pattern_for_student_names, student_names_str) is None):
        err_msg = 'The pattern for student names is not correct'
        return err_msg
    student_ids = [generate_user_id(s) for s in student_names]
    the_class = get_class(class_id)

    # Delete the students that you chose to be removed from the class
    # if they are not in any other class
    # If they are in another class, remove the class from their class list
    for s in the_class.users:
        if s.role_name == 'Student' and (not (s.id in student_ids)):
            if len(s.classes) == 1:
                ds.delete(s)
            else:
                s.classes = [c for c in s.classes if c.id != class_id]
    ds.commit()
    # Check the that the students you are adding already exist if they don't,
    # create the student account and add the class to their class list
    for s in student_names:
        s_id = generate_user_id(s)
        if not user_exists(s_id):
            ds.add(m.User(id=s_id, username=s, password='data',
                          role=role_student, classes=[the_class],
                          labs=the_class.labs))
        else:
            the_classes = get_user(s_id).classes
            if not (class_id in [c.id for c in the_classes]):
                get_user(s_id)
    ds.commit()
    return ''


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
