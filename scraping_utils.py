from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import requests

import time
import re
import pandas as pd
from datetime import datetime
import os

options = Options()
options.add_argument('--headless=new')  # Run without GUI
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--window-size=1920,1080")

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
    
    DL_link = driver.find_element(By.CSS_SELECTOR, "li.download-stats-data-link")
    DL_link.click()
    driver.save_screenshot("debug_html.png")
    DL_URL = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "form.download-stats-data-form")))
    DL_URL = DL_URL.get_attribute("action")
    
    DL_URL = DL_URL.split("?")[0]
    print(DL_URL)
    pkg_name = DL_URL.split("/")[-1]
    
    DL_driver = webdriver.Chrome(options=options)
    # DL_driver.execute_cdp_cmd(
    # "Page.setDownloadBehavior",
    # {
        # "behavior": "allow",
        # "downloadPath": DL_dir
    # }
    # )
    DL_URL = "https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD014624.pub2/media/CDSR/CD014624/supinfo/CD014624-dataPackage.zip"
    DL_driver.get(DL_URL)
    # wait_for_download(DL_dir)
    time.sleep(5)
    DL_driver.save_screenshot("debug_DL_html.png")
    DL_driver.quit()
    
    # selenium_cookies = driver.get_cookies()
    # cookies = {cookie['name']: cookie['value'] for cookie in selenium_cookies}
    # headers = {
    # "User-Agent": driver.execute_script("return navigator.userAgent"),
    # "Referer": driver.current_url,
    # "Accept": "*/*",
    # "Accept-Language": "en-US,en;q=0.5",
    # "Connection": "keep-alive"
        # }


    
    # with requests.get(DL_URL, headers=headers, cookies=cookies, stream=True) as r:
        # print(r.headers.get("Content-Type"))
        # r.raise_for_status()
        # with open(pkg_name, "wb") as f:
            # for chunk in r.iter_content(chunk_size=8192):
                # if chunk:
                    # f.write(chunk)
    # DL_file = requests.get(DL_URL)
    # with open(pkg_name, "wb") as f:
        # f.write(DL_file.content)
    
    time.sleep(2)
    
    
    # gline_ct = get_guideline_text_safe(driver)
    
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
    
# <form class="download-stats-data-form" method="GET" target="_blank" action="/cdsr/doi/10.1002/14651858.CD014624.pub2/media/CDSR/CD014624/supinfo/CD014624-dataPackage.zip?content-disposition=attachment&amp;mime-type=application/octet-stream"> <input type="hidden" name="content-disposition" value="attachment"> <input type="hidden" name="mime-type" value="application/octet-stream"> <p class="print-options-controls"> <input type="checkbox" class="download-stats-data-toc-check-box" aria-label="I agree to these terms and conditions"> <span class="checkbox-label" aria-hidden="true">I agree to these terms and conditions</span> <button class="btn primary download-stats-data pull-right" disabled=""><i class="fa fa-download" aria-hidden="true"></i> Download data</button> </p> </form>