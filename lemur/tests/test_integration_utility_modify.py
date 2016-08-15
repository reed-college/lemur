# This file consists of functions that add/delete/modify objects in db
import sys
sys.path.append('../..')
# Libraries
# Standard library
import unittest
from random import randint

# Third-party libraries
from werkzeug.datastructures import MultiDict

# Local
from lemur import (app, db, test_db_uri)
from lemur import models as m
from db_scripts.db_populate import populate_db
import helper_random as r
from lemur.utility_generate_and_convert import (check_existence,
                                                generate_lab_id,
                                                generate_experiment_id,
                                                generate_observation_id,
                                                generate_class_id,
                                                tranlate_term_code_to_semester)
from lemur.utility_find_and_get import (lab_exists,
                                        user_exists,
                                        class_exists,
                                        get_user,
                                        get_role,
                                        get_power,
                                        get_class,
                                        find_all_observations_for_labs,
                                        find_observation_number_for_experiment)

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
                                  update_users_by_data_from_iris)
ds = db.session


class IntegrationTestUtilityModify(unittest.TestCase):
    # this is automatically called for us when we run the test
    def setUp(self):
        # It disables the error catching during request handling so that we get
        # better error reports when performing test requests against the
        # application.
        app.config['TESTING'] = True
        # The database used for this suit of tests is not the one used by the
        # app. Before we run this test, we need to create a local database
        # called lemur_test
        app.config['SQLALCHEMY_DATABASE_URI'] = test_db_uri
        self.app = app.test_client()
        # Create all the tables
        db.create_all()
        # Insert all the roles(Student, Admin, SuperAdmin) that will be used
        m.Role.insert_roles()

    # tidy up after a test has been run
    def tearDown(self):
        # remove and clean the database completely
        ds.remove()
        db.drop_all()

    # Generate a json format dictionary that consists of information needed to
    # create a new lab with random values
    def construct_lab_dict(self):
        lab_dict = {'labName': r.randlength_word(),
                    'classId': r.rand_classid(),
                    'labDescription': r.randlength_word(),
                    'experiments': [],
                    'oldLabId': r.rand_lab_id()
                    }
        for i in range(r.rand_round()):
            exp_json = {'name': r.randlength_word(),
                        'description': r.randlength_word(),
                        'order': r.rand_order(),
                        'valueType': r.rand_value_type(),
                        'valueRange': r.rand_value_range(),
                        'valueCandidates': r.rand_value_candidates()

                        }
            lab_dict['experiments'].append(exp_json)
        return lab_dict

    # Construct a lab with experiments which have observations input by
    # students(they will be stored in the database before the function returns)
    def construct_lab_observations(self, student_num=5, experiment_num=5):
        student_role = get_role('Student')
        students = []
        for _ in range(student_num):
            student = r.create_user(db)
            student.role = student_role
            students.append(student)
        lab = r.create_lab(db)
        lab.users = students
        for j in range(experiment_num):
            experiment = r.create_experiment(db, lab.id)
            for k in range(student_num):
                observation = r.create_observation(db, experiment.id)
                observation.student_name = students[k].name
                experiment.observations.append(observation)
            lab.experiments.append(experiment)
        return lab

    # - Testing functions for functions that add/delete/modify an object or
    # related functions with the input in a certain format -
    def test_delete_lab(self):
        lab = r.create_lab(db)
        lab_id = lab.id
        delete_lab(lab_id)
        self.assertFalse(lab_exists(lab_id))

    def test_modify_lab(self):
        built_in_ids = populate_db()
        the_class = get_class(built_in_ids['class_id'])
        lab_dict = self.construct_lab_dict()
        lab_dict['classId'] = generate_class_id(the_class.name, the_class.time)
        lab_name = r.randlength_word()
        lab_dict['labName'] = lab_name
        lab_id = generate_lab_id(lab_name, the_class.id)
        err_msg = modify_lab(lab_dict)
        self.assertEqual('', err_msg)
        self.assertTrue(lab_exists(lab_id))

    def test_duplicate_lab(self):
        built_in_ids = populate_db()
        lab_id = built_in_ids['lab_id']
        duplicate_lab(lab_id)
        self.assertTrue(lab_exists('copy1-'+lab_id))

    def test_change_lab_status(self):
        lab = r.create_lab(db)
        new_status = r.rand_lab_status()
        change_lab_status(lab.id, new_status)
        self.assertEqual(lab.status, new_status)

    def test_delete_observation(self):
        observation_ids = []
        for i in range(r.rand_round()):
            observation = r.create_observation(db)
            observation_ids.append(observation.id)
        delete_observation(observation_ids)
        for observation_id in observation_ids:
            self.assertFalse(check_existence(observation_id))

    def test_add_observation(self):
        experiment = r.create_experiment(db)
        observation_list = []
        for i in range(r.rand_round()):
            student_name = r.randlength_word()
            observation_datum = r.randlength_word()
            experiment_id = experiment.id
            observation_id = generate_observation_id(experiment_id, student_name)
            observation_list.append({'studentName': student_name,
                                     'observationData': observation_datum,
                                     'experimentId': experiment_id,
                                     'observationId': observation_id
                                     })
        add_observation(observation_list)
        observation_num = find_observation_number_for_experiment(experiment.id)
        self.assertEqual(observation_num, len(observation_list))

    def test_add_observations_sent_by_students(self):
        student_num = 5
        experiment_num = 5
        lab = self.construct_lab_observations(student_num, experiment_num)
        observations_group_by_experiment_name, observations_group_by_student, _, _, _ = find_all_observations_for_labs([lab.id])
        err_msg = add_observations_sent_by_students(observations_group_by_student)
        self.assertEqual(student_num * experiment_num,
                         ds.query(m.Observation).count(), err_msg)

    def test_add_user(self):
        username = r.randlength_word()
        user_info = MultiDict([('username', username),
                               ('role', r.rand_role()),
                               ('name', r.randlength_word())])
        add_user(user_info)
        user_query = get_user(username)
        self.assertEqual(user_query.id, user_info['username'])
        self.assertEqual(user_query.name, user_info['name'])

    def test_delete_user(self):
        admin_role = get_role(r.rand_admin())
        admin = r.create_user(db)
        admin_id = admin.id
        admin.role = admin_role
        delete_user(admin_id)
        self.assertFalse(user_exists(admin_id))

    def test_change_user_info(self):
        username = r.create_user(db).id
        role_name = r.rand_role()
        class_ids = [r.create_class(db).id]
        change_user_info(username, role_name, class_ids)
        the_user = get_user(username)
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
                                ('className', r.randlength_word()),
                                ('classTime', r.rand_classtime())])
        for i in range(r.rand_round()):
            class_info['students'] += (r.randlength_word()+',')
        class_info['students'] = class_info['students'].rstrip(',')
        err_msg = add_class(class_info)
        if err_msg == '':
            class_id = generate_class_id(class_info['className'],
                                         class_info['classTime'])
            the_class = get_class(class_id)
            self.assertEqual(the_class.id, class_id, err_msg)

    def test_delete_class(self):
        the_class = r.create_class(db)
        class_id = the_class.id
        delete_class(class_id)
        self.assertFalse(class_exists(class_id))

    def test_change_class_users(self):
        built_in_ids = populate_db()
        the_class = get_class(built_in_ids['class_id'])
        new_user_ids = [built_in_ids['student_id'],
                        built_in_ids['admin_id']]
        change_class_users(the_class.id, new_user_ids)
        class_user_ids = [user.id for user in the_class.users]
        for user_id in new_user_ids:
            self.assertIn(user_id, class_user_ids)

    def test_populate_db_with_classes_and_professors(self):
        # A snippet from real data
        class_data = [{'course_id': '11069', 'term_code': '201701', 'subject': 'BIOL', 'course_number': '331', 'section': 'F', 'section_type': 'Lecture', 'instructors': ['prof1']},
                      {'course_id': '10236', 'term_code': '201701', 'subject': 'BIOL', 'course_number': '101', 'section': 'F22', 'section_type': 'Lab', 'instructors': ['prof2']},
                      {'course_id': '10447', 'term_code': '201701', 'subject': 'BIOL', 'course_number': '101', 'section': 'F01', 'section_type': 'Lab Lecture', 'instructors': ['prof3', 'prof4', 'prof5']},
                      {'course_id': '10010', 'term_code': '201701', 'subject': 'BIOL', 'course_number': '470', 'section': 'YJS', 'section_type': 'Ind. study', 'instructors': ['prof6']}
                      ]
        populate_db_with_classes_and_professors(class_data)
        # Pick a random professor and a random class to test their existence

        random_index = randint(0, len(class_data)-2)
        professor_id = class_data[random_index]['instructors'][0]
        self.assertTrue(user_exists(professor_id))
        class_name = class_data[random_index]['subject'] + class_data[random_index]['course_number']
        class_time = tranlate_term_code_to_semester(class_data[random_index]['term_code'])
        class_id = generate_class_id(class_name, class_time)
        self.assertTrue(class_exists(class_id))

    def test_update_users_by_data_from_iris(self):
        registration_data = [{"user_name": "fake1", "course_id": "10508", "term_code": "201701", "subject": "BIOL", "course_number": "356", "section": "FL1"},
                             {"user_name": "fake2", "course_id": "11055", "term_code": "201701", "subject": "BIOL", "course_number": "351", "section": "FL1"},
                             {"user_name": "fake3", "course_id": "11055", "term_code": "201701", "subject": "BIOL", "course_number": "351", "section": "FL1"},
                             {"user_name": "fake4", "course_id": "10369", "term_code": "201701", "subject": "BIOL", "course_number": "342", "section": "FL1"}
                             ]
        # The classes don't exist in db so the users shouldn't be added
        err_msg = update_users_by_data_from_iris(registration_data)
        self.assertNotEqual('', err_msg)

if __name__ == '__main__':
    unittest.main()
