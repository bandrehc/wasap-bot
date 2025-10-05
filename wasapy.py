import csv
import sys
import time
import argparse
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from message_templates import get_message_template


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler('wasapy.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


def reset_to_chat_list(driver, wait, logger):
    try:
        logger.debug("Resetting to chat list...")
        
        try:
            whatsapp_logo = driver.find_element(By.CSS_SELECTOR, "div[data-testid='logo']")
            if whatsapp_logo.is_displayed():
                whatsapp_logo.click()
                time.sleep(1)
                logger.debug("Reset successful via WhatsApp logo")
                return True
        except:
            logger.debug("Could not click WhatsApp logo")
        
        try:
            chat_list = driver.find_element(By.CSS_SELECTOR, "div[data-testid='chat-list']")
            if chat_list.is_displayed():
                driver.execute_script("arguments[0].click();", chat_list)
                time.sleep(1)
                logger.debug("Reset successful via chat list")
                return True
        except:
            logger.debug("Could not click chat list")
        
        try:
            driver.switch_to.active_element.send_keys(Keys.ESCAPE)
            time.sleep(0.5)
            driver.switch_to.active_element.send_keys(Keys.ESCAPE)
            time.sleep(1)
            logger.debug("Reset successful via ESC key")
            return True
        except:
            logger.debug("Could not use ESC key")
        
        try:
            current_url = driver.current_url
            if "https://web.whatsapp.com" in current_url and len(current_url) > 25:
                driver.get("https://web.whatsapp.com/")
                time.sleep(3)
                logger.debug("Reset successful via direct navigation")
                return True
        except:
            logger.debug("Could not navigate to base URL")
            
        return False
        
    except Exception as e:
        logger.debug(f"Error in reset_to_chat_list: {e}")
        return False


def ensure_new_chat_button_available(driver, wait, logger, max_attempts=3):
    for attempt in range(1, max_attempts + 1):
        try:
            logger.debug(f"Attempt {attempt}/{max_attempts} - Looking for new chat button...")
            
            new_chat = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-icon="new-chat-outline"]'))
            )
            
            if new_chat.is_displayed():
                logger.debug("New chat button found and available")
                return new_chat
            else:
                logger.debug("Button found but not visible")
                
        except TimeoutException:
            logger.debug(f"Timeout on attempt {attempt}")
            
            if attempt < max_attempts:
                reset_to_chat_list(driver, wait, logger)
                time.sleep(2)
            
        except Exception as e:
            logger.debug(f"Error on attempt {attempt}: {e}")
            
            if attempt < max_attempts:
                reset_to_chat_list(driver, wait, logger)
                time.sleep(2)
    
    return None


def send_message_with_retry(driver, wait, numero, nombre, template_name="default", max_attempts=2):
    logger = logging.getLogger(__name__)
    
    mensaje = get_message_template(template_name, nombre=nombre)
    
    for attempt in range(1, max_attempts + 1):
        try:
            logger.info(f"Attempt {attempt}/{max_attempts} - Sending personalized message to {nombre} ({numero})")
            
            if attempt > 1:
                logger.debug("Resetting state for retry...")
                reset_success = reset_to_chat_list(driver, wait, logger)
                if not reset_success:
                    logger.warning("Could not reset completely, continuing...")
                time.sleep(2)
            
            logger.debug("Looking for new chat button...")
            new_chat = ensure_new_chat_button_available(driver, wait, logger)
            
            if new_chat is None:
                logger.warning("Could not find new chat button")
                continue
                
            try:
                new_chat.click()
            except:
                driver.execute_script("arguments[0].click();", new_chat)
            
            logger.debug("New chat button clicked")
            time.sleep(1)

            logger.debug("Looking for search box...")
            search_box = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true'][aria-placeholder='Buscar un nombre o número']"))
            )
            
            search_box.click()
            time.sleep(0.3)
            search_box.clear()
            time.sleep(0.3)
            
            try:
                search_box.send_keys(Keys.CONTROL + "a")
                time.sleep(0.2)
                search_box.send_keys(Keys.DELETE)
                time.sleep(0.2)
            except:
                pass
            
            logger.debug(f"Writing number: {numero}")

            for char in numero:
                search_box.send_keys(char)
                time.sleep(0.01)

            time.sleep(1.5)
            
            logger.debug("Looking for contact in results...")
            contact_found = False
            
            contact_selectors = [
                f"span[title*='{numero}']",
                "div[data-testid='cell-frame-container']",
                "div[role='listitem']",
                "div[data-testid='chat']"
            ]
            
            for selector in contact_selectors:
                try:
                    contacts = driver.find_elements(By.CSS_SELECTOR, selector)
                    for contact in contacts:
                        contact_html = contact.get_attribute('outerHTML') or ""
                        contact_text = contact.get_attribute('textContent') or ""
                        
                        if numero in contact_html or numero in contact_text:
                            driver.execute_script("arguments[0].click();", contact)
                            contact_found = True
                            logger.debug(f"Contact found and clicked with selector: {selector}")
                            break
                    
                    if contact_found:
                        break
                        
                except Exception as e:
                    logger.debug(f"Error with selector {selector}: {e}")
                    continue
            
            if not contact_found:
                logger.debug("Contact not found in list, trying ENTER...")
                search_box.send_keys(Keys.ENTER)
                time.sleep(2)
                
                try:
                    invalid_spans = driver.find_elements(By.CSS_SELECTOR, "span[dir='auto'][class='_ao3e']")
                    for span in invalid_spans:
                        span_text = span.get_attribute('textContent') or span.text
                        if "No se encontraron resultados para" in span_text:
                            logger.warning(f"INVALID NUMBER - {span_text}")
                            return False
                except:
                    pass

            time.sleep(2)
            logger.debug("Chat opened, looking for message field")

            logger.debug("Looking for message field...")
            
            message_selectors = [
                "div[contenteditable='true'][role='textbox'][data-lexical-editor='true']",
                "div[contenteditable='true'][data-tab='10']",
                "div[contenteditable='true'][aria-placeholder='Escribe un mensaje']",
                "div[contenteditable='true'][aria-label*='Escribe a']"
            ]
            
            sms_box = None
            for selector in message_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        aria_placeholder = element.get_attribute('aria-placeholder') or ""
                        aria_label = element.get_attribute('aria-label') or ""
                        
                        is_search_bar = (
                            'buscar' in aria_placeholder.lower() or
                            'search' in aria_placeholder.lower() or
                            'buscar' in aria_label.lower() or
                            'search' in aria_label.lower()
                        )
                        
                        if not is_search_bar and element.is_displayed():
                            sms_box = element
                            logger.debug(f"Message field found with selector: {selector}")
                            break
                    
                    if sms_box is not None:
                        break
                        
                except Exception as e:
                    logger.debug(f"Error with selector {selector}: {e}")
                    continue
            
            if sms_box is None:
                logger.debug("Using last resort method...")
                try:
                    chat_area = driver.find_element(By.CSS_SELECTOR, "div[data-testid='conversation-panel-body']")
                    chat_area.click()
                    time.sleep(0.5)
                except:
                    pass
                
                active_element = driver.switch_to.active_element
                for char in mensaje:
                    if char == '\n':
                        active_element.send_keys(Keys.SHIFT, Keys.ENTER)
                        time.sleep(0.05)
                    else:
                        active_element.send_keys(char)
                        time.sleep(0.05)
                
                time.sleep(0.5)
                active_element.send_keys(Keys.ENTER)
            else:
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", sms_box)
                    time.sleep(0.3)
                    
                    sms_box.click()
                    time.sleep(0.3)
                    sms_box.clear()
                    
                    logger.debug(f"Writing personalized message for {nombre}...")
                    
                    for char in mensaje:
                        if char == '\n':
                            sms_box.send_keys(Keys.SHIFT, Keys.ENTER)
                            time.sleep(0.05)
                        else:
                            sms_box.send_keys(char)
                            time.sleep(0.05)
                    
                    time.sleep(0.5)
                    sms_box.send_keys(Keys.ENTER)
                    
                except Exception as e:
                    logger.debug(f"Error writing to specific field: {e}")
                    try:
                        chat_area = driver.find_element(By.CSS_SELECTOR, "div[data-testid='conversation-panel-body']")
                        chat_area.click()
                        time.sleep(0.5)
                    except:
                        pass
                    
                    active_element = driver.switch_to.active_element
                    for char in mensaje:
                        if char == '\n':
                            active_element.send_keys(Keys.SHIFT, Keys.ENTER)
                            time.sleep(0.05)
                        else:
                            active_element.send_keys(char)
                            time.sleep(0.05)
                    
                    time.sleep(0.5)
                    active_element.send_keys(Keys.ENTER)
            
            time.sleep(2)
            logger.info(f"SUCCESS - Personalized message sent to {nombre} ({numero}) on attempt {attempt}")
            
            logger.debug("Preparing for next contact...")
            return True

        except TimeoutException as e:
            logger.warning(f"TIMEOUT - Attempt {attempt}/{max_attempts} failed for {nombre} ({numero})")
            if attempt < max_attempts:
                logger.info("Retrying in 3 seconds...")
                time.sleep(3)
            else:
                logger.error(f"FINAL FAILURE - Timeout for {nombre} ({numero})")
                
        except WebDriverException as e:
            logger.warning(f"WEB ERROR - Attempt {attempt}/{max_attempts} failed for {nombre} ({numero})")
            if attempt < max_attempts:
                logger.info("Retrying in 3 seconds...")
                time.sleep(3)
            else:
                logger.error(f"FINAL FAILURE - Browser error for {nombre} ({numero})")
                
        except Exception as e:
            logger.warning(f"UNEXPECTED ERROR - Attempt {attempt}/{max_attempts} failed for {nombre} ({numero}): {type(e).__name__}")
            if attempt < max_attempts:
                logger.info("Retrying in 3 seconds...")
                time.sleep(3)
            else:
                logger.error(f"FINAL FAILURE - Unexpected error for {nombre} ({numero}): {e}")

    return False


def main(csv_file, template_name="default", firefox_profile=None):
    logger = setup_logging()
    logger.info("STARTING WhatsApp Bot")
    logger.info(f"CSV File: {csv_file}")
    logger.info(f"Message Template: {template_name}")
    
    logger.info("Configuring Firefox...")
    options = Options()
    options.add_argument("--user-agent=Mozilla/5.0")
    
    if firefox_profile:
        options.add_argument("-profile")
        options.add_argument(firefox_profile)

    try:
        driver = webdriver.Firefox(options=options)
        logger.info("Firefox started successfully")
        
        logger.info("Navigating to WhatsApp Web...")
        driver.get("https://web.whatsapp.com/")
        
        wait = WebDriverWait(driver, 30)
        logger.info("WebDriverWait configured (30 seconds)")

        print("\nScan the QR code in WhatsApp Web...")
        print("If you already have an active session, just press enter:")
        input("Press ENTER after logging into WhatsApp Web: ")
        logger.info("User confirmed login")

        total_contacts = 0
        successful_sends = 0
        failed_sends = 0
        
        logger.info(f"Reading CSV file: {csv_file}")
        
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row_num, row in enumerate(reader, 1):
                numero = row.get("Numero")
                nombre = row.get("Nombre")
                
                if not numero or not nombre:
                    logger.warning(f"ROW {row_num} - Incomplete data: Numero='{numero}', Nombre='{nombre}' - SKIPPING")
                    continue
                    
                total_contacts += 1
                logger.info(f"PROCESSING {total_contacts} - Number: {numero}, Name: {nombre}")
                
                success = send_message_with_retry(driver, wait, numero, nombre, template_name=template_name, max_attempts=2)
                
                if success:
                    successful_sends += 1
                    logger.info(f"CONTACT {total_contacts} COMPLETED - Success: {successful_sends}/{total_contacts}")
                else:
                    failed_sends += 1
                    logger.error(f"CONTACT {total_contacts} FAILED - Failures: {failed_sends}/{total_contacts}")
                    logger.info("Moving to next contact...")
                
                logger.debug("Pause of 3 seconds before next message...")
                time.sleep(3)

        logger.info("=" * 50)
        logger.info("FINAL SUMMARY")
        logger.info(f"Total contacts processed: {total_contacts}")
        logger.info(f"Messages sent successfully: {successful_sends}")
        logger.info(f"Failed messages: {failed_sends}")
        logger.info(f"Success rate: {(successful_sends/total_contacts*100):.1f}%" if total_contacts > 0 else "Success rate: 0%")
        logger.info("PROCESS COMPLETED")
        logger.info("=" * 50)

    except FileNotFoundError:
        logger.error(f"CRITICAL ERROR - File not found: {csv_file}")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"CRITICAL ERROR - Unexpected error in main: {e}")
        sys.exit(1)
        
    finally:
        try:
            driver.quit()
            logger.info("Browser closed successfully")
        except:
            logger.warning("Could not close browser correctly")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send WhatsApp messages from CSV")
    parser.add_argument("csv_file", help="Path to CSV file with Numero and Nombre columns")
    parser.add_argument("--template", "-t", default="default", help="Message template name (default: 'default')")
    parser.add_argument("--profile", "-p", help="Firefox profile path")
    args = parser.parse_args()

    main(args.csv_file, template_name=args.template, firefox_profile=args.profile)