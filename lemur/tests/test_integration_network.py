# This file consists of testing for view functions in views.py by
# sending request to the server
import sys
sys.path.append('../..')
# Libraries
# Standard library
import unittest
import json
from random import randint

# Third-party libraries
from bs4 import BeautifulSoup
from werkzeug.datastructures import MultiDict

# Local
from lemur import (app, db, test_db_uri)
from lemur import models as m
from db_scripts.db_populate import populate_db
import helper_random as r
from lemur.utility.generate_and_convert import (generate_lab_id,
                                                generate_experiment_id,
                                                generate_observation_id,
                                                generate_class_id,
                                                pack_labinfo_sent_from_client)
from lemur.utility.find_and_get import (lab_exists,
                                        user_exists,
                                        class_exists,
                                        observation_exists,
                                        get_lab,
                                        get_experiment,
                                        get_observation,
                                        get_user,
                                        get_role,
                                        get_power,
                                        get_class)
ds = db.session


class IntegrationTestNetwork(unittest.TestCase):
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
        # Populate db with objects
        self.built_in_ids = populate_db()

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

    # --- Test view functions in views.py by sending http request ---
    # This only covers superadmin case
    def test_login_logout(self):
        superadmin = get_user(self.built_in_ids['superadmin_id'])
        rv = self.login(superadmin.id)
        soup = self.decode(rv)
        self.assertIn(superadmin.id,
                      soup.find('p', {'id': 'welcomeMsg'}).text)
        rv = self.logout()
        soup = self.decode(rv)
        self.assertEqual('Login', soup.title.text)

    def test_student_home(self):
        student = get_user(self.built_in_ids['student_id'])
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
        admin = get_user(self.built_in_ids['admin_id'])
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
        superadmin = get_user(self.built_in_ids['superadmin_id'])
        self.login(superadmin.id)
        # superadmin has power to access superadmin_home
        rv = self.app.get('/superadmin_home')
        soup = self.decode(rv)
        self.assertIn(superadmin.id,
                      soup.find('p', {'id': 'welcomeMsg'}).text)

    def test_student_select_lab(self):
        student = get_user(self.built_in_ids['student_id'])
        self.login(student.id)

        # The lab should not be visible since it's not
        # in the student's lab list
        lab = get_lab(self.built_in_ids['lab_id'])
        rv = self.app.get('/student_select_lab')
        soup = self.decode(rv)
        self.assertEqual(None, soup.find('p', {'id': 'welcomeMsg'}))

        # Start a new session
        # The lab should be visible after it is
        # added into the lab list of the student
        student = get_user(student.id)
        lab = get_lab(self.built_in_ids['lab_id'])
        student.labs.append(lab)
        ds.commit()

        rv = self.app.get('/student_select_lab')
        soup = self.decode(rv)
        self.assertIn(lab.name, soup.tbody.text)

    def test_student_data_entry(self):
        student = get_user(self.built_in_ids['student_id'])
        lab = get_lab(self.built_in_ids['lab_id'])
        experiment = get_experiment(self.built_in_ids['experiment_id'])
        # The page will be redirected to the log in page if the user
        # does not have the power to enter data for the current lab

        self.login(student.id)
        rv = self.app.get('/student_data_entry/'+lab.id, follow_redirects=True)
        soup = self.decode(rv)
        self.assertIn(experiment.name, soup.tbody.text)

    def test__student_receive_data(self):
        student = get_user(self.built_in_ids['student2_id'])
        lab = get_lab(self.built_in_ids['lab_id'])
        experiment = get_experiment(self.built_in_ids['experiment_id'])
        student_id = student.id
        student.role = get_role('Student')
        observation_datum = r.randlength_word()
        self.login(student.id)

        # Start a new session
        student = get_user(student_id)
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
        student = get_user(student_id)
        observation_id = generate_observation_id(experiment.id,
                                                 student.id)
        observation_query = get_observation(observation_id)
        self.assertEqual(observation_query.datum, observation_datum)

    def test_admin_create_and_manage_lab(self):
        superadmin = get_user(self.built_in_ids['superadmin_id'])
        the_class = get_class(self.built_in_ids['class_id'])
        self.login(superadmin.id)
        # GET
        lab = get_lab(self.built_in_ids['lab_id'])
        rv = self.app.get('/admin_create_and_manage_lab')
        soup = self.decode(rv)
        self.assertIn(lab.name, soup.text)
        # POST
        random_lab_name = r.randlength_word()
        lab_form = MultiDict([('labName', random_lab_name),
                              ('classId', the_class.id),
                              ('className', the_class.name),
                              ('professorName', superadmin.id),
                              ('labDescription', r.randlength_word()),
                              ('labQuestions', randint(1, 5))])
        headers = {'Content-type': 'application/x-www-form-urlencoded',
                   'Accept': 'text/plain'}
        rv = self.app.post('/admin_create_and_manage_lab',
                           data=lab_form,
                           headers=headers, follow_redirects=True)
        soup = self.decode(rv)
        self.assertEqual(random_lab_name,
                         soup.find('input', {'name': 'labName'}).get('value'))

    def test_admin_setup_labs(self):
        superadmin = get_user(self.built_in_ids['superadmin_id'])
        self.login(superadmin.id)
        clinet_form = {'labName': r.randlength_word(),
                       'className': r.randlength_word(),
                       'classTime': r.rand_classtime(),
                       'professorName': r.randlength_word(),
                       'labDescription': r.randlength_word(),
                       'labQuestions': randint(1, 100)
                       }
        lab_info, err_msg = pack_labinfo_sent_from_client(clinet_form)
        rv = self.app.get('/admin_create_and_manage_lab?lab_info='+json.dumps(dict(labinfo=lab_info)),
                          follow_redirects=True)
        soup = self.decode(rv)
        self.assertIn('admin_create_and_manage_lab', soup.text)

    def test__admin_receive_setup_labs_data(self):
        superadmin = get_user(self.built_in_ids['superadmin_id'])
        self.login(superadmin.id)
        lab_dict = self.construct_lab_dict()
        the_class = get_class(self.built_in_ids['class_id'])
        lab_dict['classId'] = generate_class_id(the_class.name, the_class.time)
        lab_name = r.randlength_word()
        lab_dict['labName'] = lab_name
        lab_id = generate_lab_id(lab_name, the_class.id)

        # Add the corresponding class first since without class
        # the lab will not be able to be added
        self.app.post('/_admin_receive_setup_labs_data',
                      data=json.dumps(lab_dict),
                      content_type='application/json')
        self.assertTrue(lab_exists(lab_id))

    def test_admin_modify_lab(self):
        superadmin = get_user(self.built_in_ids['superadmin_id'])
        self.login(superadmin.id)
        rv = self.app.get('/admin_modify_lab/'+self.built_in_ids['lab_id'])
        self.assertTrue(rv.status_code, 200)

    # This only tests one possibility: when the user change the description
    # of the lab. We need more tests!
    def test__admin_modify_lab(self):
        # Add a new lab
        superadmin = get_user(self.built_in_ids['superadmin_id'])
        self.login(superadmin.id)
        lab_dict = self.construct_lab_dict()

        the_class = get_class(self.built_in_ids['class_id'])
        lab_dict['classId'] = generate_class_id(the_class.name, the_class.time)
        lab_name = r.randlength_word()
        lab_dict['labName'] = lab_name
        lab_id = generate_lab_id(lab_name, the_class.id)

        self.app.post('/_admin_receive_setup_labs_data',
                      data=json.dumps(lab_dict),
                      content_type='application/json')

        # Modify the lab's description we just set up
        lab_dict['labDescription'] = r.randlength_word()
        lab_dict['oldLabId'] = lab_id
        self.app.post('/_admin_modify_lab',
                      data=json.dumps(lab_dict),
                      content_type='application/json')
        lab_query = get_lab(lab_id)
        self.assertEqual(lab_dict['labDescription'], lab_query.description)

    def test__admin_duplicate_lab(self):
        superadmin = get_user(self.built_in_ids['superadmin_id'])
        self.login(superadmin.id)
        lab_id = self.built_in_ids['lab_id']
        self.app.post('/_admin_duplicate_lab',
                      data=json.dumps({'labId': lab_id}),
                      content_type='application/json')
        self.assertTrue(lab_exists('copy1-'+lab_id))

    def test__admin_delete_lab(self):
        superadmin = get_user(self.built_in_ids['superadmin_id'])
        self.login(superadmin.id)
        lab_id = self.built_in_ids['lab_id']
        self.app.post('/_admin_delete_lab',
                      data=json.dumps({'labId': lab_id}),
                      content_type='application/json')
        self.assertFalse(lab_exists(lab_id))

    def test__admin_change_lab_status(self):
        superadmin = get_user(self.built_in_ids['superadmin_id'])
        self.login(superadmin.id)
        lab_id = self.built_in_ids['lab_id']
        new_status = r.rand_lab_status()
        self.app.post('/_admin_change_lab_status/'+new_status,
                      data=json.dumps({'labId': lab_id}),
                      content_type='application/json')
        self.assertEqual(get_lab(lab_id).status, new_status)

    def test_admin_select_lab_for_data(self):
        lab_id = self.built_in_ids['lab_id']
        superadmin = get_user(self.built_in_ids['superadmin_id'])
        self.login(superadmin.id)
        rv = self.app.get('/admin_select_lab_for_data')
        soup = self.decode(rv)
        self.assertIn(get_lab(lab_id).name, soup.tbody.text)

    def test_admin_edit_data(self):
        lab_id = self.built_in_ids['lab_id']
        experiment_name = get_experiment(self.built_in_ids['experiment_id']).name
        superadmin = get_user(self.built_in_ids['superadmin_id'])
        self.login(superadmin.id)
        lab_ids = [lab_id]
        rv = self.app.get('/admin_edit_data/'+json.dumps(lab_ids))
        soup = self.decode(rv)
        self.assertIn(experiment_name, soup.thead.text)

    def test__admin_change_data(self):
        superadmin = get_user(self.built_in_ids['superadmin_id'])
        observation = get_observation(self.built_in_ids['observation_id'])
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
        self.assertEqual(get_observation(observation_modified['observationId']).datum,
                         new_observation_datum)

    def test__admin_delete_data(self):
        observation_id = self.built_in_ids['observation_id']
        superadmin = get_user(self.built_in_ids['superadmin_id'])
        self.login(superadmin.id)
        self.app.post('/_admin_delete_data',
                      data=json.dumps({'observationIdsToBeRemoved': [observation_id]}),
                      content_type='application/json')
        self.assertFalse(observation_exists(observation_id))

    def test_admin_download_data(self):
        lab_id = self.built_in_ids['lab_id']
        observation_datum = get_observation(self.built_in_ids['observation_id']).datum
        superadmin = get_user(self.built_in_ids['superadmin_id'])
        self.login(superadmin.id)
        rv = self.app.get('/_admin_download_data/'+json.dumps([lab_id]))
        # Decode the return value and check the downloadeded text
        text = rv.data.decode('utf-8')
        self.assertIn(observation_datum, text)

    def test_superadmin_create_and_manage_user(self):
        superadmin = get_user(self.built_in_ids['superadmin_id'])
        admin_id = get_user(self.built_in_ids['admin_id']).id
        self.login(superadmin.id)
        # GET
        rv = self.app.get('/superadmin_create_and_manage_user')
        soup = self.decode(rv)
        self.assertIn(admin_id, soup.tbody.text)
        # POST
        user_form = {'username': r.randlength_word(),
                     'name': r.randlength_word(),
                     'role': r.rand_role(),
                     'classIds': []
                     }
        headers = {'Content-type': 'application/x-www-form-urlencoded',
                   'Accept': 'text/plain'}
        rv = self.app.post('/superadmin_create_and_manage_user',
                           data=user_form,
                           headers=headers)
        self.assertEqual(get_user(user_form['username']).id,
                         user_form['username'])

    def test__superadmin_delete_user(self):
        superadmin = get_user(self.built_in_ids['superadmin_id'])
        admin_id = self.built_in_ids['admin_id']
        self.login(superadmin.id)
        self.app.post('/_superadmin_delete_user',
                      data=json.dumps({'userIdToBeRemoved': admin_id}),
                      content_type='application/json')
        self.assertFalse(user_exists(admin_id))

    def test_superadmin_create_and_manage_class(self):
        superadmin = get_user(self.built_in_ids['superadmin_id'])
        self.login(superadmin.id)
        class_name = get_class(self.built_in_ids['class_id']).name
        admin_id = get_user(self.built_in_ids['admin_id']).id
        student_id = get_user(self.built_in_ids['student2_id']).id
        # GET
        rv = self.app.get('/superadmin_create_and_manage_class')
        soup = self.decode(rv)
        self.assertIn(class_name, soup.tbody.text)
        # POST
        class_form = {'professors': [admin_id],
                      'students': [student_id],
                      'className': r.randlength_word(),
                      'classTime': r.rand_classtime()}
        headers = {'Content-type': 'application/x-www-form-urlencoded',
                   'Accept': 'text/plain'}
        rv = self.app.post('/superadmin_create_and_manage_class',
                           data=class_form,
                           headers=headers)
        new_class_id = generate_class_id(class_form['className'],
                                         class_form['classTime'])
        self.assertEqual(get_class(new_class_id).name,
                         class_form['className'])

    def test__superadmin_delete_class(self):
        superadmin = get_user(self.built_in_ids['superadmin_id'])
        class_id = self.built_in_ids['class_id']
        self.login(superadmin.id)
        self.app.post('/_superadmin_delete_class',
                      data=json.dumps({'classIdToBeRemoved': class_id}),
                      content_type='application/json')
        self.assertFalse(class_exists(class_id))

    def test__superadmin_modify_class(self):
        superadmin = get_user(self.built_in_ids['superadmin_id'])
        class_id = self.built_in_ids['class_id']
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
