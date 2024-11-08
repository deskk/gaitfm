from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

driver = webdriver.Chrome()  # google chrome
driver.get('https://www.examplewebsite.com/login')  # URL

username_field = driver.find_element(By.ID, 'username_field_id')
password_field = driver.find_element(By.ID, 'password_field_id')

# addbiomechanics login
username_field.send_keys('your_username')
password_field.send_keys('your_password')

# Click the login button
login_button = driver.find_element(By.ID, 'login_button_id')
login_button.click()

# Wait until the dashboard or next page loads
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'dashboard_element_id')))

# csv file for subject information
data = pd.read_csv('subjects.csv')
print(data.head())

'''automate web interactions for each subject'''

def create_dataset(driver, dataset_name):
    driver.get('https://app.addbiomechanics.org/data/b010a08f-1922-cc7c-2fc0-105bcc9dc08c/')
    
    # dataset name
    dataset_field = driver.find_element(By.ID, 'dataset_name_field_id')
    dataset_field.send_keys(dataset_name)
    
    # Submit the form
    create_button = driver.find_element(By.ID, 'create_dataset_button_id')
    create_button.click()
    
    # Wait for the dataset to be created
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'dataset_created_confirmation_id')))

def create_subject_folder(driver, subject_info):
    # Navigate to the subject folder creation page
    driver.get('https://www.examplewebsite.com/create-subject')
    
    # Fill in subject information
    for field_name, value in subject_info.items():
        field = driver.find_element(By.NAME, field_name)
        field.send_keys(value)
    
    # Submit the form
    create_button = driver.find_element(By.ID, 'create_subject_button_id')
    create_button.click()
    
    # Wait for the subject folder to be created
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'subject_created_confirmation_id')))
