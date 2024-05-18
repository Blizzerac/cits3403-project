from unittest import TestCase

from app import create_app, db
from app.config import TestConfig

class BasicUnitTest(TestCase):
  def setUp(self):
    testApp = create_app(TestConfig)
    self.app_context = testApp.app_context()
    self.app_context.push()
    db.create_all()
    # add_test_data_to_db()

  def tearDown(self):
    db.session.remove()
    db.drop_all()
    self.app_context.pop()
    