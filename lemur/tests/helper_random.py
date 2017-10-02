# This file consists of the functions that generate random values or
# create objects in db for testing
import sys
sys.path.append('../..')
# Libraries
# Standard library
from random import choice, randint, shuffle
from string import ascii_lowercase, ascii_uppercase, digits

# Local
from lemur import models as m
from lemur.utility_generate_and_convert import (generate_lab_id,
                                                generate_experiment_id,
                                                generate_observation_id,
                                                generate_class_id)
from lemur.utility_find_and_get import (get_power,
                                        get_role)


# --- Some helper functions used to add randomness into our tests ---
# generate a random combination of letters(both upper and lower) and digits
# with a random length within the interval
def randlength_word(min_len=5, max_len=10):
    return ''.join(choice(ascii_lowercase + ascii_uppercase +
                          digits) for i in range(randint(min_len, max_len)))


# generate a random lab status
def rand_lab_status(status=('Activated', 'Unactivated', 'Downloadable')):
    return status[randint(0, len(status)-1)]


# generate a random experiment order
def rand_order(min=1, max=100):
    return randint(min, max)


# generate a random value type
def rand_value_type(value_types=('Text', 'Number')):
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
def rand_classtime(classtime_list=['FALL2016', 'SPRING2017', 'FALL2017']):
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
    return [get_power(p) for p in
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


def rand_observations_group_by_experiment_name():
    observations_group_by_experiment_name = []
    lab_id = rand_lab_id()
    student_num = rand_round()
    student_name_list = [randlength_word() for _ in range(student_num)]
    for i in range(rand_round()):
        experiment_name = randlength_word()
        experiment_id = generate_experiment_id(lab_id, experiment_name)
        experiment = {'experiment_id': experiment_id, 'experiment_name': experiment_name,'observations':[]}
        for i in range(student_num):
            student_name = student_name_list[i]
            observation_id = generate_observation_id(experiment_id, student_name)
            observation_datum = randlength_word()
            observation = {'observation_id': observation_id,
                           'student_name': student_name,
                           'observation_data': observation_datum,
                           'lab_id': lab_id,
                           'experiment_id': experiment_id}
            experiment['observations'].append(observation)

        observations_group_by_experiment_name.append(experiment)
    return observations_group_by_experiment_name


# - A list of helper functions for creating a random object in database -
def create_class(ds):
    name = randlength_word()
    time = randlength_word()
    class_id = generate_class_id(name, time)
    while ds.query(m.Class).filter(m.Class.id == class_id).count() != 0:
        name = randlength_word()
        time = randlength_word()
        class_id = generate_class_id(name, time)

    the_class = m.Class(id=class_id, name=name, time=time)
    ds.add(the_class)
    ds.commit()
    class_query = ds.query(m.Class).filter(m.Class.id == class_id).first()
    return class_query


def create_lab(ds):
    the_class = create_class(ds)
    name = randlength_word()
    class_id = the_class.id
    description = randlength_word()
    status = 'Activated'
    lab_id = generate_lab_id(name, class_id)
    while ds.query(m.Lab).filter(m.Lab.id == lab_id).count() != 0:
        class_id = rand_classid()
        description = randlength_word()
        lab_id = generate_lab_id(name, class_id)

    lab = m.Lab(id=lab_id, name=name, the_class=the_class,
                description=description, status=status)
    ds.add(lab)
    ds.commit()
    lab_query = ds.query(m.Lab).filter(m.Lab.id == lab_id).first()
    return lab_query


def create_experiment(ds, lab_id=rand_lab_id()):
    name = randlength_word()
    description = randlength_word()
    order = rand_order()
    value_type = rand_value_type()
    value_range = rand_value_range()
    value_candidates = rand_value_candidates()
    experiment_id = generate_experiment_id(lab_id, name)
    while ds.query(m.Experiment).filter(m.Experiment.id == experiment_id).count() != 0:
        name = randlength_word()
        lab_id = rand_lab_id()
        experiment_id = generate_experiment_id(lab_id, name)

    experiment = m.Experiment(id=experiment_id, name=name,
                              description=description, order=order,
                              value_type=value_type,
                              value_range=value_range,
                              value_candidates=value_candidates)
    ds.add(experiment)
    ds.commit()
    experiment_query = ds.query(m.Experiment).filter(m.Experiment.id == experiment_id).first()
    return experiment_query


def create_observation(ds, experiment_id=rand_experiment_id()):
    student_name = randlength_word()
    datum = randlength_word()
    observation_id = generate_observation_id(experiment_id, student_name)
    while ds.query(m.Observation).filter(m.Observation.id == observation_id).count() != 0:
        student_name = randlength_word()
        experiment_id = rand_experiment_id()
        observation_id = generate_observation_id(experiment_id,
                                                 student_name)

    observation = m.Observation(id=observation_id,
                                student_name=student_name,
                                datum=datum)

    ds.add(observation)
    ds.commit()
    observation_query = ds.query(m.Observation).filter(m.Observation.id == observation_id).first()
    return observation_query


def create_user(ds):
    username = randlength_word()
    while ds.query(m.User).filter(m.User.id == username).count() != 0:
        username = randlength_word()

    name = randlength_word()
    user = m.User(id=username,
                  name=name)
    ds.add(user)
    ds.commit()
    user_query = ds.query(m.User).filter(m.User.id == username).first()
    return user_query


def create_role(ds):
    name = randlength_word()
    while ds.query(m.Role).filter(m.Role.name == name).count() != 0:
        name = randlength_word()

    powers = rand_powers()
    role = m.Role(name=name, powers=powers)
    ds.add(role)
    ds.commit()
    role_query = get_role(name)
    return role_query


def create_power(ds):
    id = randlength_word()
    while ds.query(m.Power).filter(m.Power.id == id).count() != 0:
        id = randlength_word()

    power = m.Power(id=id)
    ds.add(power)
    ds.commit()
    power_query = get_power(id)
    return power_query
