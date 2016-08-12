# This file consists of testing for functions that generate messages/strings
# and convert data into another format
import sys
sys.path.append('../..')
# Libraries
# Standard library
import unittest
from random import randint

# Local
print(sys.path)
from lemur import (app, db)
from lemur import models as m
import helper_random as r
from lemur.utility.utility_generate_and_convert import (check_existence,
                                                        generate_err_msg,
                                                        generate_lab_id,
                                                        generate_experiment_id,
                                                        generate_observation_id,
                                                        generate_class_id,
                                                        decompose_lab_id,
                                                        decompose_class_id,
                                                        serialize_lab_list,
                                                        serialize_experiment_list,
                                                        serialize_user_list,
                                                        serialize_class_list,
                                                        tranlate_term_code_to_semester,
                                                        cleanup_class_data,
                                                        pack_labinfo_sent_from_client,
                                                        change_observation_organization
                                                        )
from lemur.utility.utility_find_and_get import (get_lab,
                                                get_experiment,
                                                get_user,
                                                get_role,
                                                get_power,
                                                get_class,
                                                get_all_lab,
                                                get_all_experiment,
                                                get_all_user,
                                                get_all_class,
                                                find_all_observations_for_labs)
ds = db.session


# This file consists of functions that generate strings and convert data format
class IntegrationTestUtilityGenerateAndConvert(unittest.TestCase):
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

    # tidy up after a test has been run
    def tearDown(self):
        # remove and clean the database completely
        ds.remove()
        db.drop_all()

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

    def test_check_existence(self):
        key1 = 'key1'
        key2 = 'key2'
        key3 = 'key3'
        form = {key1: 'value1', key2: 'value2'}
        success_msg = ''
        err_msg = key3 + ' is not defined\n'
        self.assertEqual(check_existence(form, key1, key2), success_msg)
        self.assertEqual(check_existence(form, key1, key3), err_msg)

    def test_generate_err_msg(self):
        name1 = 'name1'
        value1 = 'value1'
        name2 = 'name2'
        value2 = 'value2'
        expected_msg = (name1+':'+value1+' and '+name2 +
                        ':'+value2+' are different')
        self.assertEqual(generate_err_msg(name1, value1, name2, value2),
                         expected_msg)

    def test_generate_lab_id(self):
        lab_name = r.randlength_word()
        class_id = r.rand_classid()
        expected_lab_id = lab_name + ':' + class_id
        generated_lab_id = generate_lab_id(lab_name, class_id)
        self.assertEqual(generated_lab_id, expected_lab_id)

    def test_generate_experiment_id(self):
        lab_id = r.randlength_word()
        experiment_name = r.randlength_word()
        expected_experiment_id = lab_id+':'+experiment_name
        generated_experiment_id = generate_experiment_id(lab_id, experiment_name)
        self.assertEqual(generated_experiment_id, expected_experiment_id)

    def test_generate_observation_id(self):
        experiment_id = r.randlength_word()
        student_name = r.randlength_word()
        expected_observation_id = experiment_id+':'+student_name
        self.assertEqual(generate_observation_id(experiment_id, student_name),
                         expected_observation_id)

    def test_generate_class_id(self):
        class_name = r.randlength_word()
        class_time = r.rand_classtime()
        expected_class_id = class_name+'_'+class_time
        self.assertEqual(generate_class_id(class_name, class_time),
                         expected_class_id)

    def test_decompose_lab_id(self):
        lab_name = r.randlength_word()
        class_id = r.rand_classid()
        lab_id = generate_lab_id(lab_name, class_id)
        lab_info = decompose_lab_id(lab_id)
        self.assertEqual(lab_info['lab_name'], lab_name)
        self.assertEqual(lab_info['class_id'], class_id)

    def test_decompose_class_id(self):
        class_name = r.randlength_word()
        class_time = r.randlength_word()
        class_id = generate_class_id(class_name, class_time)
        class_info = decompose_class_id(class_id)
        self.assertEqual(class_info['class_name'], class_name)
        self.assertEqual(class_info['class_time'], class_time)

    # Get all objects of one class and then serialize them into
    # a list of python dictionary
    def test_serialize_lab_list(self):
        for i in range(r.rand_round()):
            r.create_lab(db)
        lab_list_serialized = serialize_lab_list(get_all_lab())
        for lab in lab_list_serialized:
            lab_query = get_lab(lab['lab_id'])
            self.assertEqual(lab_query.name, lab['lab_name'])
            self.assertEqual(lab_query.description, lab['description'])
            self.assertEqual(lab_query.status, lab['status'])
            self.assertEqual(len(lab_query.experiments), lab['experiments'])

    def test_serialize_experiment_list(self):
        for i in range(r.rand_round()):
            r.create_experiment(db)
        experiment_list_serialized = serialize_experiment_list(get_all_experiment())
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
        for i in range(r.rand_round()):
            user = r.create_user(db)
            user.role_name = r.rand_role()
        user_list_serialized = serialize_user_list(get_all_user())
        for user in user_list_serialized:
            user_query = get_user(user['username'])
            self.assertEqual(user_query.id, user['username'])
            self.assertEqual(user_query.name, user['name'])

    def test_serialize_class_list(self):
        for i in range(r.rand_round()):
            r.create_class(db)
        class_list_serialized = serialize_class_list(get_all_class())
        for c in class_list_serialized:
            class_query = get_class(c['id'])
            self.assertEqual(class_query.id, c['id'])
            self.assertEqual(class_query.name, c['name'])
            self.assertEqual(class_query.time, c['time'])

    def test_change_observation_organization(self):
        student_num = 5
        experiment_num = 5
        lab = self.construct_lab_observations(student_num, experiment_num)
        observations_group_by_experiment_name, _, _, _, _ = find_all_observations_for_labs([lab.id])
        observations_group_by_student = change_observation_organization(observations_group_by_experiment_name)
        self.assertEqual(len(observations_group_by_student), student_num)

    # Convert a term code into a semester name
    # e.g. 201701 -> FALL2017
    def test_tranlate_term_code_to_semester(self):
        term_code = '201701'
        term_code2 = '203103'
        semester = 'FALL2016'
        semester2 = 'SPRING2031'
        self.assertEqual(tranlate_term_code_to_semester(term_code), semester)
        self.assertEqual(tranlate_term_code_to_semester(term_code2), semester2)

    def test_cleanup_class_data(self):
        # A snippet from real data
        class_data = [{'course_id': '11069', 'term_code': '201701', 'subject': 'BIOL', 'course_number': '331', 'section': 'F', 'section_type': 'Lecture', 'instructors': ['prof1']},
                      {'course_id': '10236', 'term_code': '201701', 'subject': 'BIOL', 'course_number': '101', 'section': 'F22', 'section_type': 'Lab', 'instructors': ['prof2']},
                      {'course_id': '10447', 'term_code': '201701', 'subject': 'BIOL', 'course_number': '101', 'section': 'F01', 'section_type': 'Lab Lecture', 'instructors': ['prof3', 'prof4', 'prof5']},
                      {'course_id': '10010', 'term_code': '201701', 'subject': 'BIOL', 'course_number': '470', 'section': 'YJS', 'section_type': 'Ind. study', 'instructors': ['prof6']}
                      ]
        cleaned_class_data = cleanup_class_data(class_data)
        course_numbers = [c['course_number'] for c in cleaned_class_data]
        # 470 should have been removed
        self.assertNotIn('470', course_numbers)

    # This doesn't check all the variables passed into lab_info
    def test_pack_labinfo_sent_from_client(self):
        clinet_form = {'labName': r.randlength_word(),
                       'classId': r.rand_classid(),
                       'professorName': r.randlength_word(),
                       'labDescription': r.randlength_word(),
                       'labQuestions': randint(1, 100)
                       }
        lab_info, err_msg = pack_labinfo_sent_from_client(clinet_form)
        self.assertEqual(len(lab_info['experiments']), clinet_form['labQuestions'], err_msg)

if __name__ == '__main__':
    unittest.main()
