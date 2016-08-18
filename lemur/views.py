# This file contains the view functions for all the templates this app will use
# The functions used in all the view functions can be found in utility.py
# This is meanly for code readability
# Libraries
# Standard library
import json
import ast

# Third-party libraries
from flask import (render_template, request, redirect, url_for,
                   flash)
from flask.ext.login import (login_user, logout_user, current_user,
                             login_required)
import requests

# Other modules
from lemur import (app, db, student_api_url, class_api_url)
from lemur import models as m
from lemur.utility_decorators import permission_required
from lemur.utility_generate_and_convert import (check_existence,
                                                serialize_lab_list,
                                                serialize_experiment_list,
                                                serialize_user_list,
                                                serialize_class_list,
                                                pack_labinfo_sent_from_client,
                                                format_download,
                                                normal_json,
                                                err_json,
                                                err_html)
from lemur.utility_find_and_get import (lab_exists,
                                        get_lab,
                                        get_experiment,
                                        get_user,
                                        get_class,
                                        get_all_lab,
                                        get_all_class,
                                        get_all_user,
                                        get_available_labs_for_user,
                                        get_experiments_for_lab,
                                        get_class_id_list,
                                        find_lab_list_for_user,
                                        find_all_labs,
                                        find_all_observations_for_labs)
from lemur.utility_modify import (delete_lab,
                                  modify_lab,
                                  duplicate_lab,
                                  change_lab_status,
                                  delete_observation,
                                  add_observation,
                                  add_observations_sent_by_students,
                                  add_user,
                                  change_user_info,
                                  delete_user,
                                  add_class,
                                  delete_class,
                                  change_class_users,
                                  populate_db_with_classes_and_professors,
                                  update_students_by_data_from_iris)
# Abbreviation for convenience
ds = db.session


# --- Common Side ---
# The app will be redirected to the user's main page
# if the user is not logged in, the user will be redirected to the login page
@app.route('/')
def main_page():
    if current_user.is_authenticated:
        user_home = {'SuperAdmin': 'superadmin_home',
                     'Admin': 'admin_home',
                     'Student': 'student_home'}
        return redirect(url_for(user_home[current_user.role_name]))
    return redirect(url_for('login'))


# Login page that will check user id and allow user access to the
# allowed pages
# It will be replaced by reed login page in the end
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        err_msg = check_existence(request.form, 'username')
        if err_msg != '':
            return render_template('login.html')
        user = get_user(request.form['username'])
        # check existence of the use
        if user is not None:
            # If the username is valid, redirect the user to
            # the corresponding homepage
            login_user(user, True)
            user_home = {'SuperAdmin': 'superadmin_home',
                         'Admin': 'admin_home',
                         'Student': 'student_home'}
            return redirect(url_for(user_home[user.role_name]))
    return render_template('login.html')


# Log out the user and redirect to the login page
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# Homepages
# Users will be redirected to one of these homepages after they
# log into the app according to their identity
@app.route('/student_home')
@login_required
def student_home():
    return render_template('student_home.html')


@app.route('/admin_home')
@permission_required(m.Permission.ADMIN)
def admin_home():
    return render_template('admin_home.html')


@app.route('/superadmin_home')
@permission_required(m.Permission.SUPERADMIN)
def superadmin_home():
    return render_template('superadmin_home.html')


# --- Student Side ---
# Page for student to select labs they want to enter data for
# A SuperAdmin can select among all the activated labs
# A student/Admin can only select labs among all the activated labs
# that he/she is in
@app.route('/student_select_lab')
@permission_required(m.Permission.DATA_ENTRY)
def student_select_lab():
    labs_query = get_available_labs_for_user(current_user)
    lab_list = serialize_lab_list(labs_query)
    return render_template('student_select_lab.html',
                           lab_list=lab_list)


# Page for student to enter data
@app.route('/student_data_entry/<lab_id>')
@permission_required(m.Permission.DATA_ENTRY)
def student_data_entry(lab_id):
    # Get lab information and its experiments information
    # and pack them to send to the template

    # student and admin can only access labs he/she is in
    # This checking is triggered when a student/admin tries to type
    # the lab id data entry page directly in url
    lab_ids = [lab.id for lab in current_user.labs]
    if (lab_id not in lab_ids) and current_user.role_name != 'SuperAdmin':
        err_msg = 'no power to access this page. The user can only access: {}'.format('\n'.join(lab_ids))
        return redirect(url_for('login',
                                err_msg=err_msg))
    lab_query = get_lab(lab_id)
    experiments_query = get_experiments_for_lab(lab_id)

    # check if the lab exists
    if not lab_exists(lab_id):
        err_msg = 'The lab with id: {} doesn\'t exist'.format(lab_id)
        return err_html(err_msg)

    # Convert queries into JSON format
    experiments = serialize_experiment_list(experiments_query)
    lab_info = serialize_lab_list([lab_query])

    return render_template('student_data_entry.html',
                           experiments=experiments, lab_info=lab_info)


# store incoming data into the database
@app.route('/_student_receive_data', methods=['POST'])
@permission_required(m.Permission.DATA_ENTRY)
def _student_receive_data():
    # get data from client
    jsonData = request.get_json()
    # check that data is in the appropriate format
    err_msg = check_existence(jsonData, 'observationsGroupByStudent')
    if err_msg != '':
        return err_json(err_msg)
    err_msg = add_observations_sent_by_students(jsonData['observationsGroupByStudent'])
    if err_msg != '':
        return err_json(err_msg)
    return normal_json(jsonData)


# --- Admin Side ---
# Main page for setting up and managing the labs
    # SuperAdmin can see/edit all the labs
    # Admin can only see/edit labs in his/her own zone
@app.route('/admin_create_and_manage_lab', methods=['GET', 'POST'])
@permission_required(m.Permission.LAB_SETUP)
def admin_create_and_manage_lab():
    current_labs = find_all_labs(current_user)
    class_ids = get_class_id_list(current_user)
    # If data sent by client is in correct format redirect to lab setup page
    # with user's entered data
    if request.method == 'POST':
        lab_info, err_msg = pack_labinfo_sent_from_client(request.form)
        if err_msg != '':
            return err_json(err_msg)
        return redirect(url_for('.admin_setup_labs', labinfo=lab_info))
    return render_template('admin_create_and_manage_lab.html',
                           current_labs=current_labs, class_ids=class_ids)


# fill in the experiment details of a lab
@app.route('/admin_setup_labs')
@permission_required(m.Permission.LAB_SETUP)
def admin_setup_labs():
    # translate data sent by user to a python list
    # Assume labinfo to be a python3 list(the security is guranteed
    # by the permission checking)
    labinfo = ast.literal_eval(request.args['labinfo'])
    class_ids = get_class_id_list(current_user)
    return render_template('admin_modify_lab.html', labinfo=labinfo,
                           class_ids=class_ids,
                           post_address='_admin_receive_setup_labs_data')


@app.route('/_admin_receive_setup_labs_data', methods=['POST'])
@permission_required(m.Permission.LAB_SETUP)
def _admin_receive_setup_labs_data():
    # receive the data, check the format and deserialize it
    jsonData = request.get_json()
    # Admin can only edit labs in his/her own zone
    # SuperAdmin can edit labs for anyone
    # This check has a problem: If two Admins have the same names now, they can
    # edit each other's labs
    err_msg = modify_lab(jsonData)
    if err_msg != '':
        return err_json(err_msg)
    return normal_json(jsonData)


# Change and edit the existing labs
@app.route('/admin_modify_lab/<lab_id>')
@permission_required(m.Permission.LAB_SETUP)
def admin_modify_lab(lab_id):
    # Collect the info of the current lab and send them to the template
    experiments_query = get_experiments_for_lab(lab_id)
    lab_query = get_lab(lab_id)
    # check the existence of the lab before modifying it
    if not lab_exists(lab_id):
        err_msg = ('The lab doesn\'t exist.'
                   'All the existing labs are: {}'.format(', '.join([lab.id for lab in get_all_lab()])))
        return err_html(err_msg)
    # get info to send to template
    class_ids = get_class_id_list(current_user)
    experiments = serialize_experiment_list(experiments_query)
    lab_info = serialize_lab_list([lab_query])[0]
    # Sort the list of experiments according to order and add them into labinfo
    sorted(experiments, key=lambda experiment: experiment['order'])
    lab_info['experiments'] = experiments
    return render_template('admin_modify_lab.html', labinfo=lab_info,
                           class_ids=class_ids,
                           post_address='_admin_modify_lab')


# Modify the labs in database
@app.route('/_admin_modify_lab', methods=['POST'])
@permission_required(m.Permission.LAB_SETUP)
def _admin_modify_lab():
    # receive the data, check the format and deserialize it
    lab_json = request.get_json()
    # Delete a lab's basic info, experiments info and observations info
    # Add a lab with basic info and experiments info
    err_msg = modify_lab(lab_json)
    if err_msg != '':
        return err_json(err_msg)
    return normal_json(lab_json)


# Duplicate an existing lab in database
@app.route('/_admin_duplicate_lab', methods=['POST'])
@permission_required(m.Permission.LAB_SETUP)
def _admin_duplicate_lab():
    # gather data
    jsonData = request.get_json()
    # check data format
    err_msg = check_existence(jsonData, 'labId')
    if err_msg != '':
        return err_json(err_msg)
    duplicate_lab(jsonData['labId'])
    return normal_json(jsonData)


# Delete a lab in database
@app.route('/_admin_delete_lab', methods=['POST'])
@permission_required(m.Permission.LAB_SETUP)
def _admin_delete_lab():
    jsonData = request.get_json()
    err_msg = check_existence(jsonData, 'labId')
    if err_msg != '':
        return err_json(err_msg)
    # Delete a lab's basic info, experiments info and observations info
    delete_lab(jsonData['labId'])
    return normal_json(jsonData)


# Changes a lab's status (activated, unactivated, downloadable) in database
@app.route('/_admin_change_lab_status/<new_status>', methods=['POST'])
@permission_required(m.Permission.LAB_SETUP)
def _admin_change_lab_status(new_status):
    jsonData = request.get_json()
    err_msg = check_existence(jsonData, 'labId')
    if err_msg != '':
        return err_json(err_msg)
    change_lab_status(jsonData['labId'], new_status)
    return normal_json(jsonData)


# select labs to review/edit data
# Admin can only select the data collected from his/her own zone
# SuperAdmin can view all the labs
@app.route('/admin_select_lab_for_data')
@permission_required(m.Permission.DATA_EDIT)
def admin_select_lab_for_data():
    # Get the list of labs with basic informati on according to
    # the current user's role
    lab_list = find_lab_list_for_user(current_user)
    return render_template('admin_select_lab_for_data.html', lab_list=lab_list)


# review/edit Data
@app.route('/admin_edit_data/<lab_ids>')
@permission_required(m.Permission.DATA_EDIT)
def admin_edit_data(lab_ids):
    # Get a list of lab_ids with which the observations are
    # to be retrieved
    lab_ids = json.loads(lab_ids)
    lab_ids_str = (',').join(lab_ids)
    # Get all the observations of the labs with lab_ids
    (observations, observations_by_student, _,
        err_msg, undownloadable_labs) = find_all_observations_for_labs(lab_ids)
    if err_msg == '':
        return render_template('admin_edit_data.html',
                               observations=observations,
                               student_data=observations_by_student,
                               lab_ids=lab_ids_str,
                               err_msg=err_msg,
                               undownloadable_labs=undownloadable_labs)
    else:
        return render_template('error_400.html', err_msg=err_msg), 400


# change data(backend)
@app.route('/_admin_change_data', methods=['POST'])
@permission_required(m.Permission.DATA_EDIT)
def _admin_change_data():
    # get data and check data format
    jsonData = request.get_json()
    err_msg = check_existence(jsonData, 'oldObservationIdsList',
                              'newObservationList')
    if err_msg != '':
        return err_json(err_msg)

    if not(isinstance(jsonData['oldObservationIdsList'], list) and
           isinstance(jsonData['newObservationList'], list)):
        err_msg = 'the value should be a list'
        return err_json(err_msg)

    delete_observation(jsonData['oldObservationIdsList'])
    err_msg = add_observation(jsonData['newObservationList'])
    if err_msg != '':
            return err_json(err_msg)
    # return success to the ajax call from flask
    return normal_json(jsonData)


# delete the data for a group in a lab
@app.route('/_admin_delete_data', methods=['POST'])
@permission_required(m.Permission.DATA_EDIT)
def _admin_delete_data():
    jsonData = request.get_json()
    err_msg = check_existence(jsonData, 'observationIdsToBeRemoved')
    if err_msg != '':
        return err_json(err_msg)

    if not(isinstance(jsonData['observationIdsToBeRemoved'], list)):
        err_msg = 'the value should be a list'
        return err_json(err_msg)
    delete_observation(jsonData['observationIdsToBeRemoved'])
    return normal_json(jsonData)


# format and download data
@app.route('/_admin_download_data/<lab_ids>')
@permission_required(m.Permission.DATA_EDIT)
def _admin_download_data(lab_ids):
    lab_ids = json.loads(lab_ids)

    # Query data to download
    # underscores are placeholders for data not currently needed
    (_, observations_by_student, experiment_names, err_msg, _) = find_all_observations_for_labs(lab_ids)
    if err_msg != '':
        return err_html(err_msg)
    else:
        # Format download is located in utility.py
        response = format_download(observations_by_student,
                                   experiment_names,
                                   lab_ids)
        return response


# --- Super Admin Side ---
# As a SuperAdmin, you can manage all the Admins' account
@app.route('/superadmin_create_and_manage_user', methods=['GET', 'POST'])
@permission_required(m.Permission.USER_MANAGE)
def superadmin_create_and_manage_user():
    err_msg = ''
    if request.method == 'POST':
        err_msg = add_user(request.form)
    if err_msg != '':
        return err_json(err_msg)
    # Get existing admins and class ids to send to the template
    user_list = serialize_user_list(get_all_user())
    class_ids = [c.id for c in get_all_class()]
    return render_template('superadmin_create_and_manage_user.html',
                           user_list=user_list, class_ids=class_ids)


# Modify the class a user belongs to
@app.route('/_superadmin_change_user_info', methods=['POST'])
@permission_required(m.Permission.USER_MANAGE)
def _superadmin_change_user_info():
    jsonData = request.get_json()
    # Check the correctness of data format
    err_msg = check_existence(jsonData, 'classIds', 'username', 'role')
    if err_msg != '':
        return err_json(err_msg)
    change_user_info(jsonData['username'], jsonData['role'], jsonData['classIds'])
    return normal_json(jsonData)


@app.route('/_superadmin_delete_user', methods=['POST'])
@permission_required(m.Permission.USER_MANAGE)
def _superadmin_delete_user():
    jsonData = request.get_json()
    # Check the correctness of data format
    err_msg = check_existence(jsonData, 'userIdToBeRemoved')
    if err_msg != '':
        return err_json(err_msg)
    delete_user(jsonData['userIdToBeRemoved'])
    return normal_json(jsonData)


# Update class/users info
@app.route('/_superadmin_update_info_from_iris', methods=['POST'])
@permission_required(m.Permission.USER_MANAGE)
def _superadmin_update_info_from_iris():
    jsonData = request.get_json()
    err_msg = check_existence(jsonData, 'message')
    if err_msg != '':
        return err_json(err_msg)

    if jsonData['message'] == 'update classes':
        class_data = json.loads(requests.get(class_api_url).text)
        if (len(class_data) == 0):
            return 'empty class data'
        err_msg = check_existence(class_data[0], 'subject', 'course_number',
                                  'term_code', 'instructors')
        if err_msg != '':
            return err_json(err_msg)
        warning_msg = populate_db_with_classes_and_professors(class_data)
        return normal_json(warning_msg)
    elif jsonData['message'] == 'update users':
        class_id_list = []
        if check_existence(jsonData, 'classIds'):
            class_id_list = json.loads(jsonData['classIds'])
        registration_data = json.loads(requests.get(student_api_url).text)
        if (len(registration_data) == 0):
            return 'empty registration data'
        err_msg = check_existence(registration_data[0], 'subject',
                                  'course_number', 'term_code', 'user_name',
                                  'first_name', 'last_name')
        if err_msg != '':
            return err_json(err_msg)
        warning_msg = update_students_by_data_from_iris(class_id_list, registration_data)
        return normal_json(warning_msg)
    else:
        err_msg = 'invalid message:{}'.format(jsonData['message'])
        return err_json(err_msg)


@app.route('/superadmin_create_and_manage_class', methods=['GET', 'POST'])
@permission_required(m.Permission.LAB_MANAGE)
def superadmin_create_and_manage_class():
    if request.method == 'POST':
        err_msg = add_class(request.form)
        if err_msg != '':
            return err_json(err_msg)
    # query professors' names and current classes from the database and
    # convert them into JSON format
    classes_query = get_all_class()
    all_users = get_all_user()
    current_classes = serialize_class_list(classes_query)

    return render_template('superadmin_create_and_manage_class.html',
                           current_classes=current_classes,
                           all_users=all_users)


# Delete students that are not in any classes after the deletion of the current
# class and the associated labs of the current classes
@app.route('/_superadmin_delete_class', methods=['POST'])
@permission_required(m.Permission.LAB_MANAGE)
def _superadmin_delete_class():
    jsonData = request.get_json()
    err_msg = check_existence(jsonData, 'classIdToBeRemoved')
    if err_msg != '':
        return err_json(err_msg)
    delete_class(jsonData['classIdToBeRemoved'])
    return normal_json(jsonData)


# Edit students in a class
@app.route('/_superadmin_modify_class', methods=['POST'])
@permission_required(m.Permission.LAB_MANAGE)
def _superadmin_modify_class():
    # get data from post request and check the correctness of data format
    jsonData = request.get_json()
    err_msg = check_existence(jsonData, 'classId', 'studentUserNames', 'professorUserNames')
    if err_msg != '':
        return err_json(err_msg)
    new_usernames = []
    if jsonData['studentUserNames'] is not None:
        new_usernames += jsonData['studentUserNames']
    if jsonData['professorUserNames'] is not None:
        new_usernames += jsonData['professorUserNames']
    err_msg = change_class_users(jsonData['classId'], new_usernames)
    if err_msg != '':
        return err_json(err_msg)
    return normal_json(jsonData)


# --- Error handling ---
@app.errorhandler(400)
def bad_request_error(error):
    return render_template('error_400.html'), 400


@app.errorhandler(404)
def not_found_error(error):
    return render_template('error_404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    ds.rollback()
    return render_template('error_500.html'), 500


# --- Utility ---
# Enable all the templates can access the class Permission
@app.context_processor
def inject_permissions():
    return dict(Permission=m.Permission)


# Make the requirments to the format of input fields global
@app.context_processor
def inject_patterns():
    return dict(pattern_for_name='[-a-zA-Z0-9?\s]{1,60}',
                pattern_for_name_hint=('must be a combination of some of the'
                                       ' following: number(s), question mark,'
                                       ' letter(s), hyphen(s) and white'
                                       ' space(s) with length between 1 and 60'
                                       ),
                pattern_for_experiment_description='.{,500}',
                pattern_for_experiment_description_hint=('no more than 500'
                                                         'characters'),

                pattern_for_value_candidates=('[0-9a-zA-Z\-]*'
                                              '(,[0-9a-zA-Z\-]*)*'),
                pattern_for_value_candidates_hint=('valueCandidates should'
                                                   'be in the format:N,C'),
                pattern_for_value_range=('[0-9]{1,10}[.]?[0-9]{0,10}'
                                         '-[0-9]{1,10}[.]?[0-9]{0,10}'),
                pattern_for_value_range_hint=('valueRange should be'
                                              'in the format:0.3-6.5'),
                pattern_for_class_time='[a-zA-Z]{4,7}[0-9]{2,4}',
                pattern_for_class_time_hint=('Class Time is a combination',
                                             'of semester and year. e.g. ',
                                             'FALL2016'))
