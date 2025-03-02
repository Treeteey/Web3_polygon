import os
import sys
import time
import glob
import shutil  # Used for deleting the folder
import csv
import re  # ✅ Import regex module
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
    """Check for available browsers on Windows and Linux."""
    if sys.platform.startswith("win"):
        possible_browsers = {
            "chrome": "C:/Program Files/Google/Chrome/Application/chrome.exe",
            "edge": "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
            "firefox": "C:/Program Files/Mozilla Firefox/firefox.exe",
            "yandex": f"C:/Users/{os.getlogin()}/AppData/Local/Yandex/YandexBrowser/Application/browser.exe"
        }
    elif sys.platform.startswith("linux"):
        possible_browsers = {
            "chrome": "/usr/bin/google-chrome",
            "chromium": "/usr/bin/chromium-browser",
            "firefox": "/usr/bin/firefox",
            "yandex": "/usr/bin/yandex-browser"
        }
    else:
        print("❌ Unsupported OS. This script only works on Windows and Linux.")
        sys.exit(1)

    for browser, path in possible_browsers.items():
        if os.path.exists(path):
            return browser, path

    return None, None



def get_driver():
    """Get WebDriver for the available browser."""
    browser, binary_path = find_browser()

    # ✅ Set OS-specific download directory
    if sys.platform.startswith("win"):
        download_dir = os.path.join(os.getcwd(), "top_accounts")
    elif sys.platform.startswith("linux"):
        download_dir = os.path.join(os.path.expanduser("~"), "top_accounts")

    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    if not browser:
        print("❌ No supported browser found. Please install Chrome, Edge, Firefox, or Yandex Browser.")
        sys.exit(1)

    print(f"✅ Using {browser.capitalize()} browser...")

    options = None
    service = None

    if browser in ["chrome", "chromium"]:
        options = webdriver.ChromeOptions()
        options.binary_location = binary_path

        # ✅ Set custom download folder
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

        # ✅ Set custom download folder for Firefox
        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.download.folderList", 2)  # Use custom folder
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


def DownloadCSV(num_accounts, pages=None):
    """
    Open Polygonscan and download the CSV files for the requested number of accounts.
    - If pages=None, download all pages required for num_accounts.
    - If pages is a list, download only missing pages.
    """
    driver = get_driver()  # ✅ Browser is now visible
    download_dir = os.path.join(os.getcwd(), "top_accounts")

    accounts_per_page = 100
    num_pages = (num_accounts + accounts_per_page - 1) // accounts_per_page  # Round up

    if pages is None:
        pages = range(1, num_pages + 1)  # ✅ Download all pages

    print(f"✅ Need to download {len(pages)} pages for {num_accounts} accounts.")

    for page in sorted(pages):
        url = f"https://polygonscan.com/accounts/{page}?ps=100"
        print(f"🌍 Opening: {url}")

        driver.get(url)

        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            driver.execute_script("window.scrollBy(0, 500);")

            try:
                download_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="btnExportQuickAccountCSV"]'))
                )
                print(f"✅ Found download button for page {page}!")

                download_button.click()
                print(f"✅ Download started for page {page}...")

                time.sleep(5)

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



def get_top(N):
    """
    Get the top N addresses sorted by balance from the downloaded CSV files.
    - If files are older than 5 minutes, re-download all.
    - If files are fresh but missing pages, download only missing pages.
    """
    download_dir = os.path.join(os.getcwd(), "top_accounts")

    # ✅ If folder doesn't exist, create it
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    # ✅ Check if files exist
    csv_files = sorted([f for f in os.listdir(download_dir) if f.endswith(".csv")])

    if csv_files:
        # ✅ Check if files were modified in the last 5 minutes
        newest_file = max([os.path.getmtime(os.path.join(download_dir, f)) for f in csv_files])
        file_age_minutes = (time.time() - newest_file) / 60

        if file_age_minutes > 5:
            print("🕒 CSV files are older than 5 minutes. Downloading fresh data...")
            shutil.rmtree(download_dir)  # ✅ Delete old files
            os.makedirs(download_dir)
            DownloadCSV(N)
        else:
            print("✅ CSV files are fresh! Checking if more pages are needed...")

    else:
        print("🚀 No existing files found. Downloading fresh data...")
        DownloadCSV(N)

    # ✅ Calculate how many pages are needed
    existing_pages = {int(f.split("-")[-1].split(".")[0]) for f in csv_files} if csv_files else set()
    required_pages = set(range(1, (N + 99) // 100 + 1))

    missing_pages = required_pages - existing_pages

    if missing_pages:
        print(f"📌 Missing pages: {sorted(missing_pages)}. Downloading only missing pages...")
        DownloadCSV(N, pages=list(missing_pages))

    # ✅ Now process all CSV files
    account_balances = []

    csv_files = sorted([f for f in os.listdir(download_dir) if f.endswith(".csv")])

    for file in csv_files:
        file_path = os.path.join(download_dir, file)
        print(f"📂 Processing: {file_path}")

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)  # ✅ Skip header

            for row in reader:
                if len(row) < 3:
                    continue

                address = row[1].strip()
                balance_str = row[2].replace(",", "").strip()

                match = re.search(r"\d+(\.\d+)?", balance_str)
                if match:
                    try:
                        balance = float(match.group())
                        account_balances.append((address, balance))
                    except ValueError:
                        print(f"❌ Error converting balance '{balance_str}'. Skipping...")
                        continue
                else:
                    print(f"⚠️ No valid number found in '{balance_str}'. Skipping...")

    # ✅ Sort by balance and return the top N
    top_accounts = sorted(account_balances, key=lambda x: x[1], reverse=True)[:N]

    return top_accounts



if __name__ == "__main__":
    num_accounts = 201  # ✅ Number of accounts to download

    DownloadCSV(num_accounts)
