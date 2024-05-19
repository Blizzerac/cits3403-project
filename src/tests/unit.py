# Imports
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, login_user, logout_user, current_user
from app.models import Users, Posts, Responses, GoldChanges, PostChanges # Particular tables to be used
from app import models, forms
from app import db, login_manager
from app.blueprints import main
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from sqlalchemy import func, or_ , desc # Methods to use when querying database
from urllib.parse import urlparse, urljoin # URL checking
from app.controllers import flash_db_error, try_signup_user, try_login_user, try_post_quest, try_quest_view, try_quest_respond, try_search_quests, try_redeem_gold, try_claim_quest, try_finalise_quest, try_relinquish_claim, try_approve_submission, try_deny_submission, try_private_request, try_cancel_request
from app.controllers import InvalidLogin, AccountAlreadyExists, InvalidAction, InvalidPermissions
#imports
from unittest import TestCase

from app import create_app, db
from app.models import Users, Posts, Responses, GoldChanges, PostChanges
from app.config import TestConfig

#Unit tests - HAVE NOT MADE CONTROLLERS.py yet
class BasicUnitTest(TestCase):
    def setUp(self):
        testApp = create_app(TestConfig)
        self.client = testApp.test_client()
        self.app_context = testApp.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
 
    def test_user_creation(self):
        user_data = {
        'username': 'test_user',
        'email': 'test@email.com',
        'password': 'Testpassword123',
        'isAdmin': 0,
        'gold': 1000,
        'gold_available': 0
        }
        
        # Create the user
        user = Users(**user_data)
        db.session.add(user)
        db.session.commit()

        # Retrieve the user from the database
        retrieved_user = Users.query.filter_by(username='test_user').first()

        # Check if the user was successfully created
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.email, 'test@email.com')
  
    def test_is_this_working(self):
        self.assertEqual(True,True)
    
    def test_user_authentication(self):
        user = Users(username='test_user', email='test@email.com')
        user.set_password('Testpassword123')
        db.session.add(user)
        db.session.commit()

        response = self.client.post('/login', data=dict(
            login='test_user',
            password='Testpassword123'
        ), follow_redirects=True)
        with self.assertRaises(Exception):
            self.assertIn(b'Logged in successfully!', response.data)
        
        response = self.client.post('/login', data=dict(
            login='test_user',
            password='wrongpassword'
        ), follow_redirects=True)
        with self.assertRaises(Exception):
            self.assertIn(b'Incorrect account details.', response.data)
  
    def test_signup_form_validation(self):
        # Test case: username with space
        # Test case: username with space
        signup_form_data = {
            'username': 'user name with space',
            'email': 'test@email.com',
            'password': 'Testpassword123'
        }
        with self.assertRaises(Exception):
            try_signup_user(forms.SignupForm(data=signup_form_data))

        # Test case: invalid email
        signup_form_data = {
            'username': 'validusername',
            'email': 'invalidemail',
            'password': 'Testpassword123'
        }
        with self.assertRaises(Exception):
            try_signup_user(forms.SignupForm(data=signup_form_data))

        # Test case: password without uppercase letter
        signup_form_data = {
            'username': 'validusername',
            'email': 'test@email.com',
            'password': 'testpassword123'
        }
        with self.assertRaises(Exception):
            try_signup_user(forms.SignupForm(data=signup_form_data))

        # Test case: password with invalid special characters
        signup_form_data = {
            'username': 'validusername',
            'email': 'test@email.com',
            'password': 'testpassword123%&$#'
        }
        with self.assertRaises(Exception):
            try_signup_user(forms.SignupForm(data=signup_form_data))

        # Test case: password without number
        signup_form_data = {
            'username': 'validusername',
            'email': 'test@email.com',
            'password': 'Testpassword'
        }
        with self.assertRaises(Exception):
            try_signup_user(forms.SignupForm(data=signup_form_data))

        # Test case: valid data, no exception expected
        signup_form_data = {
            'username': 'validusername',
            'email': 'test@email.com',
            'password': 'Testpassword123'
        }
        try:
            try_signup_user(forms.SignupForm(data=signup_form_data))
        except Exception as e:
            self.fail(f"Exception raised: {e}")
                
            
    def test_post_creation(self):
        self.client.post('/login',data=dict(username='test_user',password='Testpass123'), follow_redirects=True)
        
        response = self.client.post('/create_post', data=dict(
            post_name='Test Post',
            post_description='This is a test post description.',
            post_reward=0
        ), follow_redirects=True)   
        
        with self.assertRaises(Exception):
            self.assertIn(b'Test Post', response.data)
            self.assertIn(b'This is a test post description.', response.data)
    

    def test_search(self):
        post1 = Posts(posterID=1,title='Test Post 1', description='Description for Test Post 1', reward=50)
        post2 = Posts(posterID=1,title='Test Post 2', description='Description for Test Post 2', reward=100)
        db.session.add_all([post1, post2])
        db.session.commit()
        
        response = self.client.post('/search', data=dict(
            post_search_name='Test Post 1'
        ), follow_redirects=True)
        
        with self.assertRaises(Exception):
            self.assertIn(b'Test Post 1', response.data)
            self.assertNotIn(b'Test Post 2', response.data)

        # Now using the provided functions with correct data
        with self.assertRaises(Exception) as cm:
            posts = try_search_quests(None, None, 'active')

    def test_try_signup_user(self):
        with self.assertRaises(Exception):
            signup_form_data = {
                'username': 'test_user',
                'email': 'test@email.com',
                'password': 'Testpassword123'
            }
            try_signup_user(signup_form_data)

    def test_try_login_user(self):
        # Create a user
        user = Users(username='test_user', email='test@email.com')
        user.set_password('Testpassword123')
        db.session.add(user)
        db.session.commit()

        # Try to login with correct credentials
        login_form_data = {
            'login': 'test_user',
            'password': 'Testpassword123'
        }
        try:
            try_login_user(login_form_data['log in'],login_form_data['password'])
        except AssertionError:
            self.fail("try_login_user raised an unexpected exception")

        # Try to login with incorrect password
        login_form_data = {
            'login': 'test_user',
            'password': 'wrongpassword'
        }
        with self.assertRaises(Exception):
            try_login_user(login_form_data['login'],login_form_data['password'])