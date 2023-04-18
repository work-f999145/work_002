import requests
from bs4 import BeautifulSoup as BS
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By 
import json
from pathlib import Path
from pprint import pprint
import copy
import threading

from multiprocessing import Pool
from multiprocessing import cpu_count
from time import sleep as time_sleep

proxy_sel = '45.81.76.252:8000'

def run_parser(func, lst):
    with Pool(cpu_count()) as pool:
        pool.map(func=func, iterable=lst)
        


def run_driver(link):
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument(f'--proxy-server={proxy_sel}')
    driver = uc.Chrome(options=chrome_options)
    driver.get(link)
    time_sleep(10)
    element = driver.find_element(by=By.CLASS_NAME, value='address-container__adress-icon-container')
    element.click()
    time_sleep(2)

    element = driver.find_element(by=By.CLASS_NAME, value='store-picker-city__label')
    element.click()
    time_sleep(3)

    elements = driver.find_elements(by=By.CSS_SELECTOR, value="span.cities-list-item__name")
    for el in elements:
        if 'Липецк' in el.text:
            el.click()
            time_sleep(2)
            break

    elements = driver.find_elements(by=By.CSS_SELECTOR, value='span.button__inner')
    for el in elements:
        if 'Магазины' in el.text:
            el.click()
            time_sleep(2)
            break

    elements = driver.find_element(by=By.CLASS_NAME, value='simplebar-content').find_elements(by=By.CLASS_NAME, value="stores-list-item__name")
    for el in elements:
        if 'ул. Катукова, д. 51' in el.text:
            el.click()
            time_sleep(2)
            break

    element = driver.find_element(by=By.XPATH, value="//*[contains(text(), 'Выбрать магазин')]")
    element.click()
    time_sleep(10)

if __name__ == '__main__':
    list_link = ['https://lenta.com/catalog/', 'https://lenta.com/catalog/', 'https://lenta.com/catalog/']
    
    run_parser(run_driver, list_link)    