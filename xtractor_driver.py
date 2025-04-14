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

# Check if user-data-dir and URL file are provided as command-line arguments
if len(sys.argv) != 3:
    print("Usage: python xtractor_driver.py /path/to/your/custom/profile /path/to/url_list.txt")
    sys.exit(1)

# Get the user-data-dir and URL file from command-line arguments
profile_path = sys.argv[1]
url_file_path = sys.argv[2]

# Verify if the provided profile directory exists
if not os.path.exists(profile_path):
    print(f"Error: Directory {profile_path} does not exist.")
    sys.exit(1)

# Verify if the provided URL file exists
if not os.path.isfile(url_file_path):
    print(f"Error: File {url_file_path} does not exist.")
    sys.exit(1)

# Read URLs from the file
with open(url_file_path, 'r') as file:
    urls = [line.strip() for line in file if line.strip()]

if not urls:
    print("Error: The URL file is empty.")
    sys.exit(1)

# Set up TinyDB
db_file = "posts.json"
db = TinyDB(db_file)
Post = Query()

# Set Firefox options
firefox_options = Options()
firefox_options.add_argument("-profile")
firefox_options.add_argument(profile_path)

try:
    # Initialize WebDriver
    driver = webdriver.Firefox(options=firefox_options)

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

    # Process each URL
    for url in urls:
        print(f"\nProcessing {url}...")
        
        # Check if URL already exists in the database
        if db.search(Post.url == url):
            print(f"Skipping {url}: Already exists in database.")
            continue

        post_data = {"url": url, "error": None}
        try:
            driver.get(url)
            
            # Wait for the post to load
            post_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'article[data-testid="tweet"]'))
            )

            # Extract post details
            try:
                # Profile handle
                handle = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="User-Name"] a[href*="/"]').text
                post_data["handle"] = handle
                # Sanitize handle for filename
                handle_safe = handle.replace('@', '').replace('/', '_')

                # Date and time
                datetime_elem = driver.find_element(By.CSS_SELECTOR, 'time')
                post_datetime = datetime_elem.get_attribute('datetime')
                post_data["datetime"] = post_datetime

                # Post content
                content_elem = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="tweetText"]')
                content = content_elem.text
                post_data["content"] = content

                # Stats (likes, reposts, comments, views)
                stats = driver.find_elements(By.CSS_SELECTOR, 'div[role="group"] [data-testid*="count"]')
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

                # Extract post ID from URL
                post_id = re.search(r'status/(\d+)', url)
                post_id = post_id.group(1) if post_id else "unknown"
                post_data["post_id"] = post_id

                # Take screenshot of the post
                screenshot_path = None
                try:
                    # Get post element's location and size
                    location = post_element.location
                    size = post_element.size

                    # Take full-page screenshot
                    screenshot = driver.get_screenshot_as_png()
                    image = Image.open(BytesIO(screenshot))

                    # Calculate crop coordinates
                    left = location['x']
                    top = location['y']
                    right = left + size['width']
                    bottom = top + size['height']

                    # Crop to post area
                    cropped_image = image.crop((left, top, right, bottom))

                    # Save screenshot as PNG
                    screenshot_filename = f"post_{handle_safe}_{post_id}.png"
                    cropped_image.save(screenshot_filename)
                    screenshot_path = os.path.abspath(screenshot_filename)
                    print(f"Screenshot saved as {screenshot_filename}")

                except Exception as e:
                    print(f"Error capturing screenshot for {url}: {str(e)}")
                    post_data["error"] = f"Screenshot failed: {str(e)}"

                post_data["screenshot_path"] = screenshot_path

                # Check if the post is a reply and extract parent post details
                try:
                    parent_post_element = driver.find_element(By.CSS_SELECTOR, 'article[data-testid="tweet"][role="group"]')
                    parent_post_data = {}

                    # Extract parent post details
                    parent_handle = parent_post_element.find_element(By.CSS_SELECTOR, 'div[data-testid="User-Name"] a[href*="/"]').text
                    parent_post_data["handle"] = parent_handle

                    parent_datetime_elem = parent_post_element.find_element(By.CSS_SELECTOR, 'time')
                    parent_post_datetime = parent_datetime_elem.get_attribute('datetime')
                    parent_post_data["datetime"] = parent_post_datetime

                    parent_content_elem = parent_post_element.find_element(By.CSS_SELECTOR, 'div[data-testid="tweetText"]')
                    parent_content = parent_content_elem.text
                    parent_post_data["content"] = parent_content

                    # Extract stats for the parent post
                    parent_stats = parent_post_element.find_elements(By.CSS_SELECTOR, 'div[role="group"] [data-testid*="count"]')
                    parent_post_data["likes"] = "0"
                    parent_post_data["reposts"] = "0"
                    parent_post_data["comments"] = "0"
                    parent_post_data["views"] = "0"

                    for stat in parent_stats:
                        aria_label = stat.get_attribute('aria-label')
                        if aria_label:
                            if "reply" in aria_label.lower() or "comment" in aria_label.lower():
                                parent_post_data["comments"] = stat.text if stat.text else "0"
                            elif "repost" in aria_label.lower() or "retweet" in aria_label.lower():
                                parent_post_data["reposts"] = stat.text if stat.text else "0"
                            elif "like" in aria_label.lower():
                                parent_post_data["likes"] = stat.text if stat.text else "0"
                            elif "view" in aria_label.lower():
                                parent_post_data["views"] = stat.text if stat.text else "0"

                    # Take a screenshot of the parent post
                    parent_location = parent_post_element.location
                    parent_size = parent_post_element.size

                    screenshot = driver.get_screenshot_as_png()
                    image = Image.open(BytesIO(screenshot))

                    left = parent_location['x']
                    top = parent_location['y']
                    right = left + parent_size['width']
                    bottom = top + parent_size['height']

                    parent_cropped_image = image.crop((left, top, right, bottom))
                    parent_screenshot_filename = f"parent_post_{parent_handle.replace('@', '').replace('/', '_')}.png"
                    parent_cropped_image.save(parent_screenshot_filename)
                    parent_post_data["screenshot_path"] = os.path.abspath(parent_screenshot_filename)

                    print(f"Parent post screenshot saved as {parent_screenshot_filename}")
                    post_data["parent_post"] = parent_post_data

                except NoSuchElementException:
                    print("No parent post found or failed to extract parent post details.")

                # Print extracted data
                print(f"Handle: {handle}")
                print(f"Date/Time: {post_datetime}")
                print(f"Content: {content}")
                print(f"Likes: {post_data['likes']}")
                print(f"Reposts: {post_data['reposts']}")
                print(f"Comments: {post_data['comments']}")
                print(f"Views: {post_data['views']}")

            except NoSuchElementException as e:
                print(f"Error extracting data for {url}: Some elements not found. Skipping...")
                post_data["error"] = f"Extraction failed: {str(e)}"

            # Insert post data into TinyDB
            db.insert(post_data)

        except TimeoutException:
            print(f"Error: Could not load post at {url}. Skipping...")
            post_data["error"] = "Failed to load post"
            db.insert(post_data)

        # Small delay to avoid overwhelming the server
        time.sleep(1)

finally:
    # Close the browser
    driver.quit()
    print(f"\nAll data saved to {db_file}")