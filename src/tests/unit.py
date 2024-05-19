from unittest import TestCase

from app import create_app, db
from app.models import Users, Posts, Responses, GoldChanges, PostChanges
from app.config import TestConfig

#Unit tests - HAVE NOT MADE CONTROLLERS.py yet
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
    
    '''
    #basic unit test to check user creation
    def test_user_creation(self):
        # Create a test user
        user = Users(username='test_user', email='test@email.com')
        db.session.add(user)
        db.session.commit()

        # Retrieve the user from the database
        retrieved_user = Users.query.filter_by(username='test_user').first()

        # Assert that the user was successfully created and retrieved
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.email, 'test@email.com')
  
    #basic unit test to check if unit tests are actually running 
    #(as of writing they are not)
    def test_is_this_working(self):
        self.assertEqual(True,True)
    
    #unit test to check user login/authetntication 
    def test_user_authentication(self):
        #create test user login details?
        user = Users(username='test_user', email='test@email.com')
        user.set_password('Testpassword123')
        db.session.add(user)
        db.session.commit()

        #get login response
        response = self.client.post('/login', data=dict(
            username='test_user',
            password='Testpassword123'
        ), follow_redirects=True)
        #check if login was successful
        self.assertIn(b'Welcome, test_user!', response.data)
        
        #get login response for invalid credentials
        response = self.client.post('/login', data=dict(
            login='test_user',
            password='wrongpassword'
        ), follow_redirects=True)
        #check if login was not successful
        self.assertIn(b'Invalid username or password', response.data)
  
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
        
        #attempt to signup with an invalid password
        response = self.client.post('/signup', data=dict(
            username='validusername',
            email='test@email.com',
            password='testpassword123'
        ), follow_redirects=True)
        #check if the password must incldue uppercase letter message is given
        self.assertIn(b'Password must include at least one uppercase letter.', response.data)
        
        #attempt to signup with an invalid password
        response = self.client.post('/signup', data=dict(
            username='validusername',
            email='test@email.com',
            password='testpassword123%&$#'
        ), follow_redirects=True)
        #check if the password must not include special characters message is given
        self.assertIn(b'Password can only include letters, numbers, and the following special characters: !, ?, +, -, _.', response.data)
        
        #attempt to signup with an invalid password
        response = self.client.post('/signup', data=dict(
            username='validusername',
            email='test@email.com',
            password='Testpassword'
        ), follow_redirects=True)
        #check if the password must have at least one number message is given
        self.assertIn(b'Password must include at least one number.', response.data)
    
    #unit test for creating a test post
    def test_post_creation(self):
        #login as test user 
        self.clientpost('/login',data=(login='test_user',password='Testpass123'), follow_redirects=True)
        
        #create test post
        response = self.client.post('/create_post', data=dict(
            post_name='Test Post'
            post_description='This is a test post description.'
            post_reward=0
        ), follow_redirects=True)
        
        #check if post creation was successful? not sure if this works cant test currently
        self.assertIn(b'Test Post', response.data)
        self.assertIn(b'This is a test post description.', response.data)
      
    #unit test to test the search function
    def test_search(self):
        post1 = Posts(name='Test Post 1', description='Description for Test Post 1', reward=50)
        post2 = Posts(name='Test Post 2', description='Description for Test Post 2', reward=100)
        db.session.add_all([post1, post2])
        db.session.commit()
        
        #get search response
        response = self.client.post('/search', data=dict(
            post_search_name='Test Post 1'
        ), follow_redirects=True)
        
        #check if search worked correctly (not sure if this is the correct way to test, I cannot run the web app rn)
        self.assertIn(b'Test Post 1', response.data)
        self.assertNotIn(b'Test Post 2', response.data)
        '''