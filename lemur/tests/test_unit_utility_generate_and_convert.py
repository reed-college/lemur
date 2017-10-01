# This file consists of testing for functions that generate messages/strings
# and convert data into another format
import sys
sys.path.append('../..')
# Libraries
# Standard library
import unittest
from unittest.mock import patch
from random import randint

# Local
import helper_random as r
from helper_mock import (
    generate_lab_mock,
    generate_experiment_mock,
    generate_observation_mock,  # Unused
    generate_user_mock,
    generate_class_mock
)

from lemur.utility_generate_and_convert import (
    check_existence,
    generate_err_msg,
    generate_lab_id,
    generate_experiment_id,
    generate_observation_id,
    generate_class_id,
    generate_user_name,
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

# ...most of these might be unused?
from lemur.utility_find_and_get import (
    get_lab,
    get_experiment,
    get_user,
    get_role,
    get_power,
    get_class,
    get_all_lab,
    get_all_experiment,
    get_all_user,
    get_all_class,
    find_all_observations_for_labs
)


# This file consists of functions that generate strings and convert data format
class UnitTestUtilityGenerateAndConvert(unittest.TestCase):
    # this is automatically called for us when we run the test
    def setUp(self):
        pass

    # tidy up after a test has been run
    def tearDown(self):
        pass

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

    def test_generate_user_name(self):
        first_name = r.randlength_word()
        last_name = r.randlength_word()
        self.assertEqual(first_name+' '+last_name, generate_user_name(first_name, last_name))

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
    @patch('test_unit_utility_generate_and_convert.r.create_lab')
    def test_serialize_lab_list(self, create_lab_mock):
        lab_mock_list = []
        create_lab_mock.return_value = generate_lab_mock()
        for i in range(r.rand_round()):
            lab_mock_list.append(create_lab_mock())
        lab_list_serialized = serialize_lab_list(lab_mock_list)
        for i in range(len(lab_list_serialized)):
            self.assertEqual(lab_mock_list[i].name, lab_list_serialized[i]['lab_name'])
            self.assertEqual(lab_mock_list[i].description, lab_list_serialized[i]['description'])
            self.assertEqual(lab_mock_list[i].status, lab_list_serialized[i]['status'])
            self.assertEqual(len(lab_mock_list[i].experiments), lab_list_serialized[i]['experiments'])

    @patch('test_unit_utility_generate_and_convert.r.create_experiment')
    def test_serialize_experiment_list(self, create_experiment_mock):
        experiment_mock_list = []
        create_experiment_mock.return_value = generate_experiment_mock()
        for i in range(r.rand_round()):
            experiment_mock_list.append(create_experiment_mock())
        experiment_list_serialized = serialize_experiment_list(experiment_mock_list)
        for i in range(len(experiment_list_serialized)):
            self.assertEqual(experiment_mock_list[i].name, experiment_list_serialized[i]['experiment_name'])
            self.assertEqual(experiment_mock_list[i].description, experiment_list_serialized[i]['description'])
            self.assertEqual(experiment_mock_list[i].order, experiment_list_serialized[i]['order'])
            self.assertEqual(experiment_mock_list[i].value_type, experiment_list_serialized[i]['value_type'])
            self.assertEqual(experiment_mock_list[i].value_range, experiment_list_serialized[i]['value_range'])
            self.assertEqual(experiment_mock_list[i].value_candidates,
                             experiment_list_serialized[i]['value_candidates'])

    @patch('test_unit_utility_generate_and_convert.r.create_user')
    def test_serialize_user_list(self, create_user_mock):
        user_mock_list = []
        create_user_mock.return_value = generate_user_mock()
        for i in range(r.rand_round()):
            user_mock_list.append(create_user_mock())
        user_list_serialized = serialize_user_list(user_mock_list)
        for i in range(len(user_list_serialized)):
            self.assertEqual(user_mock_list[i].id, user_list_serialized[i]['username'])
            self.assertEqual(user_mock_list[i].name, user_list_serialized[i]['name'])

    @patch('test_unit_utility_generate_and_convert.r.create_class')
    def test_serialize_class_list(self, create_class_mock):
        class_mock_list = []
        create_class_mock.return_value = generate_class_mock()
        for i in range(r.rand_round()):
            class_mock_list.append(create_class_mock())
        class_list_serialized = serialize_class_list(class_mock_list)
        for i in range(len(class_list_serialized)):
            self.assertEqual(class_mock_list[i].id, class_list_serialized[i]['id'])
            self.assertEqual(class_mock_list[i].name, class_list_serialized[i]['name'])
            self.assertEqual(class_mock_list[i].time, class_list_serialized[i]['time'])

    def test_change_observation_organization(self):
        observations_group_by_experiment_name = r.rand_observations_group_by_experiment_name()
        observations_group_by_student = change_observation_organization(observations_group_by_experiment_name)
        self.assertEqual(len(observations_group_by_student), len(observations_group_by_experiment_name[0]['observations']))

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
        class_data = [{'course_id': '11069', 'term_code': '201701', 'subject': 'BIOL', 'course_number': '331', 'section': 'F', 'section_type': 'Lecture', 'instructors': [{"username": "prof1", "last_name": "Prof", "first_name": "One"}]},
                      {'course_id': '10236', 'term_code': '201701', 'subject': 'BIOL', 'course_number': '101', 'section': 'F22', 'section_type': 'Lab', 'instructors': [{"username": "prof2", "last_name": "Prof", "first_name": "Two"}]},
                      {'course_id': '10447', 'term_code': '201701', 'subject': 'BIOL', 'course_number': '101', 'section': 'F01', 'section_type': 'Lab Lecture', 'instructors': [{"username": "prof3", "last_name": "Prof", "first_name": "Three"},
                                                                                                                                                                                {"username": "prof4", "last_name": "Prof", "first_name": "Four"},
                                                                                                                                                                                {"username": "prof5", "last_name": "Prof", "first_name": "Five"}]},
                      {'course_id': '10010', 'term_code': '201701', 'subject': 'BIOL', 'course_number': '470', 'section': 'YJS', 'section_type': 'Ind. study', 'instructors': [{"username": "prof6", "last_name": "Prof", "first_name": "Six"}]}
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
