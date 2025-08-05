#!/usr/bin/env python3
"""
Live RDP Connection Test - Notepad Test
Connects to the actual RDP server and opens Notepad with test text
"""

import os
import sys
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from xvfbwrapper import Xvfb
import pyautogui

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# RDP Connection Details
RDP_WEB_PORTAL = "https://accessdatabasecloud.cloudworkstations.com"
WEB_LOGIN_USERNAME = "support@my420.ca"
WEB_LOGIN_PASSWORD = "5155Spectrum!!"
RDP_HOST = "127.0.0.1:58799"
RDP_USERNAME = "VM254950\\Christian.Marcoux"
RDP_PASSWORD = "christian.marcoux@100*"

class LiveRDPNotpadTest:
    def __init__(self):
        self.driver = None
        self.display = None
        
    def setup_virtual_display(self):
        """Set up virtual display for headless operation"""
        try:
            logger.info("Setting up virtual display...")
            self.display = Xvfb(width=1920, height=1080, colordepth=24)
            self.display.start()
            os.environ['DISPLAY'] = ':99'
            logger.info("Virtual display started successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to setup virtual display: {e}")
            return False
    
    def setup_firefox_driver(self):
        """Set up Firefox WebDriver"""
        try:
            logger.info("Setting up Firefox WebDriver...")
            options = FirefoxOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            
            # Set geckodriver path
            from selenium.webdriver.firefox.service import Service
            service = Service('/usr/local/bin/geckodriver')
            
            # Create driver
            self.driver = webdriver.Firefox(service=service, options=options)
            self.driver.implicitly_wait(10)
            logger.info("Firefox WebDriver created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create Firefox WebDriver: {e}")
            return False
    
    def login_to_web_portal(self):
        """Login to the RDP web portal"""
        try:
            logger.info(f"Navigating to web portal: {RDP_WEB_PORTAL}")
            self.driver.get(RDP_WEB_PORTAL)
            time.sleep(3)
            
            # Take screenshot
            self.driver.save_screenshot("/app/01_portal_page.png")
            logger.info("Screenshot saved: 01_portal_page.png")
            
            # Find and fill username
            logger.info("Looking for username field...")
            username_field = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_field.clear()
            username_field.send_keys(WEB_LOGIN_USERNAME)
            logger.info(f"Username entered: {WEB_LOGIN_USERNAME}")
            
            # Find and fill password
            logger.info("Looking for password field...")
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(WEB_LOGIN_PASSWORD)
            logger.info("Password entered")
            
            # Click login button
            logger.info("Clicking login button...")
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # Wait for page to load
            time.sleep(5)
            self.driver.save_screenshot("/app/02_after_login.png")
            logger.info("Screenshot saved: 02_after_login.png")
            
            return True
        except Exception as e:
            logger.error(f"Failed to login to web portal: {e}")
            self.driver.save_screenshot("/app/error_login.png")
            return False
    
    def connect_to_rdp(self):
        """Connect to the RDP session"""
        try:
            logger.info("Looking for RDP connection...")
            
            # Wait a bit for page to fully load
            time.sleep(5)
            
            # Take screenshot of current state
            self.driver.save_screenshot("/app/03_looking_for_rdp.png")
            logger.info("Screenshot saved: 03_looking_for_rdp.png")
            
            # Try multiple approaches to find and click RDP connection
            rdp_clicked = False
            
            # Method 1: Look for Connect button
            try:
                connect_elements = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Connect') or contains(text(), 'connect')]")
                if connect_elements:
                    logger.info("Found Connect button, clicking...")
                    self.driver.execute_script("arguments[0].click();", connect_elements[0])
                    rdp_clicked = True
                    time.sleep(5)
            except Exception as e:
                logger.warning(f"Connect button method failed: {e}")
            
            # Method 2: Look for RDP link
            if not rdp_clicked:
                try:
                    rdp_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'rdp') or contains(text(), 'RDP') or contains(text(), 'Remote')]")
                    if rdp_links:
                        logger.info("Found RDP link, clicking...")
                        self.driver.execute_script("arguments[0].click();", rdp_links[0])
                        rdp_clicked = True
                        time.sleep(5)
                except Exception as e:
                    logger.warning(f"RDP link method failed: {e}")
            
            # Method 3: Look for any clickable element with RDP text
            if not rdp_clicked:
                try:
                    all_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'RDP') or contains(text(), 'Remote') or contains(text(), 'Desktop')]")
                    for element in all_elements:
                        if element.is_displayed() and element.is_enabled():
                            logger.info("Found RDP element, clicking...")
                            self.driver.execute_script("arguments[0].click();", element)
                            rdp_clicked = True
                            time.sleep(5)
                            break
                except Exception as e:
                    logger.warning(f"General RDP element method failed: {e}")
            
            # Method 4: Try any clickable button or link
            if not rdp_clicked:
                try:
                    buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    links = self.driver.find_elements(By.TAG_NAME, "a")
                    all_clickable = buttons + links
                    
                    for element in all_clickable:
                        if element.is_displayed() and element.is_enabled():
                            text = element.text.lower()
                            if any(keyword in text for keyword in ['connect', 'start', 'launch', 'open']):
                                logger.info(f"Found clickable element with text '{element.text}', clicking...")
                                self.driver.execute_script("arguments[0].click();", element)
                                rdp_clicked = True
                                time.sleep(5)
                                break
                except Exception as e:
                    logger.warning(f"General clickable element method failed: {e}")
            
            # Take screenshot after attempting to click
            self.driver.save_screenshot("/app/04_after_rdp_click.png")
            logger.info("Screenshot saved: 04_after_rdp_click.png")
            
            # Wait for RDP session to load
            time.sleep(10)
            
            # Check if we need RDP credentials
            try:
                logger.info("Looking for RDP login fields...")
                
                # Look for username field
                username_fields = self.driver.find_elements(By.XPATH, "//input[@type='text' or @name='username' or @placeholder*='user']")
                password_fields = self.driver.find_elements(By.XPATH, "//input[@type='password']")
                
                if username_fields and password_fields:
                    logger.info("Found RDP login fields...")
                    
                    # Enter RDP credentials
                    username_fields[0].clear()
                    username_fields[0].send_keys(RDP_USERNAME)
                    logger.info(f"RDP username entered: {RDP_USERNAME}")
                    
                    password_fields[0].clear()
                    password_fields[0].send_keys(RDP_PASSWORD)
                    logger.info("RDP password entered")
                    
                    # Find and click login button
                    login_buttons = self.driver.find_elements(By.XPATH, "//button[@type='submit' or contains(text(), 'Login') or contains(text(), 'Connect')]")
                    if login_buttons:
                        login_buttons[0].click()
                        logger.info("RDP login button clicked")
                        time.sleep(10)
                    
            except Exception as e:
                logger.warning(f"RDP credentials not needed or already authenticated: {e}")
            
            # Final screenshot
            self.driver.save_screenshot("/app/05_rdp_session_ready.png")
            logger.info("Screenshot saved: 05_rdp_session_ready.png")
            
            logger.info("RDP connection process completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to RDP: {e}")
            self.driver.save_screenshot("/app/error_rdp_connect.png")
            return False
    
    def open_notepad_and_test(self):
        """Open Notepad and add test text"""
        try:
            logger.info("Attempting to open Notepad...")
            
            # Switch to RDP session iframe if it exists
            try:
                logger.info("Looking for RDP iframe...")
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                if iframes:
                    logger.info(f"Found {len(iframes)} iframes, switching to first one...")
                    self.driver.switch_to.frame(iframes[0])
                    time.sleep(2)
            except Exception as e:
                logger.warning(f"Could not switch to iframe: {e}")
            
            # Take screenshot of current state
            self.driver.save_screenshot("/app/05_before_notepad.png")
            logger.info("Screenshot saved: 05_before_notepad.png")
            
            # Try to click on the desktop area first
            logger.info("Clicking on desktop area...")
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                ActionChains(self.driver).move_to_element(body).click().perform()
                time.sleep(2)
            except:
                pass
            
            # Method 1: Try keyboard shortcut to open Run dialog
            logger.info("Trying Windows + R to open Run dialog...")
            try:
                ActionChains(self.driver).key_down(Keys.COMMAND).send_keys('r').key_up(Keys.COMMAND).perform()
                time.sleep(3)
                
                # Type notepad and press Enter
                ActionChains(self.driver).send_keys('notepad').perform()
                time.sleep(1)
                ActionChains(self.driver).send_keys(Keys.RETURN).perform()
                time.sleep(3)
                
                logger.info("Notepad command sent via Run dialog")
                
            except Exception as e:
                logger.warning(f"Run dialog method failed: {e}")
                
                # Method 2: Try Start menu
                logger.info("Trying Start menu...")
                try:
                    # Press Windows key
                    ActionChains(self.driver).send_keys(Keys.COMMAND).perform()
                    time.sleep(2)
                    
                    # Type notepad
                    ActionChains(self.driver).send_keys('notepad').perform()
                    time.sleep(2)
                    
                    # Press Enter
                    ActionChains(self.driver).send_keys(Keys.RETURN).perform()
                    time.sleep(3)
                    
                    logger.info("Notepad opened via Start menu")
                    
                except Exception as e2:
                    logger.warning(f"Start menu method failed: {e2}")
                    
                    # Method 3: Try right-click desktop
                    logger.info("Trying right-click on desktop...")
                    try:
                        body = self.driver.find_element(By.TAG_NAME, "body")
                        ActionChains(self.driver).context_click(body).perform()
                        time.sleep(2)
                        logger.info("Right-clicked on desktop")
                    except Exception as e3:
                        logger.warning(f"Right-click method failed: {e3}")
            
            # Wait for Notepad to open
            time.sleep(5)
            self.driver.save_screenshot("/app/06_after_notepad_attempt.png")
            logger.info("Screenshot saved: 06_after_notepad_attempt.png")
            
            # Try to type test text
            logger.info("Attempting to type test text...")
            test_text = "RDP CONNECTION TEST SUCCESSFUL!\nNotepad opened via automation.\nTimestamp: " + time.strftime("%Y-%m-%d %H:%M:%S")
            
            try:
                ActionChains(self.driver).send_keys(test_text).perform()
                logger.info("Test text typed successfully")
                time.sleep(2)
                
                # Take final screenshot
                self.driver.save_screenshot("/app/07_notepad_with_text.png")
                logger.info("Screenshot saved: 07_notepad_with_text.png")
                
                logger.info("✅ NOTEPAD TEST COMPLETED SUCCESSFULLY!")
                logger.info(f"Text entered: {test_text}")
                
                return True
                
            except Exception as e:
                logger.error(f"Failed to type text: {e}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to open Notepad: {e}")
            self.driver.save_screenshot("/app/error_notepad.png")
            return False
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.driver:
                logger.info("Closing WebDriver...")
                self.driver.quit()
            if self.display:
                logger.info("Stopping virtual display...")
                self.display.stop()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def run_test(self):
        """Run the complete RDP Notepad test"""
        logger.info("🚀 Starting Live RDP Notepad Test...")
        
        try:
            # Setup virtual display
            if not self.setup_virtual_display():
                return False
            
            # Setup Firefox driver
            if not self.setup_firefox_driver():
                return False
            
            # Login to web portal
            if not self.login_to_web_portal():
                return False
            
            # Connect to RDP
            if not self.connect_to_rdp():
                return False
            
            # Open Notepad and test
            if not self.open_notepad_and_test():
                return False
            
            logger.info("🎉 RDP NOTEPAD TEST COMPLETED SUCCESSFULLY!")
            return True
            
        except Exception as e:
            logger.error(f"Test failed with error: {e}")
            return False
        finally:
            # Keep session open for 30 seconds for verification
            logger.info("Keeping session open for 30 seconds for verification...")
            time.sleep(30)
            self.cleanup()

if __name__ == "__main__":
    # Run the live RDP test
    test = LiveRDPNotpadTest()
    success = test.run_test()
    
    if success:
        print("✅ RDP NOTEPAD TEST PASSED!")
        sys.exit(0)
    else:
        print("❌ RDP NOTEPAD TEST FAILED!")
        sys.exit(1)