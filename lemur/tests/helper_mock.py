# This file consists of functions that can generate mock for
# objects in models.py
import sys
sys.path.append('../..')
from unittest.mock import MagicMock
from lemur import models as m
import helper_random as r
from lemur.utility.generate_and_convert import (generate_lab_id,
                                                generate_experiment_id,
                                                generate_observation_id,
                                                generate_class_id)


def generate_lab_mock():
    Lab_mock = MagicMock(spec=m.Lab,
                         name=r.randlength_word(),
                         description=r.randlength_word(),
                         status=r.rand_lab_status,
                         experiments=[])
    return Lab_mock


def generate_experiment_mock():
    Experiment_mock = MagicMock(name=r.randlength_word(),
                                description=r.randlength_word(),
                                order=r.rand_order(),
                                value_type=r.rand_value_type(),
                                value_range=r.rand_value_range(),
                                value_candidates=r.rand_value_candidates())
    return Experiment_mock


def generate_observation_mock():
    Observation_mock = MagicMock(student_name=r.randlength_word(),
                                 datum=r.randlength_word())
    return Observation_mock


def generate_user_mock():
    User_mock = MagicMock(username=r.randlength_word(),
                          name=r.randlength_word(),
                          role_name=r.rand_role())
    return User_mock


def generate_class_mock():
    name = r.randlength_word()
    time = r.rand_classtime()
    class_id = generate_class_id(name, time)
    Class_mock = MagicMock(id=class_id,
                           name=name,
                           time=time)
    return Class_mock