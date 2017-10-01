# Libraries
# Third-party libraries
from flask import make_response, render_template, jsonify

# Local
from lemur import (app, db)
ds = db.session


# --- Message/ID generator/decomposer ---
# Check the existence of args in a form
# and generate an error message accordingly
def check_existence(form, *expectedArgs):
    # Python variables should be named in snake_case, not camelCase.
    # Also, please specify what "form" means in this context -- an HTML form?
    # Also that should be -- you guessed it -- a docstring. -- RMD 2017-08-26
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


# Why does class_id not get the same separator? -- RMD 2017-08-26
def generate_class_id(class_name, class_time):
    return class_name+'_'+class_time


def generate_user_name(first_name, last_name):
    if first_name is None:
        first_name = ''
    if last_name is None:
        last_name = ''
    return first_name+' '+last_name


def decompose_lab_id(lab_id):
    return {'lab_name': lab_id.split(':')[0],
            'class_id': lab_id.split(':')[1]}
# ^ No need to duplicate splitting. Either store the split result to a
# variable, or decompose the tuple (eg: lab_name, class_id = lab_id.split(':'))
# -- RMD 2017-08-26


def decompose_class_id(class_id):
    return {'class_name': class_id.split('_')[0],
            'class_time': class_id.split('_')[1]}


# --- Serialization/Deserialization ---
# These the types of parameters/return values of these functions
# are relatively flexible. This group of functions receives a list
# of objects and convert it into a python list of dictionaries
# (close to JSON format) with the info contained by these objects

# None of these functions are actually serializers. You're changing the shape
# of your data, from one Python in-memory representation to another, but
# serialization would mean converting data to a format appropriate for writing
# to a file or transmitting over the wire (e.g. Python structures to a JSON
# string, or Pickling a python object.) I'd recommend clearer names --
# `convert_lab_list_format` et al, say. -- RMD 2017-08-26
def serialize_lab_list(lab_list):
    labs = []

    for lab in lab_list:
        if lab.the_class:
            class_id = lab.the_class.id
        else:
            class_id = None
            prof_name = ','.join([u.name for u in lab.users if (u.name and ((u.role_name == 'SuperAdmin') or (u.role_name == 'Admin')))])
            # ^ That is some line length you've got there. -- RMD 2017-08-26
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
    user_list_dict = []
    for user in user_list:
        classes = [c.id for c in user.classes]
        labs = [lab.id for lab in user.labs]
        user_list_dict.append({'username': user.id,
                               'name': user.name,
                               'role_name': user.role_name,
                               'classes': classes,
                               'labs': labs})
    return user_list_dict


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
    return lab_info, '' # Why on _earth_ does this return a 2-tuple with empty string? -- RMD 2017-08-26


# Change the datastructure that stores the observation data from using
# experiment as key to using student as key
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
    # ^ Could split on 0 -- RMD 2017-08-26
    if term_index == '1':
        year = str(int(year) - 1)
    if term_index in convert_table:
        return convert_table[term_index] + year
    return ''


# This method will remove all the classes with course_number '470';
# for any of other classes, combine the instructor field of all sections
def cleanup_class_data(class_data):
    cleaned_class_data = []
    course_number_set = set()
    for c in class_data:
        if c['course_number'] != '470':
            course_number_set.add(c['course_number'])
            course_number_list = list(course_number_set)
    for course_number in course_number_list:
        # Get all the sections that have the same course number
        the_class_list = list(filter(lambda c: c['course_number'] == course_number, class_data))
        # since the_class_list is impossible to be empty, we put all the
        # instructors' info into the first course dictionary
        the_class = the_class_list[0]
        class_instructor_usernames = [instructor['username'] for instructor in the_class['instructors']]
        for c in the_class_list:
            for instructor in c['instructors']:
                if not (instructor['username'] in class_instructor_usernames):
                    the_class['instructors'].append(instructor)
                    cleaned_class_data.append(the_class)
    return cleaned_class_data


# --- Response object generators ---
# Format the string csv to be downloaded
def format_download(observations_by_student, experiment_names, lab_ids):
    # Add two additional columns besides experiment names
    experiment_names = ['Student Name', 'Lab ID'] + experiment_names

    dt = '\t'
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
