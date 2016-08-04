# This file is used to populate the database(for real use)
from lemur import utility as u
from lemur import models as m
from lemur import (db)
ds = db.session


def populate_db():
    # Create a real lab example in the database. There is a exactly
    # the same corresponding one in the old data collector)
    def create_real_lab():
        # Create a real lab
        real_lab_name = '2Cortisol'
        real_lab_id = '2Cortisol:BIOL101_FALL2016'
        if not u.lab_exists(real_lab_id):
            real_lab = m.Lab(id=real_lab_id, name=real_lab_name,
                             the_class=u.get_class(class_id),
                             description=('Enter your lab instructor (C or N),'
                                          ' lab day (M,T,W,R,F), temperature'
                                          ' treatment (ICE or RT), and'
                                          ' psychological treatment (Critical'
                                          ' or Helpful). Enter PRE, POST, and'
                                          ' POST20 cortisol results in µg/dL.'
                                          ' DO NOT type in units.'),
                             status='Activated',
                             users=[u.get_user(superadmin_id)])
            ds.add(real_lab)

        experiment1_name = 'Lab Instructor'
        experiment1_id = u.generate_experiment_id(real_lab_id, experiment1_name)
        if not u.experiment_exists(experiment1_id):
            experiment = m.Experiment(id=experiment1_id, name=experiment1_name,
                                      description=('Enter C for Carey or N for'
                                                   ' Ned. Use only 1 letter.'),
                                      order=1, value_type='Text',
                                      value_candidates='C,N',
                                      value_range='',
                                      lab=u.get_lab(real_lab_id))
            ds.add(experiment)

        experiment2_name = 'Lab day?'
        experiment2_id = u.generate_experiment_id(real_lab_id, experiment2_name)
        if not u.experiment_exists(experiment2_id):
            experiment = m.Experiment(id=experiment2_id, name=experiment2_name,
                                      description=('Enter M for Monday, T for'
                                                   ' Tuesday, W for Wednesday,'
                                                   ' R for Thursday, or F for'
                                                   ' Friday.\nUse only 1'
                                                   ' letter.'),
                                      order=2, value_type='Text',
                                      value_candidates='M,T,W,R,F',
                                      value_range='',
                                      lab=u.get_lab(real_lab_id))
            ds.add(experiment)
        experiment3_name = 'TemperatureTreatment'
        experiment3_id = u.generate_experiment_id(real_lab_id, experiment3_name)
        if not u.experiment_exists(experiment3_id):
            experiment = m.Experiment(id=experiment3_id, name=experiment3_name,
                                      description=('Enter ICE for ice water or'
                                                   ' RT for room temperature'
                                                   ' water.'),
                                      order=3, value_type='Text',
                                      value_candidates='ICE,RT',
                                      value_range='',
                                      lab=u.get_lab(real_lab_id))
            ds.add(experiment)

        experiment4_name = 'Psychol Treatment'
        experiment4_id = u.generate_experiment_id(real_lab_id, experiment4_name)
        if not u.experiment_exists(experiment4_id):
            experiment = m.Experiment(id=experiment4_id, name=experiment4_name,
                                      description=('Enter Critical for'
                                                   ' counting down with a'
                                                   ' critical partner or'
                                                   ' Helpful for counting up'
                                                   ' with a helpful partner.'),
                                      order=4, value_type='Text',
                                      value_candidates='Critical,Helpful',
                                      value_range='',
                                      lab=u.get_lab(real_lab_id))
            ds.add(experiment)

        experiment5_name = 'PRE treatment cortisol concentration'
        experiment5_id = u.generate_experiment_id(real_lab_id, experiment5_name)
        if not u.experiment_exists(experiment5_id):
            experiment = m.Experiment(id=experiment5_id, name=experiment5_name,
                                      description=('Enter the PRE treatment'
                                                   ' cortisol concentration'
                                                   ' that you read off of the'
                                                   ' standard curve (not from'
                                                   ' the paper tape).DO NOT'
                                                   ' type in the units. If'
                                                   ' your numbers have 3'
                                                   ' decimal places, you may'
                                                   ' be erroneously entering'
                                                   ' your OD (Optical Density'
                                                   ', from the paper tape)'
                                                   ' instead of your cortisol'
                                                   ' value.'),
                                      order=5, value_type='Number',
                                      value_candidates='',
                                      value_range='',
                                      lab=u.get_lab(real_lab_id))
            ds.add(experiment)

        experiment6_name = 'POST treatment cortisol concentration'
        experiment6_id = u.generate_experiment_id(real_lab_id, experiment6_name)
        if not u.experiment_exists(experiment6_id):
            experiment = m.Experiment(id=experiment6_id, name=experiment6_name,
                                      description=('Enter the POST treatment'
                                                   ' cortisol concentration'
                                                   ' that you read off of the'
                                                   ' curve (not from the paper'
                                                   ' standard tape).DO NOT'
                                                   ' type in the units. If'
                                                   ' your numbers have 3'
                                                   ' decimal places, you may'
                                                   ' be erroneously entering'
                                                   ' your OD (Optical Density,'
                                                   ' from the paper tape)'
                                                   ' instead of your cortisol'
                                                   ' value.'),
                                      order=6, value_type='Number',
                                      value_candidates='',
                                      value_range='',
                                      lab=u.get_lab(real_lab_id))
            ds.add(experiment)

        experiment7_name = 'POST20 treatment cortisol concentration'
        experiment7_id = u.generate_experiment_id(real_lab_id, experiment7_name)
        if not u.experiment_exists(experiment7_id):
            experiment = m.Experiment(id=experiment7_id, name=experiment7_name,
                                      description=('Enter the POST20 treatment'
                                                   ' cortisol concentration'
                                                   ' that you read off of the'
                                                   ' standard curve (not from'
                                                   ' the paper tape).DO NOT'
                                                   ' type in the units. If'
                                                   ' your numbers have 3'
                                                   ' decimal places, you may'
                                                   ' be erroneously entering'
                                                   ' your OD (Optical Density,'
                                                   ' from the paper tape)'
                                                   ' instead of your'
                                                   ' cortisol value.'),
                                      order=7, value_type='Number',
                                      value_candidates='',
                                      value_range='',
                                      lab=u.get_lab(real_lab_id))
            ds.add(experiment)
        ds.commit()

    superadmin_id = 'boothr'
    class_id = 'BIOL101_FALL2016'
    m.Role.insert_roles()
    # Create a SuperAdmin, a Admin, a Student
    if not u.user_exists(superadmin_id):
        u = m.User(id='boothr',
                   name='Carey Booth',
                   role=u.get_role('SuperAdmin'))
        ds.add(u)
    # Create a class
    if not u.class_exists(class_id):
        c = m.Class(id=class_id, name='BIOL101', time='FALL2016',
                    users=[u.get_user(superadmin_id)])
        ds.add(c)
    ds.commit()
    create_real_lab()


if __name__ == "__main__":
    populate_db()
