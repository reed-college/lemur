# This file consists of testing for the creation of objects and their
# relationship in db
import sys
sys.path.append('../..')
# Libraries
# Standard library
import unittest
# Local
from lemur import (app, db)
from lemur import models as m
import helper_random as r
from lemur.utility.utility_generate_and_convert import (generate_lab_id,
                                                        generate_experiment_id,
                                                        generate_observation_id,
                                                        generate_class_id)
from lemur.utility.utility_find_and_get import (get_experiment,
                                                get_observation,
                                                get_user,
                                                get_role,
                                                get_power,
                                                get_class)
ds = db.session


class IntegrationTestDBAndModels(unittest.TestCase):
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
        name = r.randlength_word()
        time = r.randlength_word()
        class_id = generate_class_id(name, time)
        while ds.query(m.Class).filter(m.Class.id == class_id).count() != 0:
            name = r.randlength_word()
            time = r.randlength_word()
            class_id = generate_class_id(name, time)
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
        name = r.randlength_word()
        class_id = the_class.id
        description = r.randlength_word()
        status = 'Activated'
        lab_id = generate_lab_id(name, class_id)
        while ds.query(m.Lab).filter(m.Lab.id == lab_id).count() != 0:
            class_id = r.rand_classid()
            description = r.randlength_word()
            lab_id = generate_lab_id(name, class_id)

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

    def test_create_experiment(self, lab_id=r.rand_lab_id()):
        name = r.randlength_word()
        description = r.randlength_word()
        order = r.rand_order()
        value_type = r.rand_value_type()
        value_range = r.rand_value_range()
        value_candidates = r.rand_value_candidates()
        experiment_id = generate_experiment_id(lab_id, name)
        while ds.query(m.Experiment).filter(m.Experiment.id == experiment_id).count() != 0:
            name = r.randlength_word()
            lab_id = r.rand_lab_id()
            experiment_id = generate_experiment_id(lab_id, name)
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

    def test_create_observation(self, experiment_id=r.rand_experiment_id()):
        student_name = r.randlength_word()
        datum = r.randlength_word()
        observation_id = generate_observation_id(experiment_id, student_name)
        while ds.query(m.Observation).filter(m.Observation.id == observation_id).count() != 0:
            student_name = r.randlength_word()
            experiment_id = r.rand_experiment_id()
            observation_id = generate_observation_id(experiment_id,
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
        username = r.randlength_word()
        while ds.query(m.User).filter(m.User.id == username).count() != 0:
            username = r.randlength_word()
        name = r.randlength_word()
        user = m.User(id=username,
                      name=name)
        ds.add(user)
        ds.commit()
        user_query = ds.query(m.User).filter(m.User.id == username).first()
        self.assertEqual(user_query.id, username)
        self.assertEqual(user_query.name, name)
        return user_query

    def test_create_role(self):
        name = r.randlength_word()
        while ds.query(m.Role).filter(m.Role.name == name).count() != 0:
            name = r.randlength_word()
        powers = r.rand_powers()
        role = m.Role(name=name, powers=powers)
        ds.add(role)
        ds.commit()
        role_query = get_role(name)
        self.assertEqual(role_query.name, name)
        self.assertEqual(role_query.powers, powers)
        return role_query

    def test_create_power(self):
        id = r.randlength_word()
        while ds.query(m.Power).filter(m.Power.id == id).count() != 0:
            id = r.randlength_word()
        power = m.Power(id=id)
        ds.add(power)
        ds.commit()
        power_query = get_power(id)
        self.assertEqual(power_query.id, id)
        return power_query

    # --- Test all relatinships in models.py ---
    # One function only tests one relationship at a time
    def test_relationship_lab_experiments(self):
        lab = self.test_create_lab()
        for i in range(r.rand_round()):
            lab.experiments.append(self.test_create_experiment(lab.id))
        for experiment in lab.experiments:
            experiment_query = get_experiment(experiment.id)
            self.assertEqual(experiment_query.lab_id,  lab.id)

    def test_relationship_lab_classes(self):
        lab = self.test_create_lab()
        class_list = []
        for i in range(r.rand_round()):
            the_class = self.test_create_class()
            the_class.lab = lab
            class_list.append(the_class)
        for c in class_list:
            the_class = get_class(c.id)
            self.assertEqual(the_class.lab.id, lab.id)

    def test_relationship_lab_users(self):
        lab = self.test_create_lab()
        for i in range(r.rand_round()):
            lab.users.append(self.test_create_user())
        for user in lab.users:
            user_query = get_user(user.id)
            self.assertEqual(user_query.labs[0].id, lab.id)

    def test_relationship_experiment_observations(self):
        experiment = self.test_create_experiment()
        for i in range(r.rand_round()):
            experiment.observations.append(self.test_create_observation(experiment.id))
        for observation in experiment.observations:
            observation_query = get_observation(observation.id)
            self.assertEqual(observation_query.experiment_id, experiment.id)

    def test_relationship_classes_users(self):
        the_class = self.test_create_class()
        for i in range(r.rand_round()):
            the_class.users.append(self.test_create_user())
        for user in the_class.users:
            user_query = get_user(user.id)
            self.assertEqual(user_query.the_class.id, the_class.id)

    def test_relationship_users_role(self):
        role = self.test_create_role()
        for i in range(r.rand_round()):
            role.users.append(self.test_create_user())
        for user in role.users:
            user_query = get_user(user.id)
            self.assertEqual(user_query.role_name, role.name)

if __name__ == '__main__':
    unittest.main()
