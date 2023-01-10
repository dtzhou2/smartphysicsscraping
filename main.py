import requests
import json
from bs4 import BeautifulSoup
import pandas as pd
import os
import csv
import time
import sys
import urllib.request
from datetime import date
from htmldate import find_date
from dotenv import load_dotenv
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from json import JSONDecoder
from fake_user_agent import user_agent
#from user_agent import random_header

# set url
url = 'https://smart.physics.illinois.edu/'

# call open browser function
chrome_options = Options()
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.headless = False
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)
ua = user_agent()
# userAgent = ua.random()
chrome_options.add_argument(f'user-agent={ua}')
driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
driver.get(url)

# Input Username
username = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//*[@type='email']")))
username.send_keys("dtzhou2@illinois.edu")
driver.find_element(By.XPATH, "//*[@type='submit']").click()

# Input Password
password = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//*[@type='password']")))
password.send_keys('CNvpnJVTFuUn6Qa')
driver.find_element(By.XPATH, "//*[@type='submit']").click()

# Automated scraping of all the physics tests here
downloadLinks = dict()
spreadsheet_index = []

# Scrape information about each page
# 245552

for num in range (245700, 246000, 1):
    try:
        # print(f'https://smart.physics.illinois.edu/Course/ViewProblem?unitItemID={num}&enrollmentID=115235')
        page = driver.get(f'https://smart.physics.illinois.edu/Course/ViewProblem?unitItemID={num}&enrollmentID=115235')
        title = driver.title
        q_number = driver.find_element(By.XPATH, "//*[@class='problem-title ']").text
        try:
            offset = int(q_number[0:2])
        except ValueError:
            offset = 0
        print(num)
        videos = driver.find_elements(By.XPATH, "//iframe")
        videos = driver.find_elements(By.XPATH, "//source")
        questions = driver.find_elements(By.XPATH, "//*[@class='qnum']")
        append = True if title in downloadLinks else False
        # print(videos)
        # print(questions)

        for video, question in zip(videos, questions):
            print('hello')
            video = video.get_attribute("src")
            question = offset+(int(question.text[0:1])-1)
            # print(video)
            # print(question)
            filename = (question, video)
            # print(filename)
            spreadsheet_index.append(question)
            if append:
                downloadLinks[title].append(filename[1])
            else:
                downloadLinks[title] = [filename[1]]
                append = not(append)
    except NoSuchElementException:
        num += 1

def pad_dict_list(dict_list, padel):
    lmax = 0
    for lname in dict_list.keys():
        lmax = max(lmax, len(dict_list[lname]))
    for lname in dict_list.keys():
        ll = len(dict_list[lname])
        if  ll < lmax:
            dict_list[lname] += [padel] * (lmax - ll)
    return dict_list

pad_dict_list(downloadLinks, '0')

# Write finished output to CSV
print(downloadLinks)
df = pd.DataFrame(downloadLinks)
df.to_csv("downloadLinks.csv")

