from unittest import TestCase

from lemur import app, db
from lemur import models as m
from db_populate import populate_db

ds = db.session


class LemurBaseCase(TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.ds = db.session
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
