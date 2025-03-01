from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

# Initialize Firefox WebDriver with headless mode
options = Options()
options.headless = True
service = Service('geckodriver.exe')
driver = webdriver.Firefox(service=service, options=options)

try:
    # Open Google Images
    driver.get('https://images.google.com/')

    # Wait for the cam button to be clickable and click it
    cam_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Search by image' and @role='button']"))
    )
    cam_button.click()

    # Directly interact with the file input element
    file_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
    )
    file_input.send_keys(os.path.join(os.getcwd(), "main_pic.jpg"))

    # Wait for the upload to complete
    time.sleep(10)

    # Locate the search bar using the provided XPath
    search_bar = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[@id='APjFqb']"))
    )

    # Type "LinkedIn" into the search bar and submit the search
    search_bar.clear()
    search_bar.send_keys("LinkedIn")
    search_bar.send_keys(Keys.RETURN)

    # Wait for a few seconds to see the results
    time.sleep(10)

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the browser
    driver.quit()
