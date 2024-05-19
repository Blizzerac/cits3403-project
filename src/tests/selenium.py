import multiprocessing
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from unittest import TestCase

from app import create_app, db
from app.config import TestConfig

localHost = "http://localhost:5000/"
loginPage = localHost + "login"
signupPage = localHost + "signup"

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

        time.sleep(1) # Give time for server to start

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

        self.server_process.terminate()
        self.driver.close()

    def wait_for_toast(self):
        wait = WebDriverWait(self.driver, 10)
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