import json
import requests
from datetime import datetime
import os
import sys

# Load WordPress site details from an external configuration file
def load_config(config_file_path):
    try:
        with open(config_file_path, 'r') as config_file:
            config = json.load(config_file)
            return config
    except Exception as e:
        print(f"Error loading configuration file: {str(e)}")
        sys.exit(1)

# Function to upload an image and return its ID
def upload_image(image_path, wp_api_url, auth):
    try:
        # Open the image file in binary mode
        with open(image_path, 'rb') as img:
            # Prepare the file for upload
            filename = os.path.basename(image_path)
            files = {
                'file': (filename, img, 'image/png')  # Adjust MIME type if needed (e.g., 'image/jpeg')
            }
            headers = {
                'Content-Disposition': f'attachment; filename={filename}'
            }
            
            # Upload the image to WordPress media library
            response = requests.post(
                f"{wp_api_url}/media",
                headers=headers,
                auth=auth,
                files=files
            )
            
            if response.status_code == 201:
                # Return the media ID of the uploaded image
                return response.json()['id']
            else:
                print(f"Failed to upload image {image_path}: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        print(f"Error uploading image {image_path}: {str(e)}")
        return None

# Function to create a WordPress post
def create_post(title, content, featured_image_id, metadata, wp_api_url, auth):
    # Prepare the post data
    post_data = {
        'title': title,
        'content': f"{content}\n\n<ul>\n{metadata}\n</ul>",  # Add metadata as a UL list
        'status': 'publish',  # Set to 'draft' if you want to review before publishing
    }
    
    # If a featured image ID is provided, set it
    if featured_image_id:
        post_data['featured_media'] = featured_image_id
    
    # Create the post via the WordPress REST API
    try:
        response = requests.post(
            f"{wp_api_url}/posts",
            auth=auth,
            json=post_data
        )
        
        if response.status_code == 201:
            print(f"Successfully created post: {title}")
        else:
            print(f"Failed to create post: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error creating post: {str(e)}")

# Main function to process the JSON file
def process_json_file(json_file_path, wp_api_url, auth):
    # Read the JSON file
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON file: {str(e)}")
        return

    # Process each post in the JSON data
    for post_id, post_data in data.get('_default', {}).items():
        # Extract post details
        handle = post_data.get('handle', 'Unknown')
        content = post_data.get('content', '')
        datetime_str = post_data.get('datetime', '')
        screenshot_file = post_data.get('screenshot_file', '')
        url = post_data.get('url', '')
        likes = post_data.get('likes', '0')
        reposts = post_data.get('reposts', '0')
        comments = post_data.get('comments', '0')
        views = post_data.get('views', '0')

        # Format the date (mm/dd/yyyy)
        try:
            post_date = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.000Z")
            formatted_date = post_date.strftime("%m/%d/%Y")
        except ValueError:
            formatted_date = "Unknown Date"

        # Create the post title
        post_title = f"Post by {handle} {formatted_date}"

        # Create the metadata list in HTML UL format
        metadata = (
            f"<li>URL: <a href='{url}'>{url}</a></li>"
            f"<li>Likes: {likes}</li>"
            f"<li>Reposts: {reposts}</li>"
            f"<li>Comments: {comments}</li>"
            f"<li>Views: {views}</li>"
        )

        # Upload the screenshot as the featured image
        featured_image_id = None
        if screenshot_file and os.path.exists(screenshot_file):
            featured_image_id = upload_image(screenshot_file, wp_api_url, auth)
        else:
            print(f"Screenshot file {screenshot_file} not found for post {post_id}")

        # Create the WordPress post
        create_post(post_title, content, featured_image_id, metadata, wp_api_url, auth)

# Run the script
if __name__ == "__main__":
    # Check if the JSON file path is provided as a command-line argument
    if len(sys.argv) != 3:
        print("Usage: python wordpress_import.py <config.json> <posts.json>")
        sys.exit(1)

    # Load configuration
    config_file_path = sys.argv[1]  # Path to your configuration file
    json_file_path = sys.argv[2]   # Path to the JSON file containing post data

    config = load_config(config_file_path)

    # Extract WordPress details from the configuration
    WP_URL = config.get("WP_URL")
    WP_USERNAME = config.get("WP_USERNAME")
    WP_APP_PASSWORD = config.get("WP_APP_PASSWORD")

    if not WP_URL or not WP_USERNAME or not WP_APP_PASSWORD:
        print("Error: Missing WordPress configuration details in the config file.")
        sys.exit(1)

    WP_API_URL = f"{WP_URL}/wp-json/wp/v2"
    auth = (WP_USERNAME, WP_APP_PASSWORD)

    # Process the JSON file
    process_json_file(json_file_path, WP_API_URL, auth)