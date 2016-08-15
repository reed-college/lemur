# This file consists of functions that can generate mock for
# objects in models.py
import sys
sys.path.append('../..')
from unittest.mock import MagicMock
from lemur import models as m
import helper_random as r
from lemur.utility_generate_and_convert import (generate_lab_id,
                                                generate_experiment_id,
                                                generate_observation_id,
                                                generate_class_id)


def generate_lab_mock():
    LabMock = MagicMock(spec=m.Lab,
                        name=r.randlength_word(),
                        description=r.randlength_word(),
                        status=r.rand_lab_status,
                        experiments=[])
    return LabMock


def generate_experiment_mock():
    ExperimentMock = MagicMock(name=r.randlength_word(),
                               description=r.randlength_word(),
                               order=r.rand_order(),
                               value_type=r.rand_value_type(),
                               value_range=r.rand_value_range(),
                               value_candidates=r.rand_value_candidates())
    return ExperimentMock


def generate_observation_mock():
    ObservationMock = MagicMock(student_name=r.randlength_word(),
                                datum=r.randlength_word())
    return ObservationMock


def generate_user_mock():
    UserMock = MagicMock(username=r.randlength_word(),
                         name=r.randlength_word(),
                         role_name=r.rand_role())
    return UserMock


def generate_class_mock():
    name = r.randlength_word()
    time = r.rand_classtime()
    class_id = generate_class_id(name, time)
    ClassMock = MagicMock(id=class_id,
                          name=name,
                          time=time)
    return ClassMock
