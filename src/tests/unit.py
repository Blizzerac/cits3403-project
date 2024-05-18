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
  
    #basic unit test to check user creation
    def test_user_creation(self):
        # Create a test user
        user = User(username='test_user', email='test@example.com')
        db.session.add(user)
        db.session.commit()

        # Retrieve the user from the database
        retrieved_user = User.query.filter_by(username='test_user').first()

        # Assert that the user was successfully created and retrieved
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.email, 'test@example.com')
  
    #basic unit test to check if unit tests are actually running 
    #(as of writing they are not)
    def test_is_this_working(self):
        self.assertEqual(True,True)
  
    #unit test to check the signup form validation
    def test_signup_form_validation(self):
        #attempt to sign up with an invalid username
        response = self.client.post('/signup', data=dict(
            username='user name with space',
            email='test@email.com',
            password='Testpassword123'
        ), follow_redirects=True)
        #checks if the no spaces message is given
        self.assertIn(b'The username must not contain spaces.', response.data)
          
        #attempt to signup with an invalid email address
        response = self.client.post('/signup', data=dict(
            username='validusername',
            email='invalidemail',
            password='Testpassword123'
        ), follow_redirects=True)
        #checks if invalid email address message is given (unsure if this is the correct error message)
        self.assertIn(b'Invalid email address.', response.data)
        
        response = self.client.post('/signup', data=dict(
            username='validusername',
            email='test@email.com',
            password='testpassword123'
        ), follow_redirects=True)
        self.assertIn(b'Password must include at least one uppercase letter.', response.data)