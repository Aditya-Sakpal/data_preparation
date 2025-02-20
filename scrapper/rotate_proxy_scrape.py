import time
import random
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

# Load Proxies
with open('valid_proxies.txt', 'r') as file:
    proxies = file.read().splitlines()

# Load URLs
with open('single_page_scrape.txt', 'r') as file:
    urls = file.read().splitlines()

def get_driver(proxy):
    """Initialize a Selenium WebDriver instance with a given proxy."""
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Prevent detection
    chrome_options.add_argument("--start-maximized")  # Maximize window
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
    
    # Set Proxy
    if proxy:
        chrome_options.add_argument(f'--proxy-server={proxy}')
    
    service = Service('chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scrape_page(driver, url):
    """Scrape the given URL and return page text."""
    driver.get(url)
    time.sleep(random.uniform(3, 6)) 
    body = driver.find_element(By.TAG_NAME, "body")
    return body.text

# Iterate over URLs while rotating proxies
for index, url in enumerate(urls):
    proxy = random.choice(proxies) if proxies else None  # Pick a random proxy
    print(f"Using Proxy: {proxy} for {url}")

    driver = get_driver(proxy)  # Initialize driver with the proxy

    try:
        page_text = scrape_page(driver, url)

        # Save scraped data
        filename = f"{url.replace('https://', '').replace('http://', '').replace('/', '_')}_data.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(page_text)
        
        print(f"Saved: {filename}")

    except Exception as e:
        print(f"Error scraping {url}: {e}")

    finally:
        driver.quit()  # Close browser after scraping

print("Scraping completed!")