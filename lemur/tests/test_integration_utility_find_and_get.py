# This file consists of testing for functions that find/get objects from db
# Libraries
# Standard library
import unittest
from random import randint

# Local
from base_case import LemurBaseCase
import helper_random as r
from lemur.utility_find_and_get import (
    lab_exists,
    experiment_exists,
    observation_exists,
    user_exists,
    class_exists,
    get_lab,
    get_experiment,
    get_observation,
    get_user,
    get_role,
    get_power,
    get_class,
    get_all_lab,
    get_all_experiment,
    get_all_user,
    get_all_admin,
    get_all_superadmin,
    get_all_class,
    get_available_labs_for_user,
    get_experiments_for_lab,
    get_observations_for_experiment,
    get_class_id_list,
    find_all_labs,
    find_lab_copy_id,
    find_all_observations_for_labs,
    find_lab_list_for_user,
    find_observation_number_for_experiment
)


class IntegrationTestUtilityFindAndGet(LemurBaseCase):
    # Construct a lab with experiments which have observations input by
    # students(they will be stored in the database before the function returns)
    def construct_lab_observations(self, student_num=5, experiment_num=5):
        student_role = get_role('Student')
        students = []
        for _ in range(student_num):
            student = r.create_user(self.ds)
            student.role = student_role
            students.append(student)

        lab = r.create_lab(self.ds)
        lab.users = students
        for j in range(experiment_num):
            experiment = r.create_experiment(self.ds, lab.id)
            for k in range(student_num):
                observation = r.create_observation(self.ds, experiment.id)
                observation.student_name = students[k].name
                experiment.observations.append(observation)

            lab.experiments.append(experiment)
        return lab

    def test_lab_exists(self):
        lab = r.create_lab(self.ds)
        self.assertTrue(lab_exists(lab.id))
        self.assertFalse(lab_exists(lab.id+'123'))

    def test_experiment_exists(self):
        experiment = r.create_experiment(self.ds)
        self.assertTrue(experiment_exists(experiment.id))
        self.assertFalse(experiment_exists(experiment.id+'123'))

    def test_observation_exists(self):
        observation = r.create_observation(self.ds)
        self.assertTrue(observation_exists(observation.id))
        self.assertFalse(observation_exists(observation.id+'123'))

    def test_class_exists(self):
        the_class = r.create_class(self.ds)
        self.assertTrue(class_exists(the_class.id))
        self.assertFalse(class_exists(the_class.id+'123'))

    def test_user_exists(self):
        user = r.create_user(self.ds)
        self.assertTrue(user_exists(user.id))
        self.assertFalse(user_exists(user.id+'123'))

    # Testing for functions that query a single object from the database
    def test_get_lab(self):
        lab = r.create_lab(self.ds)
        lab_query = get_lab(lab.id)
        self.assertEqual(lab_query, lab)

    def test_get_experiment(self):
        experiment = r.create_experiment(self.ds)
        experiment_query = get_experiment(experiment.id)
        self.assertEqual(experiment_query, experiment)

    def test_get_observation(self):
        observation = r.create_observation(self.ds)
        observation_query = get_observation(observation.id)
        self.assertEqual(observation_query, observation)

    def test_get_power(self):
        power = r.create_power(self.ds)
        power_query = get_power(power.id)
        self.assertEqual(power_query, power)

    def test_get_role(self):
        role = r.create_role(self.ds)
        role_query = get_role(role.name)
        self.assertEqual(role_query, role)

    def test_get_user(self):
        user = r.create_user(self.ds)
        user_query = get_user(user.id)
        self.assertEqual(user_query, user)

    def test_get_class(self):
        the_class = r.create_class(self.ds)
        class_query = get_class(the_class.id)
        self.assertEqual(class_query, the_class)

    # - Testing for functions that query all objects of a class from the
    # database -
    def test_get_all_lab(self):
        lab_ids = [r.create_lab(self.ds).id for _ in range(r.rand_round())]
        for lab_id in lab_ids:
            self.assertIn(get_lab(lab_id), get_all_lab())

    def test_get_all_experiment(self):
        experiment_ids = [r.create_experiment(self.ds).id for _ in range(r.rand_round())]
        for experiment_id in experiment_ids:
            self.assertIn(get_experiment(experiment_id),
                          get_all_experiment())

    def test_get_all_class(self):
        class_ids = [r.create_class(self.ds).id for _ in range(r.rand_round())]
        for class_id in class_ids:
            self.assertIn(get_class(class_id), get_all_class())

    def test_get_all_admin(self):
        admin_ids = []
        for _ in range(r.rand_round()):
            user = r.create_user(self.ds)
            user.role_name = r.rand_role()
            if user.role_name == 'Admin':
                admin_ids.append(user.id)
        for admin_id in admin_ids:
            self.assertIn(get_user(admin_id), get_all_admin())

    def test_get_all_superadmin(self):
        superadmin_ids = []
        for _ in range(r.rand_round()):
            user = r.create_user(self.ds)
            user.role_name = r.rand_role()
            if user.role_name == 'SuperAdmin':
                superadmin_ids.append(user.id)
        for superadmin_id in superadmin_ids:
            self.assertIn(get_user(superadmin_id), get_all_superadmin())

    # - Testing for functions that query a list of objects of one class
    # for an object of another class -
    def test_get_available_labs_for_user(self):
        count = 0
        user = r.create_user(self.ds)
        user.role_name == r.rand_role()
        self.assertEqual(len(get_available_labs_for_user(user)), count)
        for i in range(r.rand_round()):
            lab = r.create_lab(self.ds)
            # The lab may not be the user's own lab
            # If user is not a super admin, other admins' labs
            # should not be queried
            if randint(0, 1) == 1:
                user.labs.append(lab)
                count += 1
            elif user.role_name == 'SuperAdmin':
                count += 1

            self.assertEqual(len(get_available_labs_for_user(user)), count)

    def test_get_experiments_for_lab(self):
        experiment_ids = []
        lab = r.create_lab(self.ds)
        self.assertEqual(len(get_experiments_for_lab(lab.id)), 0)
        for i in range(r.rand_round()):
            experiment = r.create_experiment(self.ds)
            experiment_ids.append(experiment.id)
            lab.experiments.append(experiment)
        for experiment_id in experiment_ids:
            self.assertIn(get_experiment(experiment_id),
                          get_experiments_for_lab(lab.id))

    def test_get_observations_for_experiment(self):
        observation_ids = []
        experiment = r.create_experiment(self.ds)
        self.assertEqual(len(get_observations_for_experiment(experiment.id)), 0)
        for i in range(r.rand_round()):
            observation = r.create_observation(self.ds)
            observation_ids.append(observation.id)
            experiment.observations.append(observation)
        for observation_id in observation_ids:
            self.assertIn(get_observation(observation_id),
                          get_observations_for_experiment(experiment.id))

    def test_find_observation_number_for_experiment(self):
        count = 0
        experiment = r.create_experiment(self.ds)
        self.assertEqual(find_observation_number_for_experiment(experiment.id),
                         count)
        for i in range(r.rand_round()):
            observation = r.create_observation(self.ds)
            experiment.observations.append(observation)
            count += 1
            self.assertEqual(find_observation_number_for_experiment(experiment.id),
                             count)

    # - Testing for functions that returns a list of a certain attribute of
    # all the objects in this class -
    def test_get_class_id_list(self):
        user = r.create_user(self.ds)
        random_admin_role = get_role(r.rand_admin())
        user.role = random_admin_role
        class_id_list = []
        for i in range(r.rand_round()):
            the_class = r.create_class(self.ds)
            class_id_list.append(the_class.id)

        class_id_list_retrieved = get_class_id_list(user)
        if user.role_name == 'SuperAdmin':
            for class_id in class_id_list:
                self.assertIn(class_id, class_id_list_retrieved)

    def test_get_all_user(self):
        usernames = []
        for i in range(r.rand_round()):
            user = r.create_user(self.ds)
            user.role_name = r.rand_role()
            usernames.append(user.id)

        usernames_retrieved = [u.id for u in get_all_user()]
        for username in usernames:
            self.assertIn(username, usernames_retrieved)

    # - Testing for functions that return the info of objects
    # with a certain format -
    #
    # This test has been failing non-deterministically. My current belief is
    # that the underlying code is good, but the test is bad (too complex, and
    # relies on no other code having side-effects, which is patently false.)
    # - RMD 2017-10-02
    # def test_find_lab_list_for_user(self):
    #     user = r.create_user(self.ds)
    #     random_admin_role = get_role(r.rand_admin())
    #     user.role = random_admin_role
    #     # If the user is a "SuperAdmin", some other code I can't find
    #     # auto-creates two labs for that user.
    #     count = len(find_lab_list_for_user(user))
    #     for i in range(r.rand_round()):
    #         lab = r.create_lab(self.ds)
    #         # The lab may not be the user's own lab
    #         # If user is not SuperAdmin, other's labs
    #         # should not be queried
    #         if user.role_name == 'SuperAdmin':
    #             count += 1
    #         else:
    #             user.labs.append(lab)
    #             count += 1

    #     self.assertEqual(len(find_lab_list_for_user(user)), count)

    def test_find_all_labs(self):
        user = r.create_user(self.ds)
        user.role == get_role(r.rand_admin())
        for i in range(r.rand_round()):
            user.labs.append(r.create_lab(self.ds))

        labs = find_all_labs(user)

        for lab in labs['activated']:
            self.assertEqual(lab['status'], 'Activated')

        for lab in labs['unactivated']:
            self.assertEqual(lab['status'], 'Unactivated')

        for lab in labs['downloadable']:
            self.assertEqual(lab['status'], 'Downloadable')

    def test_find_lab_copy_id(self):
        lab = r.create_lab(self.ds)
        new_lab_id = find_lab_copy_id(lab.id)
        self.assertEqual(new_lab_id, 'copy1-'+lab.id)

    # This test is far from covering all the possibilities
    def test_find_all_observations_for_labs(self):
        student_num = randint(1, 5)
        experiment_num = randint(1, 5)
        lab = self.construct_lab_observations(student_num, experiment_num)
        observations_group_by_experiment_name, observations_group_by_student, _, _, _ = find_all_observations_for_labs([lab.id])
        self.assertEqual(len(observations_group_by_experiment_name), experiment_num)
        self.assertEqual(len(observations_group_by_student), student_num)

if __name__ == '__main__':
    unittest.main()
