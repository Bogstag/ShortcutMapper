"""
This script reads an HTML file containing keyboard shortcuts and converts them into a JSON format.

Usage:
    1. Place the HTML file containing the keyboard shortcuts in the same directory as this script.
    2. Run this script using a compatible Python interpreter.

The script uses the BeautifulSoup library to parse the HTML file and extract the keyboard shortcuts
It then converts the extracted data into a JSON format using the json module.

The resulting JSON data is saved to a file named 'githubjson' in the intermediate directory 
as this script.

Note: Make sure to have the BeautifulSoup and json modules installed before running this script.

Example:
    $ python parser_github_shortcut.py
"""
import json

from bs4 import BeautifulSoup

# Read the HTML file
with open('sources/github/raw/Keyboard shortcuts - GitHub Docs.html', 'r', encoding='utf-8') as file:
    html = file.read()

# Parse the HTML using BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

# Create a dictionary to store the data
data = {
    "name": "GitHub",
    "version": "2023",
    "default_context": "Global Context",
    "os": ["windows"],
    "contexts": {}
}

# Find the specific <div> tag
div_tag = soup.find(
    'div', class_='MarkdownContent_markdownBody__7_8Gt markdown-body')

# Find all <h2> tags within the <div> tag, excluding the first two
h2_tags = div_tag.find_all('h2')[2:]  # type: ignore

# Iterate over each <h2> tag
for h2 in h2_tags:
    # Create a dictionary to store the values for the current h2
    h2_values = {}

    # Find the sibling table element
    table = h2.find_next_sibling('table')

    # If a table element is found
    if table:
        # Find all <tr> elements within the table
        tr_tags = table.find_all('tr')

        # Iterate over each <tr> element
        for tr in tr_tags:
            # Find all <td> elements within the <tr> element
            td_tags = tr.find_all('td')

            # Check if the <tr> element has at least two <td> elements
            if len(td_tags) >= 2:
                # Get the content of the first <td> element
                value1 = td_tags[0].decode_contents()

                # Get the content of the second <td> element
                td2 = td_tags[1]
                value2 = td2.get_text(strip=True)

                # Check if the text starts with "For more information"
                if value2.startswith("For more information"):
                    # Find the first <a> tag within the <td> element
                    a_tag = td2.find('a')

                    # If an <a> tag is found, remove it from the text
                    if a_tag:
                        value2 = value2.replace(a_tag.get_text(strip=True), "")

                    # Remove the "For more information" text
                    value2 = value2.replace("For more information", "").strip()

                # Add the value1 and value2 to the h2_values dictionary
                h2_values[value2] = [value1]

    # Add the h2_values to the main data dictionary under the current h2
    data["contexts"][h2.get_text(strip=True)] = h2_values

# Define the output JSON file path
output_file = 'sources/github/intermediate/github.json'

# Save the data as JSON
with open(output_file, 'w') as file:
    json.dump(data, file, indent=4)

print(f"JSON file saved at {output_file}")
