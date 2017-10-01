# Libraries
# Local
from lemur import models as m
from lemur.lemur import app, db
from lemur.utility_generate_and_convert import (
    check_existence,
    generate_lab_id,
    generate_experiment_id,
    generate_observation_id,
    generate_class_id,
    generate_user_name,
    decompose_lab_id,
    tranlate_term_code_to_semester,
    cleanup_class_data
)
from lemur.utility_find_and_get import (
    lab_exists,
    experiment_exists,
    class_exists,
    observation_exists,
    user_exists,
    get_lab,
    get_observation,
    get_user,
    get_class,
    get_role,
    get_all_class,
    get_all_user,
    get_experiments_for_lab,
    get_observations_for_experiment,
    find_lab_copy_id
)
ds = db.session


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
    lab_status = 'Unactivated'
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
                experiments_for_lab.append(
                    m.Experiment(
                        lab_id=lab_id,
                        id=experiment_id,
                        name=experiment_name,
                        description=e['description'],
                        order=e['order'],
                        value_type=e['valueType'],
                        value_range=e['valueRange'],
                        value_candidates=e['valueCandidates']
                    )
                )

    the_lab = m.Lab(id=lab_id, name=lab_json['labName'],
                    description=lab_json['labDescription'],
                    status=lab_status,
                    the_class=the_class,
                    experiments=experiments_for_lab,
                    users=class_users)
    ds.add(the_lab)
    ds.commit()
    return ''


# copy a old lab and rename the new lab with 'copy'+index+'-'+old_lab_name
def duplicate_lab(old_lab_id):
    # Find a new lab id according to the old lab id
    new_lab_id = find_lab_copy_id(old_lab_id)
    # Copy info from old lab and add to new lab
    old_lab = get_lab(old_lab_id)
    # A lab can only belong to one class at this point
    old_class = get_class(old_lab.the_class.id)
    new_lab = m.Lab(id=new_lab_id,
                    name=decompose_lab_id(new_lab_id)['lab_name'],
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
    # Automatically delete all the data in the lab if it's made unavailable
    if new_status == "Unactivated":
        experiments_query = get_experiments_for_lab(lab_query.id)
        for e in experiments_query:
            for d in get_observations_for_experiment(e.id):
                ds.delete(d)

    ds.commit()


# --- Manage observations ---
# delete observation from a list of observation ids sent from client
def delete_observation(old_observation_ids_list):
    err_msg = ''
    # delete all the old data by old observation_id
    for observation_id in old_observation_ids_list:
        observations_query = get_observation(observation_id)
        # Check the existence of the observation to be deleted
        if observation_exists(observation_id):
            ds.delete(observations_query)
            # err_msg += ('To be deleted observation:' +
            #             '{} doesn\'t exits in db\n'.format(observations_query))
    ds.commit()
    return err_msg


# add observation from a list JSON format observations sent from client
# This function is invoked when admin edits data of a lab
def add_observation(new_observations_list):
    warning_msg = ''
    for d in new_observations_list:
        err_msg = check_existence(d, 'studentName', 'observationData',
                                  'experimentId', 'observationId')
        if err_msg != '':
            return err_msg

    for d in new_observations_list:
        # Check if the observation name already repetes among all the
        # observations to be added into the database and rename it if necessary
        index = 1
        tmp_student_name = d['studentName']
        tmp_observation_id = d['observationId']
        while observation_exists(tmp_observation_id):
            tmp_student_name = d['studentName'] + '('+str(index)+')'
            tmp_observation_id = generate_observation_id(d['experimentId'], tmp_student_name)
            index += 1
            # warning_msg = ('repeated observation id:{} in this lab so the ' +
            #                'current, modified entry will be renamed to ' +
            #                '{}'.format(d['observationId'], tmp_observation_id))

        # Capitalize every input
        ds.add(m.Observation(experiment_id=d['experimentId'],
                             id=tmp_observation_id,
                             student_name=tmp_student_name,
                             datum=d['observationData'].upper()))

    ds.commit()
    return warning_msg


# add observations sent by students into the database
# This function is invoked when a student send a group of data
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

        for ob in student['observationsForOneExperiment']:
            err_msg = check_existence(ob, 'labId', 'experimentName',
                                      'observation')
            if err_msg != '':
                return err_msg
            # If everything is correct add the data to the database
            experiment_id = generate_experiment_id(ob['labId'], ob['experimentName'])

            # To avoid repetition in student name field since it's used as part
            # of key for an input we add an unique index at the end of
            # each student name
            tmp_student_name = student['studentName']+'(1)'
            observation_id = generate_observation_id(experiment_id,
                                                     tmp_student_name)
            index = 2
            while observation_exists(observation_id):
                tmp_student_name = student['studentName'] + '('+str(index)+')'
                observation_id = generate_observation_id(experiment_id,
                                                         tmp_student_name)
                index += 1
                # Capitalize every input
            if not observation_exists(observation_id):
                ds.add(m.Observation(experiment_id=experiment_id,
                                     id=observation_id,
                                     student_name=tmp_student_name,
                                     datum=ob['observation'].upper()))

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
        name = None
        if 'name' in user_info:
            name = user_info['name']

        new_user = m.User(id=user_info['username'],
                          name=name,
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
    if class_ids:
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
    # Note: students is optional i.e. it can be undefined
    err_msg = check_existence(class_info, 'className', 'classTime')
    if err_msg != '':
        return err_msg
    users = []
    usernames = []
    # create new class with data sent by client to be added to database
    new_class_id = generate_class_id(
        class_info['className'], class_info['classTime'])

    if not class_exists(new_class_id):
        if 'professors' in class_info:
            for p in class_info.getlist('professors'):
                if not user_exists(p):
                    err_msg = 'The professor with id:{} doesn\'t exist.'.format(p)
                    return err_msg
                else:
                    usernames.append(p)
        if 'students' in class_info:
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
        if not(u.id in str(new_users)):
            u.classes = [c for c in u.classes if c.id != class_id]
            new_lab_list = []
            for lab in u.labs:
                if lab.the_class.id != class_id:
                    new_lab_list.append(lab)

            u.labs = new_lab_list

    ds.commit()
    return ''


# --- Initialize Classes and Users by getting data from Iris ---
# Populate the database with classes and their corresponding professors
# Note: This needs to be invoked before update_users_by_data_from_iris
# The existing professors will not be deleted even if they don't teach
# any class
def populate_db_with_classes_and_professors(class_data):
    class_data = cleanup_class_data(class_data)
    for c in class_data:
        class_name = c['subject'] + c['course_number']
        class_time = tranlate_term_code_to_semester(c['term_code'])
        class_professor_info_list = c['instructors']
        class_professor_ids = [p['username'] for p in class_professor_info_list]
        class_professors = []
        for p in class_professor_info_list:
            if not user_exists(p['username']):
                name = generate_user_name(p['first_name'], p['last_name'])
                ds.add(m.User(id=p['username'], name=name, role=get_role('Admin')))
                ds.commit()

            the_user = get_user(p['username'])
            class_professors.append(the_user)
        if class_name and class_time:
            class_id = generate_class_id(class_name, class_time)
            # If the class already exists, update the professors and keep
            # the students
            if class_exists(class_id):
                the_class = get_class(class_id)
                # handle the change of class and the labs associated with it
                old_class_professors = [u for u in the_class.users if ((u.role_name == 'Admin') or (u.role_name == 'SuperAdmin'))]
                for p in class_professors:
                    # Add the class to the professor's class list if it is not
                    # the list now.
                    if not (class_id in [c.id for c in p.classes]):
                        p.classes.append(the_class)
                        for lab in the_class.labs:
                            if not (lab in p.labs):
                                p.labs.append(lab)

                ds.commit()
                # Remove the class from the old professor's class list
                # if the professor is no longer in the class's user list.
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
def update_students_by_data_from_iris(class_id_list, registration_data):
    all_classes = get_all_class()
    selected_classes = [c for c in all_classes if c.id in class_id_list]
    registration_by_class = {}
    warning_msg = ''
    # A registration_object looks like
    # {"user_name":"fake1","course_id":"10256","term_code":"201501",
    # "subject":"BIOL","course_number":"101","section":"FTN",
    # "first_name":"Fake", "last_name":"One"}

    # Add the students in the received data into the database
    for registration_object in registration_data:
        username = registration_object['user_name']
        invalid_list = [None, 'undefined', 'null', '']
        # Since username is our key for User object, it cannot be empty
        # If that happens, we skip the current user
        if username in invalid_list:
            continue
        name = generate_user_name(registration_object['first_name'],
                                  registration_object['last_name'])
        class_id = generate_class_id((registration_object['subject'] +
                                      registration_object['course_number']),
                                     tranlate_term_code_to_semester(registration_object['term_code']))
        # only students who registered courses in the list will be updated
        if class_id not in class_id_list:
            continue
        # If the class exists in the database, update
        if class_exists(class_id):
            the_class = get_class(class_id)
            # If user already exists, add the class into the class list of the
            # user;
            # otherwise, create a user with the class
            if user_exists(username):
                the_user = get_user(username)
                if not (class_id in [c.id for c in the_user.classes]):
                    the_user.classes.append(the_class)
                    for lab in the_class.labs:
                        if not (lab in the_user.labs):
                            the_user.labs.append(lab)
            else:
                the_user = m.User(id=username, name=name, classes=[the_class],
                                  role=get_role('Student'), labs=the_class.labs)
                ds.add(the_user)

        # else return a warning message to notify the user
        else:
            warning_msg += ('class_id: ' + class_id +
                            ' doesn\'t exist in database\n')

        # for efficiency: otherwise we have to loop through
        # registration_data many times
        if class_id in registration_by_class:
            registration_by_class[class_id].append(username)
        else:
            registration_by_class[class_id] = []

    # Check the students of the classes in the database and update them
    # according to the received data
    for c in selected_classes:
        # If the class exists in the received data, compare
        # the users of the class in database and data
        if c.id in registration_by_class:
            # Keep the admins/superadmins of the class
            class_new_users = [u for u in c.users if ((u.role_name == 'Admin') or (u.role_name == 'SuperAdmin'))]
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


# Delete all students in the database
# The current function will not report any warning messages
def delete_all_students():
    for u in get_all_user():
        if u.role_name == "Student":
            ds.delete(u)

    ds.commit()
    return ''
