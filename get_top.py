import os
import sys
import time
import glob
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager


def find_browser():
    """Check for available browsers on the system."""
    possible_browsers = {
        "chrome": "C:/Program Files/Google/Chrome/Application/chrome.exe",
        "edge": "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
        "firefox": "C:/Program Files/Mozilla Firefox/firefox.exe",
        "yandex": "C:/Users/{USER}/AppData/Local/Yandex/YandexBrowser/Application/browser.exe".replace("{USER}", os.getlogin())
    }

    for browser, path in possible_browsers.items():
        if os.path.exists(path):
            return browser, path

    return None, None


def get_driver():
    """Get WebDriver for the available browser."""
    browser, binary_path = find_browser()
    download_dir = os.path.join(os.getcwd(), "top_accounts")  # ✅ Set folder for downloads

    if not os.path.exists(download_dir):
        os.makedirs(download_dir)  # ✅ Create folder if not exists

    if not browser:
        print("❌ No supported browser found. Please install Chrome, Edge, Firefox, or Yandex Browser.")
        sys.exit(1)

    print(f"✅ Using {browser.capitalize()} browser...")

    options = None
    service = None

    if browser == "chrome":
        options = webdriver.ChromeOptions()
        options.binary_location = binary_path
        prefs = {"download.default_directory": download_dir}
        options.add_experimental_option("prefs", prefs)
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

    elif browser == "edge":
        options = webdriver.EdgeOptions()
        options.binary_location = binary_path
        prefs = {"download.default_directory": download_dir}
        options.add_experimental_option("prefs", prefs)
        service = EdgeService(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=options)

    elif browser == "firefox":
        options = webdriver.FirefoxOptions()
        options.binary_location = binary_path
        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference("browser.download.dir", download_dir)
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")
        options.profile = profile
        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)

    elif browser == "yandex":
        options = webdriver.ChromeOptions()
        options.binary_location = binary_path
        prefs = {"download.default_directory": download_dir}
        options.add_experimental_option("prefs", prefs)
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

    else:
        print("❌ No supported browser found.")
        sys.exit(1)

    return driver


def get_latest_csv(download_dir):
    """Get the latest downloaded CSV file."""
    files = glob.glob(os.path.join(download_dir, "export-accounts-*.csv"))
    if not files:
        return None
    return max(files, key=os.path.getctime)  # Get the most recently created file


def DownloadCSV(num_accounts):
    """
    Open Polygonscan and download the CSV files for the requested number of accounts.
    """
    driver = get_driver()  # ✅ Browser is now visible
    download_dir = os.path.join(os.getcwd(), "top_accounts")

    # ✅ Calculate number of pages
    accounts_per_page = 100
    num_pages = (num_accounts + accounts_per_page - 1) // accounts_per_page  # Round up

    print(f"✅ Need to download {num_pages} pages for {num_accounts} accounts.")

    for page in range(1, num_pages + 1):
        url = f"https://polygonscan.com/accounts/{page}?ps=100"
        print(f"🌍 Opening: {url}")

        driver.get(url)  # Open the current page

        try:
            # ✅ Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # ✅ Scroll down to ensure all elements are loaded
            driver.execute_script("window.scrollBy(0, 500);")

            # ✅ Wait for the "Download Page Data" button
            try:
                download_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="btnExportQuickAccountCSV"]'))
                )
                print(f"✅ Found download button for page {page}!")

                # ✅ Click the button to download CSV
                download_button.click()
                print(f"✅ Download started for page {page}...")

                # ✅ Wait for the file to appear
                time.sleep(5)  # Increase if needed for slower downloads

                # ✅ Get the latest file and rename it
                latest_file = get_latest_csv(download_dir)
                if latest_file:
                    new_filename = os.path.join(download_dir, f"export-accounts-{page}.csv")
                    os.rename(latest_file, new_filename)
                    print(f"✅ Renamed file to {new_filename}")

            except TimeoutException:
                print(f"❌ Error: 'Download Page Data' button not found on page {page}.")
                continue

        except NoSuchElementException:
            print(f"❌ Error: Page structure changed. Could not find elements on page {page}.")

    print("✅ All downloads completed!")
    driver.quit()


if __name__ == "__main__":
    num_accounts = 201  # ✅ Number of accounts to download

    DownloadCSV(num_accounts)
