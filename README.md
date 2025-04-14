# XtractorDriver

XtractorDriver is a tool designed to help researchers save and analyze content from X/Twitter posts. The workflow involves bookmarking posts in a specific folder, exporting bookmarks as an HTML file, extracting URLs from the folder, and then using a Selenium-based script to save post content and screenshots.

## Features

- Extract URLs from a specific folder in a browser's exported bookmarks file.
- Save post content, metadata (likes, reposts, comments, views), and screenshots from X/Twitter posts.
- Store extracted data in a TinyDB database (`posts.json`).

---

## Setup Instructions

### Prerequisites

1. **Python**: Ensure Python 3.7+ is installed on your system.
2. **Firefox**: Install Mozilla Firefox.
3. **Geckodriver**: Download and install [Geckodriver](https://github.com/mozilla/geckodriver/releases) for Selenium.
4. **Python Libraries**: Install required libraries using `pip`:
   ```sh
   pip install selenium tinydb beautifulsoup4 pillow
   ```

---

### Setting Up Firefox for XtractorDriver

1. **Create a New Firefox Profile**:
   - Open Firefox and navigate to `about:profiles`.
   - Click "Create a New Profile" and follow the prompts to create a new profile (e.g., `XtractorProfile`).
   - Note the directory path of the new profile.

2. **Open Firefox with the New Profile**:
   - Close all Firefox windows.
   - Start Firefox with the new profile:
     ```sh
     firefox -P
     ```
   - Select the newly created profile.

3. **Log In to X/Twitter**:
   - Navigate to [https://x.com](https://x.com) and log in to your account.
   - Ensure you remain logged in for the session.

---

## Usage Instructions

### Step 1: Bookmark Posts on X/Twitter

1. Bookmark the posts you want to save in a specific folder (e.g., `Research`).

---

### Step 2: Export Bookmarks as an HTML File

1. Open your browser's bookmarks manager.
2. Export your bookmarks to an HTML file (e.g., `bookmarks.html`).

---

### Step 3: Extract URLs from the Bookmarks File

1. Run the [`extract_bookmarks.py`](extract_bookmarks.py) script to extract URLs from the desired folder:
   ```sh
   python extract_bookmarks.py <bookmark_file.html> <folder_name> <output_file.txt>
   ```
   - Replace `<bookmark_file.html>` with the path to your exported bookmarks file.
   - Replace `<folder_name>` with the name of the folder containing the bookmarks (e.g., `Research`).
   - Replace `<output_file.txt>` with the desired output file name (e.g., `urls.txt`).

2. Example:
   ```sh
   python extract_bookmarks.py bookmarks.html Research urls.txt
   ```

---

### Step 4: Run XtractorDriver

1. Use the [`xtractor_driver.py`](xtractor_driver.py) script to process the extracted URLs:
   ```sh
   python xtractor_driver.py /path/to/your/custom/profile /path/to/url_list.txt
   ```
   - Replace `/path/to/your/custom/profile` with the directory path of the Firefox profile created earlier.
   - Replace `/path/to/url_list.txt` with the path to the file containing the extracted URLs (e.g., `urls.txt`).

2. Example:
   ```sh
   python xtractor_driver.py /Users/yourname/.mozilla/firefox/xyz123.XtractorProfile urls.txt
   ```

3. The script will:
   - Save post content and metadata in `posts.json`.
   - Save screenshots of posts in the current directory.

---

## Notes

- **Delay Between Requests**: The script includes a small delay to avoid overwhelming X/Twitter's servers.
- **Error Handling**: Posts that fail to load or extract data will be logged with an error message in the database.

---

## Troubleshooting

- **Geckodriver Not Found**: Ensure `geckodriver` is installed and added to your system's PATH.
- **Login Issues**: Ensure you are logged into X/Twitter using the custom Firefox profile.
- **Empty URL File**: Verify that the folder name provided to [`extract_bookmarks.py`](extract_bookmarks.py) matches the folder in your bookmarks.

---

## License

This project is licensed under the MIT License.