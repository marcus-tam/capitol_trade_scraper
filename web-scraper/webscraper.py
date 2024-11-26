from selenium import webdriver
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

class WebScraper:
    def __init__(self, headless=True, interval=30, baseurl="https://www.capitoltrades.com/trades"):
        # Set up Chrome options
        chrome_options = webdriver.ChromeOptions()
        
        # Disables the AutomationControlled feature, which helps to prevent websites from detecting that the browser is being controlled by automation software.
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Runs Chrome in headless mode, which means it operates without a graphical user interface. This is useful for running automated tests or web scraping tasks on servers without a display.
        if headless:
            chrome_options.add_argument("--headless")
        
        # Disables the sandbox security feature. This can help avoid certain security restrictions but should be used with caution as it reduces the security of the browser.
        chrome_options.add_argument("--no-sandbox")
        
        # Disables the use of /dev/shm (shared memory) in Chrome. This can help prevent issues related to limited shared memory space, especially in containerized environments like Docker.
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Disables GPU hardware acceleration. This can help avoid rendering issues and improve stability, particularly when running in headless mode.
        chrome_options.add_argument("--disable-gpu")
        
        # Initialize the Chrome WebDriver with ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Apply stealth settings
        stealth(self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True)
        
        self.wait = WebDriverWait(self.driver, 10)
        self.baseurl = baseurl
        self.seen_trades = set()
        self.interval = interval

    def navigate_to_site(self, baseurl=None):
        if baseurl is None:
            baseurl = self.baseurl
        self.driver.get(baseurl)
        time.sleep(5)
        try:
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "site-main")))  
            print("Successfully loaded the page")
        except TimeoutException:
            print("Failed to load the page")
            self.driver.quit()

    def get_page_number(self):
        try:
            find_page_max = self.driver.find_element(By.XPATH, '/html/body/div/main/main/section/div[3]/div[2]/div[1]/p[1]/b[2]')
            page_max = int(find_page_max.text)
            return page_max
        except TimeoutException:
            print("Failed to locate the page maximum")
            self.driver.quit()
            return None
        except ValueError:
            print("Failed to convert page number to integer")
            self.driver.quit()
            return None

    def extract_trades(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))
            table_xpath = '/html/body/div/main/main/section/div[3]/div[1]/div/table'
            table = self.driver.find_element(By.XPATH, table_xpath)
            table_data = table.text
            return table_data
        except TimeoutException:
            print("Failed to locate the trades table")
            self.driver.quit()
            return None

    def close(self):
        self.driver.quit()

# Example usage
scraper = WebScraper(headless=False)
scraper.navigate_to_site()
page_max = scraper.get_page_number()

all_trades = []


try:
    if page_max is not None:
        for i in range(1, page_max + 1):
            scraper.navigate_to_site(baseurl=f"https://www.capitoltrades.com/trades?pageSize=100&page={i}")
            trades = scraper.extract_trades()
            if trades:
                all_trades.append(trades)

except Exception:
    for trade in all_trades:
        print(trade)

input("Press any key to close the browser")
scraper.close()

# Print or process all_trades
