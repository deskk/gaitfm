'''
what does it do:
- login to the website with your credentials
- reads csv file you prepared
- create dataset
- create subject subfolders within the created dataset

waiting strategy:
- wait to proceed before click button exist; if offscreen, will still find it continue the script if dataset/subject_id already exist
- might fail in certain cases, because it is hardcoded, can check the below documenation for better waitinng strategies:
https://www.selenium.dev/documentation/webdriver/waits/
'''

import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

class TestTest:
    def setup_method(self, method):
        self.driver = webdriver.Chrome()
        # self.vars = {}
    
    def teardown_method(self, method):
        self.driver.quit() # close after completion
    
    def test_test(self):
        self.driver.get("https://app.addbiomechanics.org/login") # open the website
        self.driver.set_window_size(1560, 1016)
        self.driver.find_element(By.ID, "username").send_keys("") # enter username
        self.driver.find_element(By.ID, "password").send_keys("") # enter password
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click() # click login button
        time.sleep(5)  # wait for n seconds for page to load
        csv_file_path = "selenium/gait_subjectid_lee.csv" # csv for dataset info (subject_id, anthropologic data)
        
        # read csv file
        with open(csv_file_path, newline='') as csvfile:
            csv_reader = csv.reader(csvfile)      
            dataset_name = next(csv_reader)[0]
            dataset_input = self.driver.find_element(By.CSS_SELECTOR, "input")  # Locate the input field for the dataset
            dataset_input.send_keys(dataset_name)
            self.driver.find_element(By.CSS_SELECTOR, ".btn:nth-child(3)").click()  # Click the "Create" button
            
            time.sleep(3) # wait n seconds for screen to load
            self.driver.find_element(By.LINK_TEXT, dataset_name).click() # navigate into created dataset
            time.sleep(3)
            
            # create all subject folders from your csv
            for row in csv_reader:
                subject_id = row[0]
                
                subject_input = self.driver.find_element(By.CSS_SELECTOR, "input:nth-child(1)")  # Locate the input for subject folder
                subject_input.send_keys(subject_id)
                self.driver.find_element(By.CSS_SELECTOR, ".btn:nth-child(3)").click()  # Click the 'create' button

                time.sleep(3)