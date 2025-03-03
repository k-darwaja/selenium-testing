from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
import warnings
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

# Suppress BeautifulSoup warnings
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

# Step 1: Fetch HTML and Extract First Column Values
url = "https://trends.builtwith.com/websitelist/Magento"  # Replace with the actual URL
response = requests.get(url)
html = response.text  # Get HTML content

# Parse with BeautifulSoup
soup = BeautifulSoup(html, "html.parser")
first_column_values = [td.text.strip() for td in soup.select("td.pl-0.text-primary")]

print(f"Extracted {len(first_column_values)} values.")

# Step 2: Automate Searches for All Extracted Values
if first_column_values:
    # Set up the WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode (optional)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Open the target website
    driver.get("https://www.sitemon.ai")  # Replace with actual search page URL
    time.sleep(2)  # Allow time for the page to load

    # Initialize a list to store results
    results = []

    # Iterate through all extracted values
    for value in first_column_values:
        try:
            # Re-locate the search input field (to avoid stale reference error)
            search_input = driver.find_element(By.ID, "search")
            search_input.clear()  # Clear previous input
            search_input.send_keys(value)  # Enter the new value
            
            # Locate and click the submit button
            submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            submit_button.click()  # Click search button
            
            print(f"Searched for: {value}")
            time.sleep(3)  # Wait for search results to load
            
            # Extract required information
            soup = BeautifulSoup(driver.page_source, "html.parser")
            domain = soup.select_one("p:contains('Domain:') span").text.strip()
            response_time = soup.select_one("p:contains('Response Time:') span").text.strip()
            visited_times = soup.select_one("p:contains('Visited Times:') span").text.strip()
            last_visited = soup.select_one("p:contains('Last Visited:') span").text.strip()
            status = soup.select_one("p:contains('Status:') span").text.strip()
            last_checked = soup.select_one("p:contains('Last Checked:') span").text.strip()

            # Store the results
            results.append({
                "Domain": domain,
                "Response Time": response_time,
                "Visited Times": visited_times,
                "Last Visited": last_visited,
                "Status": status,
                "Last Checked": last_checked,
            })
            
            # Click "Back" button to return to search page
            back_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Back')]")
            back_button.click()
            time.sleep(10)  # Wait for the page to reload
            
        except Exception as e:
            print(f"Error processing {value}: {e}")

    # Close the browser after all searches
    driver.quit()

    # Step 3: Save results to Excel
    df = pd.DataFrame(results)
    df.to_excel("website_data.xlsx", index=False)
    print("Data saved to website_data.xlsx.")
else:
    print("No data extracted to test.")