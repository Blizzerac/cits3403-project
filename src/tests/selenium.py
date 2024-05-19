import multiprocessing
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from unittest import TestCase

from app import create_app, db
from app.config import TestConfig

localHost = "http://localhost:5000/"

class SeleniumTestCase(TestCase):
    def setUp(self):
        self.testApp = create_app(TestConfig)
        self.app_context = self.testApp.app_context()
        self.app_context.push()
        db.create_all()

        self.server_process = multiprocessing.Process(target=self.testApp.run)
        self.server_process.start()

        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(options=options)
        self.driver.get(localHost)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

        self.server_process.terminate()
        self.driver.close()

    def test_user_signup(self):
        signup_element = self.driver.find_element(By.ID, "signup-username")
        signup_element.send_keys("testUser")
        signup_element = self.driver.find_element(By.ID, "signup-email")
        signup_element.send_keys("test@example.com")
        signup_element = self.driver.find_element(By.ID, "signup-password")
        signup_element.send_keys("Password25")
        submit_element = self.driver.find_element(By.ID, "login-submit-button")
        submit_element.click()
        messages = self.driver.find_element(By.CLASS_NAME, "toast-body")
        self.assertEqual(len(messages), 1, "Expected success message on correct signup.")
        self.assertEqual(messages[0].text, "Logged in successfully!")