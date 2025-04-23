# WordPress Import Script

## Overview

This Python script (`wordpress_import.py`) imports social media posts from a JSON file into a WordPress blog using the WordPress REST API. Each post is created with:

- A title in the format "Post by [handle] [mm/dd/yyyy]".
- The post content from the JSON file.
- A featured image (a screenshot uploaded from the specified file path).
- Metadata (e.g., URL, likes, reposts, comments, views) displayed as an HTML unordered list (`<ul>`) at the bottom of the post content.

The script is designed to be run from the command line, taking a configuration file and a JSON file as inputs.

## Requirements

To run this script, you need the following:

### Software
- **Python 3.6 or higher**: The script uses Python's standard libraries along with the `requests` library.
- **WordPress Site**: A WordPress site with the REST API enabled (this is enabled by default in modern WordPress installations).

### Python Dependencies
- **requests**: Used for making HTTP requests to the WordPress REST API.
  Install it using pip:
  ```bash
  pip install requests
  ```

### WordPress Setup
- **REST API Access**: Ensure your WordPress site has the REST API enabled.
- **Application Password**: You need a WordPress application password for authentication. Application passwords were introduced in WordPress 5.6 as a secure way to authenticate API requests.

## Setup

### 1. Clone or Download the Script
Download or clone this repository to your local machine. The main script is `wordpress_import.py`.

### 2. Install Python Dependencies
Install the required Python package (`requests`) using pip:
```bash
pip install requests
```

### 3. Prepare Your WordPress Site
1. **Enable REST API**: Ensure your WordPress site has the REST API enabled (this is typically enabled by default).
2. **Generate an Application Password**:
   - Log in to your WordPress admin panel.
   - Go to **Users > Profile**.
   - Scroll to the **Application Passwords** section.
   - Enter a name for the application (e.g., "Import Script") and click **Add New Application Password**.
   - Copy the generated password (it will look like a string of 24 characters, e.g., `abcd efgh ijkl mnop qrst uvwx`).
   - Note your WordPress username as well.

### 4. Prepare the JSON File
The script expects a JSON file containing the post data in the following format:
```json
{
    "_default": {
        "1": {
            "url": "https://x.com/CoreyJMahler/status/1830309275693945000",
            "error": null,
            "handle": "Corey J. Mahler",
            "datetime": "2024-09-01T18:18:31.000Z",
            "content": "I want every Jew to repent and cease to be a Jew. I do not want any Jews \u2014 including former \u2014 in my country. These are not incompatible or incoherent beliefs.",
            "likes": "0",
            "reposts": "0",
            "comments": "0",
            "views": "0",
            "screenshot_file": "images/1830309275693945000.png"
        }
    }
}
```
- Ensure the `screenshot_file` path points to a valid image file (e.g., `images/1830309275693945000.png`).
- The `images/` directory should be in the same directory as the script, or you should provide the correct relative or absolute path to the images.

### 5. Configure the Script
Create a configuration file (e.g., `config.json`) with your WordPress site details:
```json
{
    "WP_URL": "https://your-wordpress-site.com",
    "WP_USERNAME": "your-username",
    "WP_APP_PASSWORD": "your-app-password"
}
```
- **WP_URL**: The URL of your WordPress site (e.g., `https://example.com`).
- **WP_USERNAME**: Your WordPress username.
- **WP_APP_PASSWORD**: The application password you generated.

Place this `config.json` file in the same directory as the script.

## Usage

1. **Run the Script**:
   Use the following command to run the script, providing the paths to the configuration file and the JSON file:
   ```bash
   python wordpress_import.py config.json posts.json
   ```
   - `config.json`: Path to your configuration file.
   - `posts.json`: Path to the JSON file containing the post data.

2. **What Happens**:
   - The script loads the configuration from `config.json`.
   - It reads the post data from `posts.json`.
   - For each post in the JSON file:
     - It uploads the specified screenshot as a featured image to the WordPress media library.
     - It creates a new WordPress post with the title, content, featured image, and metadata.
   - Posts are published immediately (you can change the `status` to `'draft'` in the `create_post` function if you want to review them first).

3. **Output**:
   - The script prints status messages for each operation (e.g., "Successfully created post: Post by Corey J. Mahler 09/01/2024").
   - If there are errors (e.g., missing files, API failures), they will be printed to the console.

## Configuration Details

### JSON File Format
The JSON file (`posts.json`) must have the following structure:
- A top-level key `_default` containing a dictionary of posts.
- Each post has:
  - `url`: The URL of the original post.
  - `handle`: The author’s handle (e.g., "Corey J. Mahler").
  - `datetime`: The timestamp of the post in ISO format (e.g., `"2024-09-01T18:18:31.000Z"`).
  - `content`: The content of the post.
  - `likes`, `reposts`, `comments`, `views`: Engagement metrics (default to "0" if missing).
  - `screenshot_file`: The path to the screenshot image (e.g., `images/1830309275693945000.png`).

### Configuration File (`config.json`)
The configuration file must include:
- `WP_URL`: Your WordPress site URL.
- `WP_USERNAME`: Your WordPress username.
- `WP_APP_PASSWORD`: Your WordPress application password.

### Image Files
- The script assumes the screenshot files are PNGs (MIME type `image/png`). If your images are in a different format (e.g., JPEG), modify the `upload_image` function to use the correct MIME type (e.g., `image/jpeg`).

## Troubleshooting

- **Error: "Error loading configuration file"**
  - Ensure the `config.json` file exists and is correctly formatted.
  - Check the path provided in the command-line argument.

- **Error: "Screenshot file not found"**
  - Verify that the `screenshot_file` path in the JSON file points to a valid image file.
  - Ensure the `images/` directory is in the correct location relative to the script.

- **Error: "Failed to create post" or "Failed to upload image"**
  - Check your WordPress REST API credentials in `config.json`.
  - Ensure your WordPress site has the REST API enabled.
  - Verify that your application password is valid and has the necessary permissions.
  - Check for network issues or WordPress server errors (the script will print the response code and message).

- **Rate Limiting**
  - If you’re uploading many posts, WordPress might throttle API requests. Add a delay between requests by modifying the script (e.g., using `time.sleep(1)` after each post).

- **Authentication Issues**
  - If authentication fails, ensure your application password is correct and hasn’t been revoked.
  - Verify that your WordPress site supports application passwords (requires WordPress 5.6 or higher).

## Additional Notes

- **Security**:
  - Do not hardcode sensitive information (e.g., application passwords) in the script or configuration file in a production environment. Consider using environment variables or a secure vault solution.
  - Revoke the application password after use if it’s no longer needed.

- **Customization**:
  - You can modify the `create_post` function to set the post status to `'draft'` instead of `'publish'` if you want to review posts before publishing.
  - Adjust the metadata format in the `process_json_file` function to change how metadata is displayed in the post.

- **Error Handling**:
  - The script includes basic error handling. You may want to add more robust logging (e.g., to a file) or retry logic for failed API requests in a production environment.

- **Dependencies**:
  - The script uses only the `requests` library, which is lightweight and widely used. No additional WordPress-specific libraries are required.

## License

This script is provided as-is under the MIT License. Feel free to modify and distribute it as needed.

