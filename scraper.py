#*************WEBSCRAPING***************
#scrape data from a website and store it in a database

#*************CHROMEDRIVER VERSION SAME AS THE driver***************
website = 'https://iknow.jp/content/japanese'

#IMPORTS
import sys
import csv
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# HEADLESS
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-software-rasterizer")
chrome_options.add_argument('--disable-features=DefaultPassthroughCommandDecoder')

# OPENING THE WEBSITE
driver = webdriver.Chrome(options=chrome_options)
driver.get(website)
driver.window_handles


# FUNCTIONS
def wait_for_element(time, by, locator):
    return WebDriverWait(driver, time).until(EC.presence_of_element_located((by, locator)))

def wait_for_elements(time, by, locator):
    return WebDriverWait(driver, time).until(EC.presence_of_all_elements_located((by, locator)))


# WEBSCRAPING

divs = wait_for_elements(10, By.CLASS_NAME, 'details.shiv-border-box-sizing')

for div in divs:
    try:
        first_child = div.find_element(By.XPATH, './*')  
        first_child.click()  
                    
        series = wait_for_element(10, By.XPATH, '//span[@class="primary"]/a').text
        level = driver.find_element(By.XPATH, '//span[@class="secondary"]').text
        
        print(series, level)
        
        items = driver.find_elements(By.CLASS_NAME, 'item')
        
        for item in items:
            
            item_details = item.find_element(By.CLASS_NAME, 'item-details')
            
            vocabulary = item_details.find_element(By.CLASS_NAME, 'cue').text
            translation =  item_details.find_element(By.CLASS_NAME, 'response').text
            vocType =   item_details.find_element(By.CLASS_NAME, 'part-of-speech').text
            
            try:
                transliteration = item_details.find_element(By.CLASS_NAME, 'transliteration').text
            except:
                transliteration = ''
                            
            print('vocabulary: ', vocabulary, transliteration, translation, vocType)
            
            try:
                sentences = item.find_elements(By.CLASS_NAME, 'sentence-text')
                
                for sentence in sentences:
                    sentence_voc = sentence.find_element(By.CLASS_NAME, 'text').text
                    sentence_transliteration = sentence.find_element(By.CLASS_NAME, 'transliteration').text
                    sentence_translation = sentence.find_element(By.CLASS_NAME, 'translation').text
                    
                    print('ex. : ', sentence_voc, sentence_transliteration, sentence_translation)
            except:
                print('no exemples')

        driver.back()

    except Exception as e:
        print(f"Error processing div: {e}")
        try:
            driver.back()
        except:
            print("Couldn't navigate back.")
driver.quit()
