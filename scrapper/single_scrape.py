from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import os

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
chrome_options.add_argument("--no-sandbox")  # Disable sandboxing

# Path to your ChromeDriver
chrome_driver_path = "D:/data_preparation/scrapper/chromedriver.exe"  # Replace with your ChromeDriver path

# Initialize the WebDriver
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Read URLs from the file
with open('scrapper/single_page_scrape.txt', 'r') as file:
    urls = file.read().splitlines()

# Create a directory to store the scraped data
output_dir = "scrapper/scraped_data"
os.makedirs(output_dir, exist_ok=True)

for url in urls:
    try:
        # Navigate to the URL
        driver.get(url)
        time.sleep(5) 
        # Get the entire page text
        page_text = driver.find_element(By.TAG_NAME, "body").text

        # Sanitize the filename
        filename = url.replace("https://", "").replace("http://", "")
        filename = filename.replace("/", "_").replace(".", "_").replace(":", "_").replace("?", "_").replace("&", "_").replace("=", "_")

        # Add markdown file extension
        filename += ".md"
        filepath = os.path.join(output_dir, filename)

        # Save the text to a markdown file
        with open(filepath, "w", encoding="utf-8") as output_file:
            output_file.write(f"# URL: {url}\n\n")
            output_file.write(page_text)

        print(f"Scraped and saved: {filepath}")

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        continue

driver.quit()