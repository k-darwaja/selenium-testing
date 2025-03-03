import os
import time
import pandas as pd
from bs4 import BeautifulSoup
import warnings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Step 1: Read Website URLs from CSV
csv_file_path = r"C:\Users\kdarw\OneDrive\Desktop\website_list.csv"  # Update with your actual CSV file path

try:
    df = pd.read_csv(csv_file_path)
    if df.empty or df.columns[0] not in df:
        raise ValueError("CSV file is empty or does not contain valid website URLs.")
    
    # Extract website URLs from the first column
    website_urls = df.iloc[:, 0].dropna().astype(str).tolist()
    website_urls = [url.strip() for url in website_urls if url.strip()]  # Clean whitespace

    if not website_urls:
        print("❌ No website URLs found in the CSV file.")
    else:
        print(f"✅ Extracted {len(website_urls)} website URLs from CSV.")

except Exception as e:
    print(f"❌ Failed to read CSV file: {e}")
    website_urls = []

# Step 2: Check Server Status using sitemon.ai
def check_website_status(driver, website_url):
    """Checks if a website is UP or DOWN using sitemon.ai"""
    print(f"\n🔎 Checking {website_url} on sitemon.ai")

    try:
        driver.get("https://www.sitemon.ai")

        # Wait for the search box
        search_input = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "search")))
        search_input.clear()
        search_input.send_keys(website_url)

        # Click the search button
        search_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        )
        search_button.click()

        # Wait for results to load completely
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//p[contains(text(), 'Status:')]"))
        )

        # Extract data using BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")

        def extract_text(selector):
            """Finds the first matching element and extracts its text."""
            element = soup.select_one(selector)
            return element.text.strip() if element else "N/A"

        # Extract correct values
        response_time = extract_text("p:contains('Response Time:') span")
        last_visited = extract_text("p:contains('Last Visited:') span")

        # Extract status (UP or DOWN)
        status_element = soup.select_one("p:contains('Status:') span.font-semibold")
        status = status_element.text.strip() if status_element else "N/A"

        # Debugging output
        print(f"✅ {website_url}: Status={status}, Response Time={response_time}, Last Visited={last_visited}")

        return {
            "Website": website_url,
            "Response Time": response_time,
            "Last Visited": last_visited,
            "Status": status
        }

    except Exception as e:
        print(f"❌ Error checking {website_url}: {e}")
        return {
            "Website": website_url,
            "Response Time": "Error",
            "Last Visited": "Error",
            "Status": "Error"
        }

# Set up WebDriver with anti-bot options
def start_driver():
    """Starts and returns a new Selenium WebDriver instance"""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run without GUI for faster execution
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")  
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")
    
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Initialize WebDriver
driver = start_driver()

results = []
batch_size = 100  # Restart WebDriver after every 100 sites

for index, website in enumerate(website_urls[:5000]):  # Process first 5000 websites
    if not website.startswith("https://"):
        website = f"https://{website}"

    results.append(check_website_status(driver, website))

    # Restart WebDriver every batch_size URLs to prevent memory issues
    if index % batch_size == 0 and index > 0:
        driver.quit()
        driver = start_driver()

    # Save data every 500 URLs to avoid data loss
    if index % 50 == 0 and index > 0:
        temp_save_path = r"C:\Users\kdarw\OneDrive\Desktop\server_status_backup.xlsx"
        pd.DataFrame(results).to_excel(temp_save_path, index=False)
        print(f"\n💾 Backup saved to {temp_save_path} after {index} checks.")

driver.quit()

# Step 3: Save final results to Excel
final_save_path = r"C:\Users\kdarw\OneDrive\Desktop\server_status.xlsx"

if results:
    df = pd.DataFrame(results)
    df.to_excel(final_save_path, index=False)
    print(f"\n📁 Final data saved to {final_save_path}")
else:
    print("\n⚠️ No valid data extracted. Check for errors.")
