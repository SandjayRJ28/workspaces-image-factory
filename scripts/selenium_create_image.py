from os import environ as env
import boto3
import time
import string
import json
from retry import retry
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


LOGIN_URL = env['LOGIN_URL']
USERNAME = env['USER_NAME']
PASSWORD = env['PASSWORD']


def find_id_of_workspace():
    cloudformation = boto3.resource('cloudformation')
    stack = cloudformation.Stack('WorkspaceBuilder')
    stack_resource = stack.Resource('workspace1').physical_resource_id
    return stack_resource


def login_page(driver):
    # login_page method
    driver.get(LOGIN_URL)
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, 'username')))

    user = driver.find_element_by_id('username')
    driver.implicitly_wait(20)
    user.send_keys(USERNAME)
    driver.implicitly_wait(20)

    password = driver.find_element_by_id('password')
    driver.implicitly_wait(20)
    password.send_keys(PASSWORD)

    driver.implicitly_wait(20)
    driver.find_element_by_id("signin_button").click()


def navigate_to_workspaces(driver):
    # workspaces_page method
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, 'nav-servicesMenu')))
    driver.find_element_by_id("nav-servicesMenu").click()
    driver.implicitly_wait(5)
    driver.find_element_by_link_text("WorkSpaces").click()


def navigate_to_images(driver):
    # navigate to bundles page
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.LINK_TEXT, 'Images')))
    driver.find_element_by_link_text("Images").click()


def check_image_status(driver, image_name):
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.NILBMCB-r-o table tbody:nth-child(3) tr')))
    rows = driver.find_elements_by_css_selector("div.NILBMCB-r-o table tbody:nth-child(3) tr")
    driver.implicitly_wait(10)

    for row in rows:
        cell = row.find_element_by_css_selector("td:nth-child(3)")
        if cell.text == image_name:
            status = row.find_element_by_css_selector("td.NILBMCB-w-h.NILBMCB-w-j.NILBMCB-w-w")
            print(status.text)
            if status.text == "Available":
                return True
            else:
                return False

    return None


def create_bundle(driver, image_name):
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.NILBMCB-r-o table tbody:nth-child(3)')))
    rows = driver.find_elements_by_css_selector("div.NILBMCB-r-o table tbody:nth-child(3) tr")
    driver.implicitly_wait(10)

    for row in rows:
        cell = row.find_element_by_css_selector("td:nth-child(3)")
        if cell.text == image_name:
            check = row.find_element_by_css_selector("td")
            ActionChains(driver).move_to_element(check).click(check).perform()

    driver.find_element_by_css_selector("div.NILBMCB-r-a div.NILBMCB-r-x button").click()
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, 'createBundleButton')))
    driver.find_element_by_id("createBundleButton").click()
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.NILBMCB-j-r div div div:nth-child(4) table tbody tr:nth-child(1) td:nth-child(3) div.NILBMCB-Nb-h.NILBMCB-Nb-e input')))

    imageName = driver.find_element_by_css_selector("div.NILBMCB-j-r div div div:nth-child(4) table tbody tr:nth-child(1) td:nth-child(3) div.NILBMCB-Nb-h.NILBMCB-Nb-e input")
    imageName.send_keys('test-selenium-bundle-trader')
    driver.implicitly_wait(10)
    description = driver.find_element_by_css_selector("div.NILBMCB-j-r div div div:nth-child(5) table tbody tr:nth-child(1) td:nth-child(3) div.NILBMCB-Nb-h.NILBMCB-Nb-e input")
    description.send_keys('Test Trader Bundle')
    driver.implicitly_wait(10)
    select_fr = Select(driver.find_element_by_id("baseWorkspaceBundleListBoxId"))
    select_fr.select_by_value('VALUE')
    driver.implicitly_wait(10)
    volume_size = driver.find_element_by_css_selector("div.NILBMCB-j-r div div div:nth-child(8) table tbody tr:nth-child(1) td:nth-child(3) div.NILBMCB-Nb-h.NILBMCB-Nb-e input")
    volume_size.send_keys('10')
    driver.implicitly_wait(10)
    driver.find_element_by_id("createBundleConfirmButtonId").click()




def create_image(driver, workspace_id, image_name, image_description):
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.NILBMCB-r-o table tbody:nth-child(3) tr')))
    rows = driver.find_elements_by_css_selector("div.NILBMCB-r-o table tbody:nth-child(3) tr")
    driver.implicitly_wait(10)

    for row in rows:
        cell = row.find_element_by_css_selector("td:nth-child(3)")

        if cell.text == workspace_id:
            check = row.find_element_by_css_selector("td")
            ActionChains(driver).move_to_element(check).click(check).perform()
        
    driver.find_element_by_id("workspacesActionButton").click()
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, 'createImageButton')))
    driver.find_element_by_id("createImageButton").click()
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, 'createImageConfirmButton')))
    driver.find_element_by_id("createImageConfirmButton").click()
    driver.implicitly_wait(5)

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.NILBMCB-j-r div div div:nth-child(3) div:nth-child(3) table tbody tr:nth-child(1) td:nth-child(3) div.NILBMCB-Nb-h.NILBMCB-Nb-e input')))
    imageName = driver.find_element_by_css_selector("div.NILBMCB-j-r div div div:nth-child(3) div:nth-child(3) table tbody tr:nth-child(1) td:nth-child(3) div.NILBMCB-Nb-h.NILBMCB-Nb-e input")
    imageName.send_keys(image_name)
    driver.implicitly_wait(10)
    description = driver.find_element_by_css_selector("div.NILBMCB-j-r div div div:nth-child(3) div:nth-child(4) table tbody tr:nth-child(1) td:nth-child(3) div.NILBMCB-Nb-h.NILBMCB-Nb-e input")
    description.send_keys(image_description)
    driver.implicitly_wait(10)
    driver.find_element_by_id("createImageConfirmButton").click()


def wait_for_image(driver, image_name):
    condition = False
    while condition == False:
        condition = check_image_status(driver, image_name)
        print(condition)
        if condition == False:
            print("Waiting")
            time.sleep(60*5)

    return


def main():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("--disable-dev-shm-usage")
    # set the window size
    # options.add_argument('window-size=1200x600')

    # initialize the driver
    driver = webdriver.Chrome(chrome_options=options)
    driver.maximize_window()

    workspace_id = find_id_of_workspace()
    image_name = 'test-selenium-image'
    image_description = 'Test Description'

    driver.implicitly_wait(20)
    login_page(driver)
    driver.implicitly_wait(20)
    navigate_to_workspaces(driver)
    driver.implicitly_wait(20)
    navigate_to_images(driver)
    status = check_image_status(driver, image_name)
    if status is None:
        navigate_to_workspaces(driver)
        create_image(driver, workspace_id, image_name, image_description)
        driver.implicitly_wait(20)
        navigate_to_images(driver)
        wait_for_image(driver, image_name)
        create_bundle(driver, image_name)
    elif status == False:
        wait_for_image(driver, image_name)
        create_bundle(driver, image_name)
    else:
        create_bundle(driver, image_name)


if __name__ == "__main__":
    main()
