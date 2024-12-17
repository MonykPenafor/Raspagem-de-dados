import pyodbc
import json
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database connection
DB_CONFIG = {
    'driver': 'ODBC Driver 18 for SQL Server',
    'server': 'MONYK\\SQLEXPRESS',
    'database': 'FlashcardGeneratorDB',
    'trusted_connection': 'yes',
    'trust_server_certificate': 'yes'
}

def get_db_connection():
    try:
        conn = pyodbc.connect(
            f"DRIVER={DB_CONFIG['driver']};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"Trusted_Connection={DB_CONFIG['trusted_connection']};"
            f"TrustServerCertificate={DB_CONFIG['trust_server_certificate']};",
            timeout=10
        )
        logging.info("Connected to the database successfully.")
        return conn
    except pyodbc.Error as e:
        logging.error(f"Database connection failed: {e}")
        raise

# Save flashcard data to the database
failed_items = []


def save_flashcard(cursor, data, id_user):
    try:
        cursor.execute(
            """
            INSERT INTO FLASHCARDS (
                id_user, 
                source_language, 
                target_language, 
                category,
                word_source, 
                word_target, 
                example_sentence_source,
                example_sentence_target, 
                pronunciation, 
                tips, 
                is_public, 
                proficiency
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                id_user,
                data['source_language'],
                data['target_language'],
                data['category'],
                data['word_source'],
                data['word_target'],
                data.get('example_sentence_source', '-'),
                data.get('example_sentence_target', '-'),
                data.get('pronunciation', '-'),
                data.get('tips', None),
                1,
                data.get('proficiency')
            )
        )
        logging.info("Flashcard saved successfully.")
    except Exception as e:
        logging.error(f"Error saving flashcard: {e}")
        
        data['error_message'] = str(e)
        
        failed_items.append(data)

        with open('failed_items.json', 'w', encoding='utf-8') as f:
            json.dump(failed_items, f, ensure_ascii=False, indent=4)
        logging.info("Error details saved to 'failed_items.json'")
        
        raise

# Selenium helpers
def wait_for_element(driver, time, by, locator):
    try:
        return WebDriverWait(driver, time).until(EC.presence_of_element_located((by, locator)))
    except TimeoutException:
        logging.error(f"Element not found: {locator}")
        raise

def wait_for_elements(driver, time, by, locator):
    try:
        return WebDriverWait(driver, time).until(EC.presence_of_all_elements_located((by, locator)))
    except TimeoutException:
        logging.error(f"Elements not found: {locator}")
        raise

def convert_proficiency_level(level):
    proficiency_map = {
        'beginner': 'A1',
        'lower intermediate': 'A2',
        'intermediate': 'B1',
        'upper intermediate': 'B2',
        'advanced': 'C1',
        'proficient': 'C2',
    }
    
    return proficiency_map.get(level.lower(), 'A2')  

# Main script
id_user = 3
source_language = 'ENG_JAP'
website = 'https://iknow.jp/content/japanese'

# Headless browser setup
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-software-rasterizer")
chrome_options.add_argument('--disable-features=DefaultPassthroughCommandDecoder')


def main():
    conn = get_db_connection()
    cursor = conn.cursor()

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(website)
    logging.info("Website opened successfully.")

    try:
        divs = wait_for_elements(driver, 10, By.CLASS_NAME, 'details.shiv-border-box-sizing')
        for div in divs:
            try:
                
                # Navigate to link
                link = div.find_element(By.CSS_SELECTOR, 'a')
                logging.info(f"Acessing: {link.text}")                
                link.click()
                logging.info("Navigated to detail page")

                # Extract series and level
                series = wait_for_element(driver, 10, By.CLASS_NAME, 'content-column.stat.series').find_element(By.CLASS_NAME, 'primary').text
                level = driver.find_element(By.CLASS_NAME, 'content-column.stat.level').find_element(By.CLASS_NAME, 'primary').text
                proficiency = convert_proficiency_level(level)
                
                # Extract items
                items = driver.find_elements(By.CLASS_NAME, 'item')

                for item in items:
                    try:
                        # Extract item details
                        item_details = item.find_element(By.CLASS_NAME, 'item-details')

                        vocabulary = item_details.find_element(By.CLASS_NAME, 'cue').text
                        translation = item_details.find_element(By.CLASS_NAME, 'response').text
                        voc_type = item_details.find_element(By.CLASS_NAME, 'part-of-speech').text

                        transliteration = ''
                        t = item_details.find_elements(By.CLASS_NAME, 'transliteration')
                        if t:
                            transliteration = t[0].text
                            
                        data = {
                            'source_language': source_language,
                            'target_language': series,
                            'category': voc_type,
                            'word_source': translation,
                            'word_target': f"{vocabulary} {transliteration}",
                            'proficiency': proficiency

                        }

                        # Extract sentences
                        sentences = item.find_elements(By.CLASS_NAME, 'sentence-text')
                        if sentences:
                            for sentence in sentences:
                                sentence_voc = sentence.find_element(By.CLASS_NAME, 'text').text
                                sentence_transliteration = sentence.find_element(By.CLASS_NAME, 'transliteration').text
                                sentence_translation = sentence.find_element(By.CLASS_NAME, 'translation').text

                                data.update({
                                    'example_sentence_source': sentence_translation,
                                    'example_sentence_target': sentence_voc,
                                    'pronunciation': sentence_transliteration
                                })

                                save_flashcard(cursor, data, id_user)
                        else:
                            save_flashcard(cursor, data, id_user)
                    except Exception as e:
                        logging.error(f"Error processing item")

                conn.commit()
                logging.info("Transaction committed.")
                driver.back()
                logging.info("going back.")

            except Exception as e:
                conn.rollback()
                logging.error(f"Error processing div: {e}")
                try:
                    driver.back()
                except Exception:
                    logging.error("Failed to navigate back.")

    finally:
        cursor.close()
        conn.close()
        driver.quit()
        logging.info("Resources cleaned up and script completed.")

if __name__ == "__main__":
    main()
