from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import requests
from urllib import request

import time
import re
import pandas as pd
from datetime import datetime
import os
import random

options = Options()
options.add_argument('--headless=new')  # Run without GUI
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--window-size=3840,2160")

DL_dir = "C:/Users/PC/Dropbox/various_projects/retraction_watch/MEP_DataAnalyst/shared_code"


def scrape_review_data(url, driver_options=options, DL_dir=DL_dir):
    options.add_experimental_option("prefs", {
    "download.default_directory": DL_dir,
    "download.prompt_for_download": False,
    "directory_upgrade": True
       })
    
    vals = {
        "guideline":0,
        "pub_date":None,
        "downloadable":0,
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
    print(f"... published on {pub_date}. {gline_ct}")
    if len(gline_ct)>0:
        vals["guideline"] = int(gline_ct.split(" ")[2])
    vals["pub_date"] = pub_date
    
    
    
    DL_link = driver.find_element(By.CSS_SELECTOR, "li.download-stats-data-link")
    DL_link.click()
    
    is_locked = ("locked" in DL_link.get_attribute("class")
                or DL_link.find_element(By.TAG_NAME, "a").get_attribute("data-disabled") == "true"
                or "fa-lock" in DL_link.find_element(By.TAG_NAME, "i").get_attribute("class")
                )
    if is_locked:
        print("Data is locked. Let's deal with it later.")
        time.sleep(2+2*random.random())
        driver.quit()
        return vals
    
    
    driver.save_screenshot("debug_html.png")
    DL_URL = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "form.download-stats-data-form")))
    DL_URL = DL_URL.get_attribute("action")
    
    DL_URL = DL_URL.split("?")[0]
    print(DL_URL)
    pkg_name = DL_URL.split("/")[-1]
    
    
    # DL_URL = "https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD014624.pub2/media/CDSR/CD014624/supinfo/CD014624-dataPackage.zip"
    
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}
    req = request.Request(DL_URL, headers=headers)
    # cookie is actually not needed.
    # cookie_dict = {c['name']: c['value'] for c in driver.get_cookies()}
    # for k, v in cookie_dict.items():
        # req.add_header("Cookie", f"{k}={v}")
    with request.urlopen(req) as response, open(f"{DL_dir}/{pkg_name}", "wb") as out_file:
        out_file.write(response.read())
    vals["downloadable"] = 1
    
    
    # gline_ct = get_guideline_text_safe(driver)
    
   
    time.sleep(2+2*random.random()) # to avoid being regarded as a DDoS attack
    driver.quit()
    
    return vals
    