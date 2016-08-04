# This is file contains a unit test suit which completely test the backend
# functions of our app.
# Note:
# 1.We create some random functions before the test suit to add randomness to
# our tests.
# 2.Some later tests use some of the previous test to avoid code repetitions.
# This should be fully justified since the functions used have already passed
# previous tests. Besides, none of the previous functions use the later
# functions to avoid cyclic testing.
# 3.The tests are not enough to cover all the possibilities at this point

# Libraries
# Standard library
import unittest
import json
from random import choice, randint, shuffle, seed
from datetime import datetime
from string import ascii_lowercase, ascii_uppercase, digits

# Third-party libraries
from bs4 import BeautifulSoup
from werkzeug.datastructures import MultiDict

# Other modules
from lemur import app, db
from lemur import models as m
from lemur import utility as u
from db_populate import populate_db
ds = db.session


# --- Some helper functions used to add randomness into our tests ---
# generate a random combination of letters(both upper and lower) and digits
# with a random length within the interval
def randlength_word(min_len=5, max_len=10):
    return ''.join(choice(ascii_lowercase + ascii_uppercase +
                   digits) for i in range(randint(min_len, max_len)))


# generate a random lab status
def rand_lab_status(status=['Activated', 'Unactivated', 'Downloadable']):
    return status[randint(0, len(status)-1)]


# generate a random experiment order
def rand_order(min=1, max=100):
    return randint(min, max)


# generate a random value type
def rand_value_type(value_types=['Text', 'Number']):
    return value_types[randint(0, len(value_types)-1)]


# generate a random value range in required format
def rand_value_range(min=0, max=10000):
    return (str(randint(min, max))+'.'+str(randint(min, max)) +
            '-'+str(randint(min, max))+'.'+str(randint(min, max)))


# generate a list of random value candidates(the number of which is random)
# in required format
def rand_value_candidates(min_number=1, max_number=10):
    candidates = randlength_word()
    for _ in range(randint(min_number-1, max_number-1)):
        candidates += (randlength_word()+',')
    return candidates


# generate a random lab id in the required format
def rand_lab_id():
    return randlength_word()+':'+randlength_word()


# generate a random experiment id in the required format
def rand_experiment_id():
    return rand_lab_id()+':'+randlength_word()


# generate a random value for classTime attribute in Class class
def rand_classtime(classtime_list=['16fall', '17spring', '17fall']):
    return classtime_list[randint(0, len(classtime_list)-1)]


def rand_classid():
    return randlength_word()+'_'+rand_classtime()


# generate a power lists
def rand_powers():
    m.Role.insert_roles()
    permission_list = [m.Permission.DATA_ENTRY,
                       m.Permission.DATA_EDIT,
                       m.Permission.LAB_SETUP,
                       m.Permission.ADMIN,
                       m.Permission.LAB_MANAGE,
                       m.Permission.USER_MANAGE,
                       m.Permission.SUPERADMIN]
    shuffle(permission_list)
    return [u.get_power(p) for p in
            permission_list[0:randint(1, len(permission_list))]]


# Generate a random value for role_name attribute in User class
def rand_role(roles=['SuperAdmin', 'Admin', 'Student']):
    return roles[randint(0, len(roles)-1)]


# Generate a random value for role_name attribute in User class
# among all the possible admin role names
def rand_admin(roles=['SuperAdmin', 'Admin']):
    return roles[randint(0, len(roles)-1)]


# Generate a random integer which is the number of a loop in many testing
# functions
def rand_round(min_round=1, max_round=5):
    return randint(min_round, max_round)


# Generate a random list of students in string format with comma as delimitor
def rand_student_names(number=5):
    s = ''
    for _ in range(number):
        username = randlength_word()
        # Avoid repetition of username
        while s.find(username) != -1:
            username = randlength_word()
        s += (username+',')
    s = s.rstrip(',')
    return s


class TestCase(unittest.TestCase):
    # this is automatically called for us when we run the test
    def setUp(self):
        # It disables the error catching during request handling so that we get
        # better error reports when performing test requests against the
        # application.
        app.config['TESTING'] = True
        # The database used for this suit of tests is not the one used by the
        # app. Before we run this test, we need to create a local database
        # called lemur_test
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost/lemur_test'
        self.app = app.test_client()
        # Create all the tables
        db.create_all()
        # Insert all the roles(Student, Admin, SuperAdmin) that will be used
        m.Role.insert_roles()
        # Set a random seed according to current time
        seed(datetime.now())

    # tidy up after a test has been run
    def tearDown(self):
        # remove and clean the database completely
        ds.remove()
        db.drop_all()

    # ---- Other helper functions ---
    # Log in the user and redirect to a corresponding page
    def login(self, username):
        return self.app.post('/login', data=dict(
               username=username), follow_redirects=True)

    # Log out the user and redirect to a corresponding page
    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    # Decode a response object and return its data in the beutiful soup format
    def decode(self, response, format='utf-8'):
        html = response.data.decode('utf-8')
        soup = BeautifulSoup(html, 'html5lib')
        return soup

    # Generate a json format dictionary that consists of information needed to
    # create a new lab with random values
    def construct_lab_json(self):
        lab_json = {'labName': randlength_word(),
                    'classId': rand_classid(),
                    'labDescription': randlength_word(),
                    'experiments': [],
                    'oldLabId': rand_lab_id()
                    }
        for i in range(rand_round()):
            exp_json = {'name': randlength_word(),
                        'description': randlength_word(),
                        'order': rand_order(),
                        'valueType': rand_value_type(),
                        'valueRange': rand_value_range(),
                        'valueCandidates': rand_value_candidates()

                        }
            lab_json['experiments'].append(exp_json)
        return lab_json

    # Construct a lab with experiments which have observations input by
    # students(they will be stored in the database before the function returns)
    def construct_lab_observations(self, student_num=5, experiment_num=5):
        student_role = u.get_role('Student')
        students = []
        for _ in range(student_num):
            student = self.test_create_user()
            student.role = student_role
            students.append(student)
        lab = self.test_create_lab()
        lab.users = students
        for j in range(experiment_num):
            experiment = self.test_create_experiment(lab.id)
            for k in range(student_num):
                observation = self.test_create_observation(experiment.id)
                observation.student_name = students[k].name
                experiment.observations.append(observation)
            lab.experiments.append(experiment)
        return lab

    # Construct and add a class for a lab to be set up according to the info of
    # the lab in the lab_json provided
    def add_a_class_for_lab_json(self, lab_json):
        # Without the existence of the class in the database,
        # the lab which belongs to this class can't be added
        class_info = u.decompose_class_id(lab_json['classId'])
        the_class = m.Class(id=lab_json['classId'],
                            name=class_info['class_name'],
                            time=class_info['class_time'])
        ds.add(the_class)
        ds.commit()

    # --- Testing functions(no interaction with database) for functions in utility.py ---
    # Note: some of these tests seem trivial. For the completeness of the
    # testing, we still keep them.
    def test_check_existence(self):
        key1 = 'key1'
        key2 = 'key2'
        key3 = 'key3'
        form = {key1: 'value1', key2: 'value2'}
        success_msg = ''
        err_msg = key3+' is not defined\n'
        self.assertEqual(u.check_existence(form, key1, key2), success_msg)
        self.assertEqual(u.check_existence(form, key1, key3), err_msg)

    def test_generate_err_msg(self):
        name1 = 'name1'
        value1 = 'value1'
        name2 = 'name2'
        value2 = 'value2'
        expected_msg = (name1+':'+value1+' and '+name2 +
                        ':'+value2+' are different')
        self.assertEqual(u.generate_err_msg(name1, value1, name2, value2),
                         expected_msg)

    def test_generate_lab_id(self):
        lab_name = randlength_word()
        class_id = rand_classid()
        expected_lab_id = lab_name + ':' + class_id
        generated_lab_id = u.generate_lab_id(lab_name, class_id)
        self.assertEqual(generated_lab_id, expected_lab_id)

    def test_generate_experiment_id(self):
        lab_id = randlength_word()
        experiment_name = randlength_word()
        expected_experiment_id = lab_id+':'+experiment_name
        generated_experiment_id = u.generate_experiment_id(lab_id, experiment_name)
        self.assertEqual(generated_experiment_id, expected_experiment_id)

    def test_generate_observation_id(self):
        experiment_id = randlength_word()
        student_name = randlength_word()
        expected_observation_id = experiment_id+':'+student_name
        self.assertEqual(u.generate_observation_id(experiment_id, student_name),
                         expected_observation_id)

    def test_generate_class_id(self):
        class_name = randlength_word()
        class_time = rand_classtime()
        expected_class_id = class_name+'_'+class_time
        self.assertEqual(u.generate_class_id(class_name, class_time),
                         expected_class_id)

    def test_decompose_lab_id(self):
        lab_name = randlength_word()
        class_id = rand_classid()
        lab_id = u.generate_lab_id(lab_name, class_id)
        lab_info = u.decompose_lab_id(lab_id)
        self.assertEqual(lab_info['lab_name'], lab_name)
        self.assertEqual(lab_info['class_id'], class_id)

    def test_decompose_class_id(self):
        class_name = randlength_word()
        class_time = randlength_word()
        class_id = u.generate_class_id(class_name, class_time)
        class_info = u.decompose_class_id(class_id)
        self.assertEqual(class_info['class_name'], class_name)
        self.assertEqual(class_info['class_time'], class_time)

    # --- Test data models in models.py ---
    # Notes:
    # 1.These tests don't check the relationship related values between
    # different data models. Tests for these relationships will be performed
    # later. E.g. experiments, users, classes will not be assigned and
    # tested when we test the Lab class.
    # 2.This group of functions check the id of an object before creating the
    # object with that id and regenerate if it comes across a repetition.
    # In this way, we avoid the error of repetition of id in database

    def test_create_class(self):
        name = randlength_word()
        time = randlength_word()
        class_id = u.generate_class_id(name, time)
        while ds.query(m.Class).filter(m.Class.id == class_id).count() != 0:
            name = randlength_word()
            time = randlength_word()
            class_id = u.generate_class_id(name, time)
        the_class = m.Class(id=class_id, name=name, time=time)
        ds.add(the_class)
        ds.commit()
        class_query = ds.query(m.Class).filter(m.Class.id == class_id).first()
        self.assertEqual(class_query.id, class_id)
        self.assertEqual(class_query.name, name)
        self.assertEqual(class_query.time, time)
        return class_query

    def test_create_lab(self):
        the_class = self.test_create_class()
        name = randlength_word()
        class_id = the_class.id
        description = randlength_word()
        status = 'Activated'
        lab_id = u.generate_lab_id(name, class_id)
        while ds.query(m.Lab).filter(m.Lab.id == lab_id).count() != 0:
            class_id = rand_classid()
            description = randlength_word()
            lab_id = u.generate_lab_id(name, class_id)

        lab = m.Lab(id=lab_id, name=name, the_class=the_class,
                    description=description, status=status)
        ds.add(lab)
        ds.commit()
        lab_query = ds.query(m.Lab).filter(m.Lab.id == lab_id).first()
        self.assertEqual(lab_query.name, name)
        self.assertEqual(lab_query.class_id, class_id)
        self.assertEqual(lab_query.description, description)
        self.assertEqual(lab_query.status, status)
        return lab_query

    def test_create_experiment(self, lab_id=rand_lab_id()):
        name = randlength_word()
        description = randlength_word()
        order = rand_order()
        value_type = rand_value_type()
        value_range = rand_value_range()
        value_candidates = rand_value_candidates()
        experiment_id = u.generate_experiment_id(lab_id, name)
        while ds.query(m.Experiment).filter(m.Experiment.id == experiment_id).count() != 0:
            name = randlength_word()
            lab_id = rand_lab_id()
            experiment_id = u.generate_experiment_id(lab_id, name)
        experiment = m.Experiment(id=experiment_id, name=name,
                                  description=description, order=order,
                                  value_type=value_type,
                                  value_range=value_range,
                                  value_candidates=value_candidates)
        ds.add(experiment)
        ds.commit()
        experiment_query = ds.query(m.Experiment).filter(m.Experiment.id == experiment_id).first()
        self.assertEqual(experiment_query.name, name)
        self.assertEqual(experiment_query.description, description)
        self.assertEqual(experiment_query.order, order)
        self.assertEqual(experiment_query.value_type, value_type)
        self.assertEqual(experiment_query.value_range, value_range)
        self.assertEqual(experiment_query.value_candidates,
                         value_candidates)
        return experiment_query

    def test_create_observation(self, experiment_id=rand_experiment_id()):
        student_name = randlength_word()
        datum = randlength_word()
        observation_id = u.generate_observation_id(experiment_id, student_name)
        while ds.query(m.Observation).filter(m.Observation.id == observation_id).count() != 0:
            student_name = randlength_word()
            experiment_id = rand_experiment_id()
            observation_id = u.generate_observation_id(experiment_id,
                                                       student_name)
        observation = m.Observation(id=observation_id,
                                    student_name=student_name,
                                    datum=datum)

        ds.add(observation)
        ds.commit()
        observation_query = ds.query(m.Observation).filter(m.Observation.id == observation_id).first()
        self.assertEqual(observation_query.id, observation_id)
        self.assertEqual(observation_query.student_name, student_name)
        self.assertEqual(observation_query.datum, datum)
        return observation_query

    def test_create_user(self):
        username = randlength_word()
        while ds.query(m.User).filter(m.User.id == username).count() != 0:
            username = randlength_word()
        name = randlength_word()
        user = m.User(id=username,
                      name=name)
        ds.add(user)
        ds.commit()
        user_query = ds.query(m.User).filter(m.User.id == username).first()
        self.assertEqual(user_query.id, username)
        self.assertEqual(user_query.name, name)
        return user_query

    def test_create_role(self):
        name = randlength_word()
        while ds.query(m.Role).filter(m.Role.name == name).count() != 0:
            name = randlength_word()
        powers = rand_powers()
        role = m.Role(name=name, powers=powers)
        ds.add(role)
        ds.commit()
        role_query = u.get_role(name)
        self.assertEqual(role_query.name, name)
        self.assertEqual(role_query.powers, powers)
        return role_query

    def test_create_power(self):
        id = randlength_word()
        while ds.query(m.Power).filter(m.Power.id == id).count() != 0:
            id = randlength_word()
        power = m.Power(id=id)
        ds.add(power)
        ds.commit()
        power_query = u.get_power(id)
        self.assertEqual(power_query.id, id)
        return power_query

    # --- Testing functions(have interaction with database) for functions in utility.py ---

    # Testing for the existence of an object
    # This group of functions create a new object in the database with random
    # and then test the existence of the object by calling the existence
    # checking function. It also checks the non-existence of a object that
    # should not be in the database by calling the function to make sure that
    # the existen checking function will not always return True.
    def test_lab_exists(self):
        lab = self.test_create_lab()
        self.assertTrue(u.lab_exists(lab.id))
        self.assertFalse(u.lab_exists(lab.id+'123'))

    def test_experiment_exists(self):
        experiment = self.test_create_experiment()
        self.assertTrue(u.experiment_exists(experiment.id))
        self.assertFalse(u.experiment_exists(experiment.id+'123'))

    def test_observation_exists(self):
        observation = self.test_create_observation()
        self.assertTrue(u.observation_exists(observation.id))
        self.assertFalse(u.observation_exists(observation.id+'123'))

    def test_class_exists(self):
        the_class = self.test_create_class()
        self.assertTrue(u.class_exists(the_class.id))
        self.assertFalse(u.class_exists(the_class.id+'123'))

    def test_user_exists(self):
        user = self.test_create_user()
        self.assertTrue(u.user_exists(user.id))
        self.assertFalse(u.user_exists(user.id+'123'))

    # Testing for querying a single object from the database
    # This group of testing functions query objects from the database by
    # calling the corresponging utility function and comepare it with
    # the object we created and added
    def test_get_lab(self):
        lab = self.test_create_lab()
        lab_query = u.get_lab(lab.id)
        self.assertEqual(lab_query, lab)

    def test_get_experiment(self):
        experiment = self.test_create_experiment()
        experiment_query = get_experiment(experiment.id)
        self.assertEqual(experiment_query, experiment)

    def test_get_observation(self):
        observation = self.test_create_observation()
        observation_query = u.get_observation(observation.id)
        self.assertEqual(observation_query, observation)

    def test_get_power(self):
        power = self.test_create_power()
        power_query = u.get_power(power.id)
        self.assertEqual(power_query, power)

    def test_get_role(self):
        role = self.test_create_role()
        role_query = u.get_role(role.name)
        self.assertEqual(role_query, role)

    def test_get_user(self):
        user = self.test_create_user()
        user_query = u.get_user(user.id)
        self.assertEqual(user_query, user)

    def test_get_class(self):
        the_class = self.test_create_class()
        class_query = u.get_class(the_class.id)
        self.assertEqual(class_query, the_class)

    # - Testing for query all objects of a class from the database -
    # This group of testing functions create a bunch of random objects
    # of the same class and store them into the database. Then, calling
    # the corresponding get_all function and check whether all the objects
    # will be returned
    def test_get_all_lab(self):
        lab_ids = [self.test_create_lab().id for _ in range(rand_round())]
        for lab_id in lab_ids:
            self.assertIn(u.get_lab(lab_id), u.get_all_lab())

    def test_get_all_experiment(self):
        experiment_ids = [self.test_create_experiment().id for _ in range(rand_round())]
        for experiment_id in experiment_ids:
            self.assertIn(get_experiment(experiment_id),
                          u.get_all_experiment())

    def test_get_all_class(self):
        class_ids = [self.test_create_class().id for _ in range(rand_round())]
        for class_id in class_ids:
            self.assertIn(u.get_class(class_id), u.get_all_class())

    def test_get_all_admin(self):
        admin_ids = []
        for _ in range(rand_round()):
            user = self.test_create_user()
            user.role_name = rand_role()
            if user.role_name == 'Admin':
                admin_ids.append(user.id)
        for admin_id in admin_ids:
            self.assertIn(u.get_user(admin_id), u.get_all_admin())

    def test_get_all_superadmin(self):
        superadmin_ids = []
        for _ in range(rand_round()):
            user = self.test_create_user()
            user.role_name = rand_role()
            if user.role_name == 'SuperAdmin':
                superadmin_ids.append(user.id)
        for superadmin_id in superadmin_ids:
            self.assertIn(u.get_user(superadmin_id), u.get_all_superadmin())

    # - Testing for query objects of one class for an object of another class -
    def test_get_available_labs_for_user(self):
        count = 0
        user = self.test_create_user()
        user.role_name == rand_role()
        self.assertEqual(len(u.get_available_labs_for_user(user)), count)
        for i in range(rand_round()):
            lab = self.test_create_lab()
            # The lab may not be the user's own lab
            # If user is not a super admin, other admins' labs
            # should not be queried
            if randint(0, 1) == 1:
                user.labs.append(lab)
                count += 1
            elif user.role_name == 'SuperAdmin':
                count += 1
            self.assertEqual(len(u.get_available_labs_for_user(user)), count)

    def test_get_experiments_for_lab(self):
        experiment_ids = []
        lab = self.test_create_lab()
        self.assertEqual(len(u.get_experiments_for_lab(lab.id)), 0)
        for i in range(rand_round()):
            experiment = self.test_create_experiment()
            experiment_ids.append(experiment.id)
            lab.experiments.append(experiment)
        for experiment_id in experiment_ids:
            self.assertIn(get_experiment(experiment_id),
                          u.get_experiments_for_lab(lab.id))

    def test_get_observations_for_experiment(self):
        observation_ids = []
        experiment = self.test_create_experiment()
        self.assertEqual(len(u.get_observations_for_experiment(experiment.id)), 0)
        for i in range(rand_round()):
            observation = self.test_create_observation()
            observation_ids.append(observation.id)
            experiment.observations.append(observation)
        for observation_id in observation_ids:
            self.assertIn(u.get_observation(observation_id),
                          u.get_observations_for_experiment(experiment.id))

    def test_observation_number_for_experiment(self):
        count = 0
        experiment = self.test_create_experiment()
        self.assertEqual(u.observation_number_for_experiment(experiment.id),
                         count)
        for i in range(rand_round()):
            observation = self.test_create_observation()
            experiment.observations.append(observation)
            count += 1
            self.assertEqual(u.observation_number_for_experiment(experiment.id),
                             count)

    # - serialize a list of an object of one class -
    # Get all objects of one class and then serialize them into
    # a list of python dictionary
    def test_serialize_lab_list(self):
        for i in range(rand_round()):
            self.test_create_lab()
        lab_list_serialized = u.serialize_lab_list(u.get_all_lab())
        for lab in lab_list_serialized:
            lab_query = u.get_lab(lab['lab_id'])
            self.assertEqual(lab_query.name, lab['lab_name'])
            self.assertEqual(lab_query.description, lab['description'])
            self.assertEqual(lab_query.status, lab['status'])
            self.assertEqual(len(lab_query.experiments), lab['experiments'])

    def test_serialize_experiment_list(self):
        for i in range(rand_round()):
            self.test_create_experiment()
        experiment_list_serialized = u.serialize_experiment_list(u.get_all_experiment())
        for exp in experiment_list_serialized:
            experiment_query = get_experiment(exp['experiment_id'])
            self.assertEqual(experiment_query.name, exp['experiment_name'])
            self.assertEqual(experiment_query.description, exp['description'])
            self.assertEqual(experiment_query.order, exp['order'])
            self.assertEqual(experiment_query.value_type, exp['value_type'])
            self.assertEqual(experiment_query.value_range, exp['value_range'])
            self.assertEqual(experiment_query.value_candidates,
                             exp['value_candidates'])

    def test_serialize_user_list(self):
        for i in range(rand_round()):
            user = self.test_create_user()
            user.role_name = rand_role()
        user_list_serialized = u.serialize_user_list(u.get_all_user())
        for user in user_list_serialized:
            user_query = u.get_user(user['username'])
            self.assertEqual(user_query.id, user['username'])
            self.assertEqual(user_query.name, user['name'])

    def test_serialize_class_list(self):
        for i in range(rand_round()):
            self.test_create_class()
        class_list_serialized = u.serialize_class_list(u.get_all_class())
        for c in class_list_serialized:
            class_query = u.get_class(c['id'])
            self.assertEqual(class_query.id, c['id'])
            self.assertEqual(class_query.name, c['name'])
            self.assertEqual(class_query.time, c['time'])

    # - This group returns a list of a certain attribute of all the objects in
    # this class -
    def test_get_class_id_list(self):
        user = self.test_create_user()
        random_admin_role = u.get_role(rand_admin())
        user.role = random_admin_role
        class_id_list = []
        for i in range(rand_round()):
            the_class = self.test_create_class()
            class_id_list.append(the_class.id)
        class_id_list_retrieved = u.get_class_id_list(user)
        if user.role_name == 'SuperAdmin':
            for class_id in class_id_list:
                self.assertIn(class_id, class_id_list_retrieved)

    def test_get_all_user(self):
        usernames = []
        for i in range(rand_round()):
            user = self.test_create_user()
            user.role_name = rand_role()
            usernames.append(user.id)
        usernames_retrieved = [u.id for u in u.get_all_user()]
        for username in usernames:
            self.assertIn(username, usernames_retrieved)

    # --- Testing functions for functions that return the info of objects
    # in the format different from an object directly queried from the database
    def test_find_lab_list_for_user(self):
        count = 0
        user = self.test_create_user()
        random_admin_role = u.get_role(rand_admin())
        user.role = random_admin_role
        self.assertEqual(len(u.find_lab_list_for_user(user)), count)
        for i in range(rand_round()):
            lab = self.test_create_lab()
            # The lab may not be the user's own lab
            # If user is not SuperAdmin, other's labs
            # should not be queried
            if randint(0, 1) == 1:
                user.labs.append(lab)
                count += 1
            elif user.role_name == 'SuperAdmin':
                count += 1
        self.assertEqual(len(u.find_lab_list_for_user(user)), count)

    def test_find_all_labs(self):
        user = self.test_create_user()
        user.role == u.get_role(rand_admin())
        for i in range(rand_round()):
            user.labs.append(self.test_create_lab())
        labs = u.find_all_labs(user)
        for lab in labs['activated']:
            self.assertEqual(lab['status'], 'Activated')
        for lab in labs['unactivated']:
            self.assertEqual(lab['status'], 'Unactivated')
        for lab in labs['downloadable']:
            self.assertEqual(lab['status'], 'Downloadable')

    # - Testing functions for functions that add/delete/modify an object or
    # related functions with the input in a certain format -
    def test_delete_lab(self):
        lab = self.test_create_lab()
        lab_id = lab.id
        u.delete_lab(lab_id)
        self.assertFalse(u.lab_exists(lab_id))

    def test_modify_lab(self):
        built_in_ids = populate_db()
        the_class = u.get_class(built_in_ids['class_id'])
        lab_json = self.construct_lab_json()
        lab_json['classId'] = u.generate_class_id(the_class.name, the_class.time)
        lab_name = randlength_word()
        lab_json['labName'] = lab_name
        lab_id = u.generate_lab_id(lab_name, the_class.id)
        err_msg = u.modify_lab(lab_json)
        self.assertEqual('', err_msg)
        self.assertTrue(u.lab_exists(lab_id))

    def test_find_lab_copy_id(self):
        lab = self.test_create_lab()
        new_lab_id = u.find_lab_copy_id(lab.id)
        self.assertEqual(new_lab_id, 'copy1-'+lab.id)

    def test_duplicate_lab(self):
        built_in_ids = populate_db()
        lab_id = built_in_ids['lab_id']
        u.duplicate_lab(lab_id)
        self.assertTrue(u.lab_exists('copy1-'+lab_id))

    def test_change_lab_status(self):
        lab = self.test_create_lab()
        new_status = rand_lab_status()
        u.change_lab_status(lab.id, new_status)
        self.assertEqual(lab.status, new_status)

    # This doesn't check all the variables passed into lab_info
    def test_pack_labinfo_sent_from_client(self):
        clinet_form = {'labName': randlength_word(),
                       'classId': rand_classid(),
                       'professorName': randlength_word(),
                       'labDescription': randlength_word(),
                       'labQuestions': randint(1, 100)
                       }
        lab_info, err_msg = u.pack_labinfo_sent_from_client(clinet_form)
        self.assertEqual(len(lab_info['experiments']), clinet_form['labQuestions'], err_msg)

    # This test is far from covering all the possibilities
    def test_find_all_observations_for_labs(self):
        student_num = randint(1, 5)
        experiment_num = randint(1, 5)
        lab = self.construct_lab_observations(student_num, experiment_num)
        observations_group_by_experiment_name, observations_group_by_student, _, _, _ = u.find_all_observations_for_labs([lab.id])
        self.assertEqual(len(observations_group_by_experiment_name), experiment_num)
        self.assertEqual(len(observations_group_by_student), student_num)

    def test_change_observation_organization(self):
        student_num = 5
        experiment_num = 5
        lab = self.construct_lab_observations(student_num, experiment_num)
        observations_group_by_experiment_name, _, _, _, _ = u.find_all_observations_for_labs([lab.id])
        observations_group_by_student = u.change_observation_organization(observations_group_by_experiment_name)
        self.assertEqual(len(observations_group_by_student), student_num)

    def test_delete_observation(self):
        observation_ids = []
        for i in range(rand_round()):
            observation = self.test_create_observation()
            observation_ids.append(observation.id)
        u.delete_observation(observation_ids)
        for observation_id in observation_ids:
            self.assertFalse(u.check_existence(observation_id))

    def test_add_observation(self):
        experiment = self.test_create_experiment()
        observation_list = []
        for i in range(rand_round()):
            student_name = randlength_word()
            observation_datum = randlength_word()
            experiment_id = experiment.id
            observation_id = u.generate_observation_id(experiment_id, student_name)
            observation_list.append({'studentName': student_name,
                                     'observationData': observation_datum,
                                     'experimentId': experiment_id,
                                     'observationId': observation_id
                                     })
        u.add_observation(observation_list)
        observation_num = u.observation_number_for_experiment(experiment.id)
        self.assertEqual(observation_num, len(observation_list))

    def test_add_observations_sent_by_students(self):
        student_num = 5
        experiment_num = 5
        lab = self.construct_lab_observations(student_num, experiment_num)
        observations_group_by_experiment_name, observations_group_by_student, _, _, _ = u.find_all_observations_for_labs([lab.id])
        err_msg = u.add_observations_sent_by_students(observations_group_by_student)
        self.assertEqual(student_num * experiment_num,
                         ds.query(m.Observation).count(), err_msg)

    def test_add_user(self):
        username = randlength_word()
        user_info = MultiDict([('username', username),
                               ('role', rand_role()),
                               ('name', randlength_word())])
        u.add_user(user_info)
        user_query = u.get_user(username)
        self.assertEqual(user_query.id, user_info['username'])
        self.assertEqual(user_query.name, user_info['name'])

    def test_delete_user(self):
        admin_role = u.get_role(rand_admin())
        admin = self.test_create_user()
        admin_id = admin.id
        admin.role = admin_role
        u.delete_user(admin_id)
        self.assertFalse(u.user_exists(admin_id))

    def test_change_user_info(self):
        username = self.test_create_user().id
        role_name = rand_role()
        class_ids = [self.test_create_class().id]
        u.change_user_info(username, role_name, class_ids)
        the_user = u.get_user(username)
        class_id_list = [c.id for c in the_user.classes]
        self.assertEqual(username, the_user.id)
        for c in class_ids:
            self.assertIn(c, class_id_list)

    def test_add_class(self):
        built_in_ids = populate_db()
        professor_id = built_in_ids['admin_id']
        student_id = built_in_ids['student_id']
        class_info = MultiDict([('professors', professor_id),
                                ('students', student_id),
                                ('className', randlength_word()),
                                ('classTime', rand_classtime())])
        for i in range(rand_round()):
            class_info['students'] += (randlength_word()+',')
        class_info['students'] = class_info['students'].rstrip(',')
        err_msg = u.add_class(class_info)
        if err_msg == '':
            class_id = u.generate_class_id(class_info['className'],
                                           class_info['classTime'])
            the_class = u.get_class(class_id)
            self.assertEqual(the_class.id, class_id, err_msg)

    def test_delete_class(self):
        the_class = self.test_create_class()
        class_id = the_class.id
        u.delete_class(class_id)
        self.assertFalse(u.class_exists(class_id))

    def test_change_class_users(self):
        built_in_ids = populate_db()
        the_class = u.get_class(built_in_ids['class_id'])
        new_user_ids = [built_in_ids['student_id'],
                        built_in_ids['admin_id']]
        u.change_class_users(the_class.id, new_user_ids)
        class_user_ids = [user.id for user in the_class.users]
        for user_id in new_user_ids:
            self.assertIn(user_id, class_user_ids)

    # --- Test Interaction with Iris ---
    # Convert a term code into a semester name
    # e.g. 201701 -> FALL2017
    def test_tranlate_term_code_to_semester(self):
        term_code = '201701'
        term_code2 = '203103'
        semester = 'FALL2016'
        semester2 = 'SPRING2031'
        self.assertEqual(u.tranlate_term_code_to_semester(term_code), semester)
        self.assertEqual(u.tranlate_term_code_to_semester(term_code2), semester2)

    def test_cleanup_class_data(self):
        # A snippet from real data
        class_data = [{'course_id': '11069', 'term_code': '201701', 'subject': 'BIOL', 'course_number': '331', 'section': 'F', 'section_type': 'Lecture', 'instructors': ['prof1']},
                      {'course_id': '10236', 'term_code': '201701', 'subject': 'BIOL', 'course_number': '101', 'section': 'F22', 'section_type': 'Lab', 'instructors': ['prof2']},
                      {'course_id': '10447', 'term_code': '201701', 'subject': 'BIOL', 'course_number': '101', 'section': 'F01', 'section_type': 'Lab Lecture', 'instructors': ['prof3', 'prof4', 'prof5']},
                      {'course_id': '10010', 'term_code': '201701', 'subject': 'BIOL', 'course_number': '470', 'section': 'YJS', 'section_type': 'Ind. study', 'instructors': ['prof6']}
                      ]
        cleaned_class_data = u.cleanup_class_data(class_data)
        course_numbers = [c['course_number'] for c in cleaned_class_data]
        # 470 should have been removed
        self.assertNotIn('470', course_numbers)

    def test_populate_db_with_classes_and_professors(self):
        # A snippet from real data
        class_data = [{'course_id': '11069', 'term_code': '201701', 'subject': 'BIOL', 'course_number': '331', 'section': 'F', 'section_type': 'Lecture', 'instructors': ['prof1']},
                      {'course_id': '10236', 'term_code': '201701', 'subject': 'BIOL', 'course_number': '101', 'section': 'F22', 'section_type': 'Lab', 'instructors': ['prof2']},
                      {'course_id': '10447', 'term_code': '201701', 'subject': 'BIOL', 'course_number': '101', 'section': 'F01', 'section_type': 'Lab Lecture', 'instructors': ['prof3', 'prof4', 'prof5']},
                      {'course_id': '10010', 'term_code': '201701', 'subject': 'BIOL', 'course_number': '470', 'section': 'YJS', 'section_type': 'Ind. study', 'instructors': ['prof6']}
                      ]
        u.populate_db_with_classes_and_professors(class_data)
        # Pick a random professor and a random class to test their existence
        random_index = randint(0, len(class_data)-1)
        professor_id = class_data[random_index]['instructors'][0]
        self.assertTrue(u.user_exists(professor_id))
        class_name = class_data[random_index]['subject'] + class_data[random_index]['course_number']
        class_time = u.tranlate_term_code_to_semester(class_data[random_index]['term_code'])
        class_id = u.generate_class_id(class_name, class_time)
        self.assertTrue(u.class_exists(class_id))

    def test_update_users_by_data_from_iris(self):
        registration_data = [{"user_name": "fake1", "course_id": "10508", "term_code": "201701", "subject": "BIOL", "course_number": "356", "section": "FL1"},
                             {"user_name": "fake2", "course_id": "11055", "term_code": "201701", "subject": "BIOL", "course_number": "351", "section": "FL1"},
                             {"user_name": "fake3", "course_id": "11055", "term_code": "201701", "subject": "BIOL", "course_number": "351", "section": "FL1"},
                             {"user_name": "fake4", "course_id": "10369", "term_code": "201701", "subject": "BIOL", "course_number": "342", "section": "FL1"}
                             ]
        u.update_users_by_data_from_iris(registration_data)
        # Pick a random student to test their existence
        random_index = randint(0, len(registration_data)-1)
        professor_id = registration_data[random_index]['user_name']
        self.assertTrue(u.user_exists(professor_id))

    # --- Test all relatinships in models.py ---
    # One function only tests one relationship at a time
    def test_relationship_lab_experiments(self):
        lab = self.test_create_lab()
        for i in range(rand_round()):
            lab.experiments.append(self.test_create_experiment(lab.id))
        for experiment in lab.experiments:
            experiment_query = u.get_experiment(experiment.id)
            self.assertEqual(experiment_query.lab_id,  lab.id)

    def test_relationship_lab_classes(self):
        lab = self.test_create_lab()
        class_list = []
        for i in range(rand_round()):
            the_class = self.test_create_class()
            the_class.lab = lab
            class_list.append(the_class)
        for c in class_list:
            the_class = u.get_class(c.id)
            self.assertEqual(the_class.lab.id, lab.id)

    def test_relationship_lab_users(self):
        lab = self.test_create_lab()
        for i in range(rand_round()):
            lab.users.append(self.test_create_user())
        for user in lab.users:
            user_query = u.get_user(user.id)
            self.assertEqual(user_query.labs[0].id, lab.id)

    def test_relationship_experiment_observations(self):
        experiment = self.test_create_experiment()
        for i in range(rand_round()):
            experiment.observations.append(self.test_create_observation(experiment.id))
        for observation in experiment.observations:
            observation_query = u.get_observation(observation.id)
            self.assertEqual(observation_query.experiment_id, experiment.id)

    def test_relationship_classes_users(self):
        the_class = self.test_create_class()
        for i in range(rand_round()):
            the_class.users.append(self.test_create_user())
        for user in the_class.users:
            user_query = u.get_user(user.id)
            self.assertEqual(user_query.the_class.id, the_class.id)

    def test_relationship_users_role(self):
        role = self.test_create_role()
        for i in range(rand_round()):
            role.users.append(self.test_create_user())
        for user in role.users:
            user_query = u.get_user(user.id)
            self.assertEqual(user_query.role_name, role.name)

    # --- Test view functions in views.py by sending http request ---
    # This only covers superadmin case
    def test_login_logout(self):
        built_in_ids = populate_db()
        superadmin = u.get_user(built_in_ids['superadmin_id'])
        rv = self.login(superadmin.id)
        soup = self.decode(rv)
        self.assertIn(superadmin.id,
                      soup.find('p', {'id': 'welcomeMsg'}).text)
        rv = self.logout()
        soup = self.decode(rv)
        self.assertEqual('Login', soup.title.text)

    def test_student_home(self):
        built_in_ids = populate_db()
        student = u.get_user(built_in_ids['student_id'])
        self.login(student.id)
        # student has power to access student_home
        rv = self.app.get('/student_home')
        soup = self.decode(rv)
        self.assertIn(student.id,
                      soup.find('p', {'id': 'welcomeMsg'}).text)

        # student has power to access student_home
        rv = self.app.get('/admin_home')
        soup = self.decode(rv)
        self.assertEqual(None, soup.find('p', {'id': 'welcomeMsg'}))

        # student doesn't have power to access superstudent_home
        rv = self.app.get('/superadmin_home')
        soup = self.decode(rv)
        self.assertEqual(None, soup.find('p', {'id': 'welcomeMsg'}))

    def test_admin_home(self):
        built_in_ids = populate_db()
        admin = u.get_user(built_in_ids['admin_id'])
        self.login(admin.id)
        # admin has power to access admin_home
        rv = self.app.get('/admin_home')
        soup = self.decode(rv)
        self.assertIn(admin.id,
                      soup.find('p', {'id': 'welcomeMsg'}).text)

        # admin doesn't have power to access superadmin_home
        rv = self.app.get('/superadmin_home')
        soup = self.decode(rv)
        self.assertEqual(None, soup.find('p', {'id': 'welcomeMsg'}))

    def test_superadmin_home(self):
        built_in_ids = populate_db()
        superadmin = u.get_user(built_in_ids['superadmin_id'])
        self.login(superadmin.id)
        # superadmin has power to access superadmin_home
        rv = self.app.get('/superadmin_home')
        soup = self.decode(rv)
        self.assertIn(superadmin.id,
                      soup.find('p', {'id': 'welcomeMsg'}).text)

    def test_student_select_lab(self):
        built_in_ids = populate_db()
        student = u.get_user(built_in_ids['student_id'])
        self.login(student.id)

        # The lab should not be visible since it's not
        # in the student's lab list
        lab = u.get_lab(built_in_ids['lab_id'])
        rv = self.app.get('/student_select_lab')
        soup = self.decode(rv)
        self.assertEqual(None, soup.find('p', {'id': 'welcomeMsg'}))

        # Start a new session
        # The lab should be visible after it is
        # added into the lab list of the student
        student = u.get_user(student.id)
        lab = u.get_lab(built_in_ids['lab_id'])
        student.labs.append(lab)
        ds.commit()

        rv = self.app.get('/student_select_lab')
        soup = self.decode(rv)
        self.assertIn(lab.name, soup.tbody.text)

    def test_student_data_entry(self):
        built_in_ids = populate_db()
        student = u.get_user(built_in_ids['student_id'])
        lab = u.get_lab(built_in_ids['lab_id'])
        experiment = u.get_experiment(built_in_ids['experiment_id'])
        # The page will be redirected to the log in page if the user
        # does not have the power to enter data for the current lab

        self.login(student.id)
        rv = self.app.get('/student_data_entry/'+lab.id, follow_redirects=True)
        soup = self.decode(rv)
        self.assertIn(experiment.name, soup.tbody.text)

    def test__student_receive_data(self):
        built_in_ids = populate_db()
        student = u.u.get_user(built_in_ids['student2_id'])
        lab = u.get_lab(built_in_ids['lab_id'])
        experiment = u.get_experiment(built_in_ids['experiment_id'])
        student_id = student.id
        student.role = u.get_role('Student')
        observation_datum = randlength_word()
        self.login(student.id)

        # Start a new session
        student = u.get_user(student_id)
        student.labs.append(lab)
        ds.commit()

        observationsForOneExperiment = [{'labId': lab.id,
                                         'experimentName': experiment.name,
                                         'observation': observation_datum}]
        observationsGroupByStudent = [{'studentName': student.name,
                                      'observationsForOneExperiment': observationsForOneExperiment}]
        data_to_be_sent = dict(observationsGroupByStudent=observationsGroupByStudent)
        self.app.post('/_student_receive_data',
                      data=json.dumps(data_to_be_sent),
                      content_type='application/json',
                      follow_redirects=True)

        # Start a new session
        student = u.get_user(student_id)
        observation_id = u.generate_observation_id(experiment.id,
                                                   student.id)
        observation_query = u.get_observation(observation_id)
        self.assertEqual(observation_query.datum, observation_datum)

    def test_admin_create_and_manage_lab(self):
        built_in_ids = populate_db()
        superadmin = u.get_user(built_in_ids['superadmin_id'])
        the_class = u.get_class(built_in_ids['class_id'])
        self.login(superadmin.id)
        # GET
        lab = u.get_lab(built_in_ids['lab_id'])
        rv = self.app.get('/admin_create_and_manage_lab')
        soup = self.decode(rv)
        self.assertIn(lab.name, soup.text)
        # POST
        lab_form = {'labName': randlength_word(),
                    'classId': the_class.id,
                    'className': the_class.name,
                    'professorName': superadmin.id,
                    'labDescription': randlength_word(),
                    'labQuestions:': randint(1, 100)}
        headers = {'Content-type': 'application/x-www-form-urlencoded',
                   'Accept': 'text/plain'}
        rv = self.app.post('/admin_create_and_manage_lab',
                           data=lab_form,
                           headers=headers)
        self.assertEqual(rv.status_code, 200)

    def test_admin_setup_labs(self):
        built_in_ids = populate_db()
        superadmin = u.get_user(built_in_ids['superadmin_id'])
        self.login(superadmin.id)
        clinet_form = {'labName': randlength_word(),
                       'className': randlength_word(),
                       'classTime': rand_classtime(),
                       'professorName': randlength_word(),
                       'labDescription': randlength_word(),
                       'labQuestions': randint(1, 100)
                       }
        lab_info, err_msg = u.pack_labinfo_sent_from_client(clinet_form)
        rv = self.app.get('/admin_create_and_manage_lab?lab_info='+json.dumps(dict(labinfo=lab_info)),
                          follow_redirects=True)
        soup = self.decode(rv)
        self.assertIn('admin_create_and_manage_lab', soup.text)

    def test__admin_receive_setup_labs_data(self):
        built_in_ids = populate_db()
        superadmin = u.get_user(built_in_ids['superadmin_id'])
        self.login(superadmin.id)
        lab_json = self.construct_lab_json()
        the_class = u.get_class(built_in_ids['class_id'])
        lab_json['classId'] = u.generate_class_id(the_class.name, the_class.time)
        lab_name = randlength_word()
        lab_json['labName'] = lab_name
        lab_id = u.generate_lab_id(lab_name, the_class.id)

        # Add the corresponding class first since without class
        # the lab will not be able to be added
        self.app.post('/_admin_receive_setup_labs_data',
                      data=json.dumps(lab_json),
                      content_type='application/json')
        self.assertTrue(u.lab_exists(lab_id))

    def test_admin_modify_lab(self):
        built_in_ids = populate_db()
        superadmin = u.get_user(built_in_ids['superadmin_id'])
        self.login(superadmin.id)
        rv = self.app.get('/admin_modify_lab/'+built_in_ids['lab_id'])
        self.assertTrue(rv.status_code, 200)

    # This only tests one possibility: when the user change the description
    # of the lab. We need more tests!
    def test__admin_modify_lab(self):
        # Add a new lab
        built_in_ids = populate_db()
        superadmin = u.get_user(built_in_ids['superadmin_id'])
        self.login(superadmin.id)
        lab_json = self.construct_lab_json()

        the_class = u.get_class(built_in_ids['class_id'])
        lab_json['classId'] = u.generate_class_id(the_class.name, the_class.time)
        lab_name = randlength_word()
        lab_json['labName'] = lab_name
        lab_id = u.generate_lab_id(lab_name, the_class.id)

        self.app.post('/_admin_receive_setup_labs_data',
                      data=json.dumps(lab_json),
                      content_type='application/json')

        # Modify the lab's description we just set up
        lab_json['labDescription'] = randlength_word()
        lab_json['oldLabId'] = lab_id
        self.app.post('/_admin_modify_lab',
                      data=json.dumps(lab_json),
                      content_type='application/json')
        lab_query = u.get_lab(lab_id)
        self.assertEqual(lab_json['labDescription'], lab_query.description)

    def test__admin_duplicate_lab(self):
        built_in_ids = populate_db()
        superadmin = u.get_user(built_in_ids['superadmin_id'])
        self.login(superadmin.id)
        lab_id = built_in_ids['lab_id']
        self.app.post('/_admin_duplicate_lab',
                      data=json.dumps({'labId': lab_id}),
                      content_type='application/json')
        self.assertTrue(u.lab_exists('copy1-'+lab_id))

    def test__admin_delete_lab(self):
        built_in_ids = populate_db()
        superadmin = u.get_user(built_in_ids['superadmin_id'])
        self.login(superadmin.id)
        lab_id = built_in_ids['lab_id']
        self.app.post('/_admin_delete_lab',
                      data=json.dumps({'labId': lab_id}),
                      content_type='application/json')
        self.assertFalse(u.lab_exists(lab_id))

    def test__admin_change_lab_status(self):
        built_in_ids = populate_db()
        superadmin = u.get_user(built_in_ids['superadmin_id'])
        self.login(superadmin.id)
        lab_id = built_in_ids['lab_id']
        new_status = rand_lab_status()
        self.app.post('/_admin_change_lab_status/'+new_status,
                      data=json.dumps({'labId': lab_id}),
                      content_type='application/json')
        self.assertEqual(u.get_lab(lab_id).status, new_status)

    def test_admin_select_lab_for_data(self):
        built_in_ids = populate_db()
        lab_id = built_in_ids['lab_id']
        superadmin = u.get_user(built_in_ids['superadmin_id'])
        self.login(superadmin.id)
        rv = self.app.get('/admin_select_lab_for_data')
        soup = self.decode(rv)
        self.assertIn(u.get_lab(lab_id).name, soup.tbody.text)

    def test_admin_edit_data(self):
        built_in_ids = populate_db()
        lab_id = built_in_ids['lab_id']
        experiment_name = get_experiment(built_in_ids['experiment_id']).name
        superadmin = u.get_user(built_in_ids['superadmin_id'])
        self.login(superadmin.id)
        lab_ids = [lab_id]
        rv = self.app.get('/admin_edit_data/'+json.dumps(lab_ids))
        soup = self.decode(rv)
        self.assertIn(experiment_name, soup.thead.text)

    def test__admin_change_data(self):
        built_in_ids = populate_db()
        superadmin = u.get_user(built_in_ids['superadmin_id'])
        observation = u.get_observation(built_in_ids['observation_id'])
        self.login(superadmin.id)
        new_observation_datum = 'C'
        observation_modified = {'studentName': observation.student_name,
                                'observationData': new_observation_datum,
                                'experimentId': observation.experiment_id,
                                'observationId': observation.id}
        data_change_info = {'oldObservationIdsList': [observation.id],
                            'newObservationList': [observation_modified]}

        self.app.post('/_admin_change_data',
                      data=json.dumps(data_change_info),
                      content_type='application/json')
        self.assertEqual(u.get_observation(observation_modified['observationId']).datum,
                         new_observation_datum)

    def test__admin_delete_data(self):
        built_in_ids = populate_db()
        observation_id = built_in_ids['observation_id']
        superadmin = u.get_user(built_in_ids['superadmin_id'])
        self.login(superadmin.id)
        self.app.post('/_admin_delete_data',
                      data=json.dumps({'observationIdsToBeRemoved': [observation_id]}),
                      content_type='application/json')
        self.assertFalse(u.observation_exists(observation_id))

    def test_admin_download_data(self):
        built_in_ids = populate_db()
        lab_id = built_in_ids['lab_id']
        observation_datum = u.get_observation(built_in_ids['observation_id']).datum
        superadmin = u.get_user(built_in_ids['superadmin_id'])
        self.login(superadmin.id)
        rv = self.app.get('/_admin_download_data/'+json.dumps([lab_id]))
        # Decode the return value and check the downloadeded text
        text = rv.data.decode('utf-8')
        self.assertIn(observation_datum, text)

    def test_superadmin_create_and_manage_user(self):
        built_in_ids = populate_db()
        superadmin = u.get_user(built_in_ids['superadmin_id'])
        admin_id = u.get_user(built_in_ids['admin_id']).id
        self.login(superadmin.id)
        # GET
        rv = self.app.get('/superadmin_create_and_manage_user')
        soup = self.decode(rv)
        self.assertIn(admin_id, soup.tbody.text)
        # POST
        user_form = {'username': randlength_word(),
                     'name': randlength_word(),
                     'role': rand_role(),
                     'classIds': []
                     }
        headers = {'Content-type': 'application/x-www-form-urlencoded',
                   'Accept': 'text/plain'}
        rv = self.app.post('/superadmin_create_and_manage_user',
                           data=user_form,
                           headers=headers)
        self.assertEqual(u.get_user(user_form['username']).id,
                         user_form['username'])

    def test__superadmin_delete_user(self):
        built_in_ids = populate_db()
        superadmin = u.get_user(built_in_ids['superadmin_id'])
        admin_id = built_in_ids['admin_id']
        self.login(superadmin.id)
        self.app.post('/_superadmin_delete_user',
                      data=json.dumps({'userIdToBeRemoved': admin_id}),
                      content_type='application/json')
        self.assertFalse(u.user_exists(admin_id))

    def test_superadmin_create_and_manage_class(self):
        built_in_ids = populate_db()
        superadmin = u.get_user(built_in_ids['superadmin_id'])
        self.login(superadmin.id)
        class_name = u.get_class(built_in_ids['class_id']).name
        admin_id = u.get_user(built_in_ids['admin_id']).id
        student_id = u.get_user(built_in_ids['student2_id']).id
        # GET
        rv = self.app.get('/superadmin_create_and_manage_class')
        soup = self.decode(rv)
        self.assertIn(class_name, soup.tbody.text)
        # POST
        class_form = {'professors': [admin_id],
                      'students': [student_id],
                      'className': randlength_word(),
                      'classTime': rand_classtime()}
        headers = {'Content-type': 'application/x-www-form-urlencoded',
                   'Accept': 'text/plain'}
        rv = self.app.post('/superadmin_create_and_manage_class',
                           data=class_form,
                           headers=headers)
        new_class_id = u.generate_class_id(class_form['className'],
                                           class_form['classTime'])
        self.assertEqual(u.get_class(new_class_id).name,
                         class_form['className'])

    def test__superadmin_delete_class(self):
        built_in_ids = populate_db()
        superadmin = u.get_user(built_in_ids['superadmin_id'])
        class_id = built_in_ids['class_id']
        self.login(superadmin.id)
        self.app.post('/_superadmin_delete_class',
                      data=json.dumps({'classIdToBeRemoved': class_id}),
                      content_type='application/json')
        self.assertFalse(u.class_exists(class_id))

    def test__superadmin_modify_class(self):
        built_in_ids = populate_db()
        superadmin = u.get_user(built_in_ids['superadmin_id'])
        class_id = built_in_ids['class_id']
        professor_usernames = []
        new_student_names = []
        self.login(superadmin.id)
        rv = self.app.post('/_superadmin_modify_class',
                           data=json.dumps({'classId': class_id,
                                            'professorUserNames': professor_usernames,
                                            'studentUserNames': new_student_names}),
                           content_type='application/json')
        self.assertEqual(rv.status_code, 200)

if __name__ == '__main__':
    unittest.main()
