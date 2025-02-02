import os
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Load the CSV with character links
df = pd.read_csv('./data/cleaned_character_data.csv')

# Ensure the directory for storing text files exists
output_dir = './data/character_data'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Function to scrape character page and save it as a text file
def scrape_and_save_character_page(name, url):
    try:
        # Fetch the character page content
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to retrieve page for {name}. Status code: {response.status_code}")
            return

        # Parse the page with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Focus on the content inside the mw-parser-output div
        content_section = soup.find('div', {'class': 'mw-parser-output'})
        if not content_section:
            print(f"No content section found for {name}")
            return

        # Initialize a dictionary to store section content
        sections = {}

        # Iterate over all <h2> tags to find sections
        for header in content_section.find_all('h2'):
            section_title = header.get_text().strip()
            section_content = []

            # Get the next siblings until the next <h2> or end of the section
            for sibling in header.find_next_siblings():
                if sibling.name == 'h2':
                    break
                if sibling.name in ['p', 'ul', 'dl']:
                    section_content.append(sibling.get_text(separator='\n').strip())

            # Store the section content in the dictionary
            sections[section_title] = '\n'.join(section_content)

        # Save the sections to a CSV file
        output_path = os.path.join(output_dir, f"{name.replace(' ', '_')}.csv")
        pd.DataFrame([sections]).to_csv(output_path, index=False)
        
        print(f"Successfully saved {name}'s page content to {output_path}")

    except Exception as e:
        print(f"Error scraping {name}: {e}")

# Loop through each character in the CSV
for index, row in df.iterrows():
    character_name = row['name']
    character_url = row['url']

    print(f"Scraping page for {character_name}...")
    scrape_and_save_character_page(character_name, character_url)

print("Scraping complete.")
