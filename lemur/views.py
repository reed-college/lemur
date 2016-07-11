# Libraries
# Standard library
import json
import ast

# Third-party libraries
from flask import (render_template, request, redirect, url_for,
                   flash)
from flask.ext.login import (login_user, logout_user, current_user,
                             login_required)

# Other modules
from lemur import (app, db, class_time, current_time)
from lemur import models as m
from lemur.utility import *
# Abbreviation for convenience
ds = db.session


# --- Common Side ---
# Login page that will check user id and allow user access to the
# allowed pages
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        err_msg = check_existence(request.form, 'username')
        if err_msg != '':
            return render_template('login.html')
        user_id = generate_user_id(request.form['username'])
        user = get_user(user_id)
        # check existence of the user and the user's password
        if user is not None and user.verify_password(request.form['password']):
            # When both the username and password are valid then redirect to
            # the corresponding home page
            login_user(user, True)
            user_home = {'SuperAdmin': 'superadmin_home',
                         'Admin': 'admin_home',
                         'Student': 'student_home'}
            return redirect(url_for(user_home[user.role_name]))
            flash('Invalid username or password')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# homepages
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
@app.route('/student_enter_data')
@permission_required(m.Permission.DATA_ENTRY)
def student_enter_data():
    labs_query = get_labs_for_user(current_user)
    lab_list = serialize_lab_list(labs_query)['lab_list']
    return render_template('student_enter_data.html',
                           lab_list=lab_list)


# Page for student data entry with the right lab id
@app.route('/student_data_entry/<lab_id>')
@permission_required(m.Permission.DATA_ENTRY)
def student_data_entry(lab_id):
    # Get lab information and its experiments information
    # and pack them to send to the template
    # student and admin can only access labs he/she is in
    lab_ids = [lab.id for lab in current_user.labs]
    if (lab_id not in lab_ids) and current_user.role_name != 'SuperAdmin':
        return redirect(url_for('login',
                                err_msg='no power to access this page'))
    lab_query = get_lab(lab_id)
    experiments_query = get_experiments_for_lab(lab_id)

    # check if the lab exists
    if not lab_exists(lab_id):
        err_msg = 'The lab doesn\'t exist'
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
@app.route('/admin_setup_labs_and_data_access', methods=['GET', 'POST'])
@permission_required(m.Permission.LAB_SETUP)
def admin_setup_labs_and_data_access():
    current_labs = find_all_labs(current_user)
    class_names = serialize_class_name_list()
    prof_names = serialize_prof_name_list()
    # If data sent by client is in correct format redirect to lab setup page
    # with user's entered data
    if request.method == 'POST':
        lab_info, err_msg = pack_labinfo_sent_from_client(request.form)
        if err_msg != '':
            return err_json(err_msg)
        return redirect(url_for('.admin_setup_labs', labinfo=lab_info))
    return render_template('admin_setup_labs_and_data_access.html',
                           current_labs=current_labs, class_names=class_names,
                           prof_names=prof_names)


# fill in the experiment details of a lab
@app.route('/admin_setup_labs')
@permission_required(m.Permission.LAB_SETUP)
def admin_setup_labs():
    # translate data sent by user to a python list
    # Assume labinfo to be a python3 list(the security is guranteed
    # by the permission checking)
    labinfo = ast.literal_eval(request.args['labinfo'])
    class_names = serialize_class_name_list()
    prof_names = serialize_prof_name_list()
    return render_template('admin_modify_lab.html', labinfo=labinfo,
                           class_names=class_names, prof_names=prof_names,
                           post_address='_admin_receive_setup_labs_data')


@app.route('/_admin_receive_setup_labs_data', methods=['POST'])
@permission_required(m.Permission.LAB_SETUP)
def _admin_receive_setup_labs_data():
    # receive the data, check the format and deserialize it
    jsonData = request.get_json()
    err_msg = check_existence(jsonData, 'labName', 'className', 'classTime',
                                        'professorName', 'labDescription',
                                        'experiments', 'oldLabId')
    if err_msg != '':
        return (None, err_msg)
    class_id = generate_class_id(jsonData['className'], jsonData['classTime'])
    # Admin can only edit labs in his/her own zone
    # SuperAdmin can edit labs for anyone
    # This check has a problem: If two Admins have the same names now, they can
    # edit each other's labs
    err_msg = check_power_to_add_lab(current_user, jsonData['professorName'],
                                     class_id)
    if err_msg != '':
        return err_json(err_msg)
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
                   'All the existing labs are:{}'.format(find_all_labs(current_user)))
        return err_html(err_msg)
    # get info to send to template
    class_names = serialize_class_name_list()
    prof_names = serialize_prof_name_list()
    experiments = serialize_experiment_list(experiments_query)
    lab_info = serialize_lab_list([lab_query])[0]
    # Sort the list of experiments according to order and add them into labinfo
    sorted(experiments, key=lambda experiment: experiment['order'])
    lab_info['experiments'] = experiments
    return render_template('admin_modify_lab.html', labinfo=lab_info,
                           class_names=class_names, prof_names=prof_names,
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


# Duplicate an existing lab
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


# Delete labs
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


# Changes lab status (activated, unactivated, downloadable)
@app.route('/_admin_change_status/<new_status>', methods=['POST'])
@permission_required(m.Permission.LAB_SETUP)
def _admin_change_status(new_status):
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
    # Get all the observations of the labs with lab_ids
    (observations, observations_by_student, _,
        err_msg, undownloadable_labs) = find_all_observations_for_labs(lab_ids)
    if err_msg == '':
        return render_template('admin_edit_data.html',
                               observations=observations,
                               student_data=observations_by_student,
                               lab_ids=lab_ids,
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
    lab_ids, err_msg = deserialize_lab_id(lab_ids)
    if err_msg != '':
        return err_html(err_msg)
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
@app.route('/superadmin_manage_admins', methods=['GET', 'POST'])
@permission_required(m.Permission.USER_MANAGE)
def superadmin_manage_admins():
    err_msg = ''
    if request.method == 'POST':
        err_msg = add_admin(request.form)
    if err_msg != '':
        return err_json(err_msg)
    # Get existing admins to send to the template
    admins_query = get_all_admin()
    current_admins = serialize_admin_list(admins_query)
    return render_template('superadmin_manage_admins.html',
                           current_admins=current_admins)


@app.route('/_superadmin_delete_admin', methods=['POST'])
@permission_required(m.Permission.USER_MANAGE)
def _superadmin_delete_admin():
    jsonData = request.get_json()
    # Check the correctness of data format
    err_msg = check_existence(jsonData, 'adminIdToBeRemoved')
    if err_msg != '':
        return err_json(err_msg)
    delete_admin(jsonData['adminIdToBeRemoved'])
    return normal_json(jsonData)


@app.route('/_superadmin_modify_admin', methods=['POST'])
@permission_required(m.Permission.USER_MANAGE)
def _superadmin_modify_admin():
    jsonData = request.get_json()
    # Check the correctness of data format
    err_msg = check_existence(jsonData, 'adminId', 'password')
    if err_msg != '':
        return err_json(err_msg)
    change_admin_password(jsonData['adminId'], jsonData['password'])
    return normal_json(jsonData)


@app.route('/superadmin_manage_classes', methods=['GET', 'POST'])
@permission_required(m.Permission.LAB_MANAGE)
def superadmin_manage_classes():
    if request.method == 'POST':
        err_msg = add_class(request.form)
        if err_msg != '':
            return err_json(err_msg)
    # query professors' names and current classes from the database and
    # convert them into JSON format
    classes_query = get_all_class()
    prof_names = serialize_prof_name_list()
    current_classes = serialize_class_list(classes_query)

    return render_template('superadmin_manage_classes.html',
                           current_classes=current_classes,
                           prof_names=prof_names)


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
    err_msg = check_existence(jsonData, 'classId', 'studentNames')
    if err_msg != '':
        return err_json(err_msg)
    err_msg = change_class_students(jsonData['classId'],
                                    jsonData['studentNames'])
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


# Whenever a CSRF validation fails, it will return a 400 response.
# @csrf.error_handler
# def csrf_error(reason):
#     return render_template('csrf_error.html', reason=reason), 400


# --- Utility ---
# Enable all the templates can access the class Permission
@app.context_processor
def inject_permissions():
    return dict(Permission=m.Permission)


# Manually set all the candidates of class_time and current_time since
# in most case only the data in one semester will be used at one time
@app.context_processor
def inject_class_time():
    return dict(class_time=class_time, current_time=current_time)


# Add the demand to the format of the inputs
@app.context_processor
def inject_patterns():
    return dict(patter_for_name='[-a-zA-Z0-9\s]{1,60}',
                pattern_for_name_hint=('must be a combination of number(s),'
                                       'letter(s), hyphen(s) and white'
                                       'space(s) with length between 1 and 60'
                                       ),
                pattern_for_value_candidates='[0-9a-zA-Z\-]*(,[0-9a-zA-Z\-]*)*',
                pattern_for_value_candidates_hint='valueCandidates should be in the format:N,C',
                pattern_for_value_range='[0-9]{1,10}[.]?[0-9]{0,10}-[0-9]{1,10}[.]?[0-9]{0,10}',
                pattern_for_value_range_hint='valueRange should be in the format:0.3-6.5')
