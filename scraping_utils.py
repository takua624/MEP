from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re
import pandas as pd
from datetime import datetime

options = Options()
options.add_argument('--headless')  # Run without GUI
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--window-size=1920,1080")

def scrape_review_data(url, driver_options=options):
    vals = {
        "guideline":0,
        "pub_date":None,
    }
    page_retrieved = False
    retry = 0
    while not page_retrieved:
        driver = webdriver.Chrome(options=driver_options)
        driver.get(url)
        title_element = re.search(r"{database.*?}}",driver.page_source)
        page_retrieved = title_element!=None
        if title_element == None:
            print(f"... Title element not found, retry")
            retry += 1
            time.sleep(3)
            driver.quit()
            continue
    try:
        latest_ver = driver.find_element(By.CSS_SELECTOR, "div.version-button a")
        new_url = latest_ver.get_attribute("href")
        print("... There is a newer version, accessing...")
        print(f"... Latest URL: {new_url}")
        latest_ver.click()
    except:
        print("... We have the latest version.")
    
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[title="Guidelines"]')))

    gline_ct = driver.find_element(By.CSS_SELECTOR, 'a[title="Guidelines"]').text
    pub_date = driver.find_element(By.CSS_SELECTOR, 'span.publish-date').text
    pub_date = datetime.strptime(pub_date.split(": ")[-1], "%d %B %Y").date()
    # gline_ct = get_guideline_text_safe(driver)
    driver.save_screenshot("debug_html.png")
    print(f"... published on {pub_date}. {gline_ct}")
    if len(gline_ct)>0:
        vals["guideline"] = int(gline_ct.split(" ")[2])
    vals["pub_date"] = pub_date
    # print(gline_ct.text)
    # driver.delete_all_cookies()
    # driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
    # driver.get("about:blank")
    driver.quit()
    time.sleep(3) # to avoid being regarded as a DDoS attack
    return vals