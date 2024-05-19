import multiprocessing
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from unittest import TestCase

from app import create_app, db
from app.config import TestConfig
from app.models import Users

localHost = "http://localhost:5000/"
loginPage = localHost + "login"
signupPage = localHost + "signup"
logoutPage = localHost + "logout"
postPage = localHost + "post"

class SeleniumTestCase(TestCase):
    def setUp(self):
        self.testApp = create_app(TestConfig)
        self.app_context = self.testApp.app_context()
        self.app_context.push()
        db.create_all()
        self.add_sample_users() # Add sample users after creating database

        self.server_process = multiprocessing.Process(target=self.testApp.run)
        self.server_process.start()

        options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(options=options)
        self.driver.get(localHost)

        time.sleep(1) # Give time for server to start

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

        self.server_process.terminate()
        self.driver.close()

    def add_sample_users(self):
        user1 = Users(username='testUser1', email='test1@example.com')
        user1.set_password('Password123')
        user2 = Users(username='testUser2', email='test2@example.com')
        user2.set_password('Password456')
        db.session.add_all([user1, user2])
        db.session.commit()

    def wait_for_toast(self):
        wait = WebDriverWait(self.driver, 3)
        toast = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "toast-body")))
        return toast

    def test_user_signup(self):
        self.driver.get(signupPage)
        signup_element = self.driver.find_element(By.ID, "signup-username")
        signup_element.send_keys("testUser")
        signup_element = self.driver.find_element(By.ID, "signup-email")
        signup_element.send_keys("test@example.com")
        signup_element = self.driver.find_element(By.ID, "signup-password")
        signup_element.send_keys("Password25")
        submit_element = self.driver.find_element(By.ID, "signup-submit-button")
        submit_element.click()

        # Get the toast message:
        toast = self.wait_for_toast()
        # Check the content of the toast message
        self.assertIn("Account created successfully!", toast.text)
    
    def login_user(self, username, password):
        self.driver.get(loginPage)
        login_element = self.driver.find_element(By.ID, "login-username-or-email")
        login_element.send_keys(username)
        password_element = self.driver.find_element(By.ID, "login-password")
        password_element.send_keys(password)
        submit_element = self.driver.find_element(By.ID, "login-submit-button")
        submit_element.click()
        toast = self.wait_for_toast()
        self.assertIn("Logged in successfully!", toast.text)
    
    def post_quest(self, title, desc, reward):
        self.login_user('testUser1', 'Password123')
        self.driver.find_element(By.ID, "post-button").click()

        self.driver.find_element(By.ID, "first-post-input").send_keys(title)
        self.driver.find_element(By.ID, "second-post-input").send_keys(desc)
        self.driver.find_element(By.ID, "third-post-input").send_keys(reward)
        self.driver.find_element(By.ID, "submit-post").click()
        toast = self.wait_for_toast()
        self.assertIn("ReQuest posted successfully!", toast.text)

    def test_user_logout(self):
        # Log in the user
        self.login_user('testUser1', 'Password123')

        self.driver.find_element(By.CLASS_NAME, "dropdown-toggle").click()
        self.driver.find_element(By.ID, "logout").click()
        toast = self.wait_for_toast()
        self.assertIn("Logged out successfully!", toast.text)

    def test_post_quest(self):
        self.post_quest("This is an example post!", "Example description.", 0) # Test default post submission

    # def test_claim(self):
    #     self.post_quest("SAMPLE CLAIM", "sample description", 0)



 


        
