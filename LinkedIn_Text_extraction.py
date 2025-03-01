from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

service = Service("geckodriver.exe")
driver = webdriver.Firefox(service=service)

try:
    driver.get("https://duckduckgo.com")
    
    # Wait for and interact with search box
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "q"))
    )
    search_box.send_keys("Chris Montes linkedin" + Keys.RETURN)
    
    # Wait for results and remove interfering elements
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "article[data-nrn='result']"))
    )
    
    # Remove any overlays or badges
    driver.execute_script(
        """document.querySelectorAll('.badge-link__wrap, .js-sidebar-ads')
           .forEach(element => element.remove());"""
    )
    
    # Wait for and click the first main result using more precise selector
    first_result = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((
            By.CSS_SELECTOR, 
            "article[data-nrn='result'] a[data-testid='result-title-a']:first-child"
        ))
    )
    
    # Scroll and click using normal click (more reliable when element is visible)
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", first_result)
    time.sleep(0.5)
    first_result.click()
    
    # Wait for LinkedIn page to load
    WebDriverWait(driver, 10).until(
        EC.title_contains("LinkedIn")
    )
    
    print("Successfully opened LinkedIn profile:", driver.title)
    time.sleep(560)

finally:
    driver.quit()