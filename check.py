from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Website to check
url = "https://www.sitemon.ai"

# Configure Selenium options
options = Options()
options.add_argument("--headless")  # Run Chrome in headless mode (no GUI)
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Initialize WebDriver
try:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Open the website
    driver.get(url)

    # Wait for the page to load
    time.sleep(5)  # Adjust based on website load time

    # Check if the page loaded successfully
    if "ERR_CONNECTION" in driver.page_source or "This site can’t be reached" in driver.page_source:
        print("Website is DOWN.")
    else:
        print("Website is UP. Taking screenshot...")
        driver.save_screenshot("website_screenshot.png")
        print("Screenshot saved as 'website_screenshot.png'")

except Exception as e:
    print(f"Error: {e}")

finally:
    # Close the browser
    driver.quit()
