import sys
import os
from tinydb import TinyDB, Query
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from PIL import Image
from io import BytesIO
import time
import re


def read_urls(url_file_path):
    """Read URLs from the provided file."""
    if not os.path.isfile(url_file_path):
        print(f"Error: File {url_file_path} does not exist.")
        sys.exit(1)

    with open(url_file_path, 'r') as file:
        urls = [line.strip() for line in file if line.strip()]

    if not urls:
        print("Error: The URL file is empty.")
        sys.exit(1)

    return urls


def setup_firefox_driver(profile_path):
    """Set up the Firefox WebDriver with the specified profile."""
    if not os.path.exists(profile_path):
        print(f"Error: Directory {profile_path} does not exist.")
        sys.exit(1)

    firefox_options = Options()
    firefox_options.add_argument("-profile")
    firefox_options.add_argument(profile_path)

    driver = webdriver.Firefox(options=firefox_options)
    return driver


def extract_post_details(driver, post_element, images_dir, post_id_suffix=""):
    """
    Extract details of a post and take a full-page screenshot.
    :param driver: Selenium WebDriver instance
    :param post_element: WebElement representing the post
    :param images_dir: Directory to save screenshots
    :param post_id_suffix: Optional suffix for the screenshot filename
    :return: Dictionary containing post details
    """
    post_data = {}

    try:
        # Extract handle
        handle = post_element.find_element(By.CSS_SELECTOR, 'div[data-testid="User-Name"] a[href*="/"]').text
        post_data["handle"] = handle

        # Extract datetime
        datetime_elem = post_element.find_element(By.CSS_SELECTOR, 'time')
        post_datetime = datetime_elem.get_attribute('datetime')
        post_data["datetime"] = post_datetime

        # Extract content
        content_elem = post_element.find_element(By.CSS_SELECTOR, 'div[data-testid="tweetText"]')
        content = content_elem.text
        post_data["content"] = content

        # Extract stats (likes, reposts, comments, views)
        stats = post_element.find_elements(By.CSS_SELECTOR, 'div[role="group"] [data-testid*="count"]')
        post_data["likes"] = "0"
        post_data["reposts"] = "0"
        post_data["comments"] = "0"
        post_data["views"] = "0"

        for stat in stats:
            aria_label = stat.get_attribute('aria-label')
            if aria_label:
                if "reply" in aria_label.lower() or "comment" in aria_label.lower():
                    post_data["comments"] = stat.text if stat.text else "0"
                elif "repost" in aria_label.lower() or "retweet" in aria_label.lower():
                    post_data["reposts"] = stat.text if stat.text else "0"
                elif "like" in aria_label.lower():
                    post_data["likes"] = stat.text if stat.text else "0"
                elif "view" in aria_label.lower():
                    post_data["views"] = stat.text if stat.text else "0"

        # Take full-page screenshot
        screenshot_filename = None
        try:
            # Capture full-page screenshot
            screenshot_filename = os.path.join(images_dir, f"{post_id_suffix}.png")
            driver.save_screenshot(screenshot_filename)
            print(f"Full-page screenshot saved to {screenshot_filename}")

        except Exception as e:
            print(f"Error capturing screenshot: {str(e)}")
            post_data["error"] = f"Screenshot failed: {str(e)}"

        post_data["screenshot_file"] = screenshot_filename

    except NoSuchElementException as e:
        print(f"Error extracting post details: {str(e)}")
        post_data["error"] = f"Extraction failed: {str(e)}"

    return post_data

def process_urls(driver, urls, db, images_dir):
    """Process the list of URLs and extract post details."""
    for url in urls:
        print(f"\nProcessing {url}...")

        # Check if URL already exists in the database
        existing_record = db.get(Query().url == url)
        if existing_record and not existing_record.get("error"):
            print(f"Skipping {url}: Already exists in database without errors.")
            continue
        elif existing_record and existing_record.get("error"):
            print(f"Reprocessing {url}: Previous attempt had an error.")

        post_data = {"url": url, "error": None}
        try:
            driver.get(url)

            # Wait for the post to load
            post_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'article[data-testid="tweet"]'))
            )

            # Extract original post details
            post_id = re.search(r'status/(\d+)', url)
            post_id = post_id.group(1) if post_id else "unknown"
            post_data.update(extract_post_details(driver, post_element, images_dir, post_id))

            # Check if the post is a reply and extract parent post details
            try:
                parent_post_element = driver.find_element(By.CSS_SELECTOR, 'article[data-testid="tweet"][role="group"]')
                parent_post_data = extract_post_details(driver, parent_post_element, images_dir, f"{post_id}_parent")
                post_data["parent_post"] = parent_post_data
            except NoSuchElementException:
                print("No parent post found or failed to extract parent post details.")

            # Remove the old record if it exists
            if existing_record:
                db.remove(Query().url == url)

            # Insert post data into TinyDB
            db.insert(post_data)

        except TimeoutException:
            print(f"Error: Could not load post at {url}. Skipping...")
            post_data["error"] = "Failed to load post"
            db.insert(post_data)

        # Small delay to avoid overwhelming the server
        time.sleep(3)


if __name__ == '__main__':
    # Check if user-data-dir and URL file are provided as command-line arguments
    if len(sys.argv) != 3:
        print("Usage: python xtractor_driver.py /path/to/your/custom/profile /path/to/url_list.txt")
        sys.exit(1)

    # Get the user-data-dir and URL file from command-line arguments
    profile_path = sys.argv[1]
    url_file_path = sys.argv[2]

    # Read URLs
    urls = read_urls(url_file_path)

    # Set up TinyDB
    db_file = "posts.json"
    db = TinyDB(db_file)

    # Define the directory to save screenshots
    images_dir = "images"
    os.makedirs(images_dir, exist_ok=True)

    # Initialize WebDriver
    driver = setup_firefox_driver(profile_path)

    try:
        # Check login status once at the start
        driver.get("https://x.com")
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="AppTabBar_Profile_Link"]'))
            )
            print("LOGGED IN!")
        except TimeoutException:
            print("Not logged in.")
            driver.quit()
            sys.exit(1)  # Exit if not logged in

        # Process URLs
        process_urls(driver, urls, db, images_dir)

    finally:
        # Close the browser
        driver.quit()
        print(f"\nAll data saved to {db_file}")
