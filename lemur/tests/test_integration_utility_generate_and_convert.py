# This file consists of testing for functions that generate messages/strings
# and convert data into another format
import sys
sys.path.append('../..')
# Libraries
# Standard library
import unittest

# Local
from base_case import LemurBaseCase
from lemur.lemur import db
from lemur import models as m
import helper_random as r
from lemur.utility_generate_and_convert import (
    serialize_lab_list,
    serialize_experiment_list,
    serialize_user_list,
    serialize_class_list,
    change_observation_organization
)

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
ds = db.session


# This file consists of functions that generate strings and convert data format
class IntegrationTestUtilityGenerateAndConvert(LemurBaseCase):
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

if __name__ == '__main__':
    unittest.main()
