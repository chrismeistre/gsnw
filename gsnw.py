'''
    This script currently "JUST WORKS"
    Nothing fancy yet.
    Enjoy :)
'''
import time
import logging
from pathlib import Path
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

# Banner
banner = '''
---------------------------------
GSNW
Find me on X (Twitter) @retkoussa
---------------------------------
'''

# Disable logging for Selenium and other verbose outputs
logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

# Dedicated profile directory — separate from the user's main Chrome profile
# so it never conflicts with a running Chrome instance.
GSNW_PROFILE_DIR = Path.home() / ".config" / "gsnw" / "chrome-profile"


def clean_stale_locks(profile_dir):
    """Remove stale Chrome lock files left behind by a previous crash."""
    for name in ["SingletonLock", "SingletonSocket", "SingletonCookie"]:
        lock = profile_dir / name
        if lock.exists() or lock.is_symlink():
            lock.unlink(missing_ok=True)


def login_to_github():
    """Launch a visible Chrome window so the user can log into GitHub."""
    GSNW_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    clean_stale_locks(GSNW_PROFILE_DIR)

    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"--user-data-dir={GSNW_PROFILE_DIR}")
    chrome_options.add_argument("--log-level=3")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://github.com/login")
    print("A Chrome window has been opened.")
    print("Please log into GitHub in the browser window (including MFA if prompted)...")
    print("Waiting for login to complete...")

    # Wait up to 5 minutes for the user to fully log in (including MFA)
    for _ in range(150):
        time.sleep(2)
        try:
            # GitHub sets a meta tag with the username when logged in
            user_meta = driver.execute_script(
                "var el = document.querySelector('meta[name=\"user-login\"]');"
                "return el ? el.getAttribute('content') : null;"
            )
            if user_meta:
                print(f"Logged in as: {user_meta}")
                break
        except Exception:
            # Browser was closed manually
            print("Browser closed.")
            return

    print("Login detected! Saving session...")
    driver.quit()
    print("Login saved. You can now run searches.")


def search_github(query, ext=None):
    matched_words = set()  # Use a set to store unique matched words
    page_number = 1
    search_q = f"path%3A%2F{query}"
    if ext:
        ext = ext.lstrip(".")
        search_q += f"+path%3A*.{ext}"
    base_url = f"https://github.com/search?q={search_q}&type=code&p="

    GSNW_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    clean_stale_locks(GSNW_PROFILE_DIR)

    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"--user-data-dir={GSNW_PROFILE_DIR}")
    chrome_options.add_argument("--log-level=3")

    # Selenium 4.6+ handles driver management automatically
    driver = webdriver.Chrome(options=chrome_options)

    while True:
        # Construct the URL for the current page
        url = f"{base_url}{page_number}"
        driver.get(url)

        try:
            # Detect "sign in" prompt — means user hasn't logged in yet
            sign_in = driver.find_elements(By.XPATH, "//*[contains(text(), 'Sign in to search code')]")
            if sign_in:
                print("Error: Not logged into GitHub.")
                print("Run with --login first to authenticate:")
                print("  python gsnw.py --login")
                break

            # Wait until the elements are located or timeout after 10 seconds
            elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".search-title a[href*='/blob/']"))
            )

            if elements:
                for element in elements:
                    try:
                        path = element.text
                        segments = path.split('/')
                        for segment in segments:
                            if query.lower() in segment.lower() and segment not in matched_words:
                                print(f"\t[x] {segment}")
                                matched_words.add(segment)

                    except StaleElementReferenceException:
                        print("Encountered a stale element, continuing...")
            else:
                print(f"Error: No elements found on page {page_number}")
                break

            # Check if there are no results for the next page
            no_results_message = driver.find_elements(By.XPATH, "//h3[contains(text(), 'Your search did not match any')]")
            if no_results_message:
                break

            # Increment the page number for the next iteration
            page_number += 1
            time.sleep(2)  # Add a short delay to avoid making requests too quickly
        except Exception:
            # Timeout means no more results on this page
            break

    driver.quit()
    return list(matched_words)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("search_query", nargs='?', default=None, help="The search query to use for GitHub code search")
    parser.add_argument("output_file", nargs='?', default=None, help="The output file to save the results")
    parser.add_argument("-silent", action="store_true", help="Suppress the banner")
    parser.add_argument("-e", "--ext", default=None, help="Filter by file extension (e.g. aspx, config, php)")
    parser.add_argument("--login", action="store_true", help="Open a browser to log into GitHub")

    args = parser.parse_args()

    if not args.silent:
        print(banner)

    if args.login:
        login_to_github()
        return

    if not args.search_query:
        parser.error("search_query is required (or use --login to authenticate)")

    matched_words = search_github(args.search_query, ext=args.ext)

    if args.output_file:
        with open(args.output_file, "w") as file:
            for word in matched_words:
                file.write(word + "\n")
    else:
        print('-------------------------')
        for word in matched_words:
            print(word)
        print('-------------------------')


if __name__ == "__main__":
    main()
