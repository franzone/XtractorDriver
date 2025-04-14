import sys
from bs4 import BeautifulSoup
import re

def extract_folder_urls(file_path, folder_name):
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    def find_folder(soup, folder_name):
        print(f"Searching for folder: {folder_name}")
        # Use a case-insensitive regex to find the <h3> tag with the folder name
        folder = soup.find("h3", string=re.compile(re.escape(folder_name), re.IGNORECASE))
        if folder:
            return folder.find_next_sibling("dl")
        return None

    # Find the folder
    folder_dl = find_folder(soup, folder_name)

    if not folder_dl:
        print(f"Folder '{folder_name}' not found.")
        return []

    # Extract URLs from the folder
    urls = []
    for dt in folder_dl.find_all("dt", recursive=True):
        a = dt.find("a")
        if a and a.has_attr("href"):
            urls.append(a["href"])

    # Return only unique URLs
    return list(set(urls))

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python extract_bookmarks.py <bookmark_file.html> <folder_name> <output_file.txt>")
        sys.exit(1)

    print("Starting extraction...")
    print("Arguments provided:", sys.argv)
    file_path = sys.argv[1]
    folder_name = sys.argv[2]
    output_file = sys.argv[3]

    # Extract URLs
    urls = extract_folder_urls(file_path, folder_name)

    if urls:
        # Write unique URLs to the output file
        with open(output_file, 'w', encoding='utf-8') as f:
            for url in sorted(urls):  # Sort URLs for consistent output
                f.write(url + '\n')
        print(f"Extracted {len(urls)} unique URLs to '{output_file}'.")
    else:
        print(f"No URLs found in folder '{folder_name}'.")