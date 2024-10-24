import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL to scrape character links from
base_url = 'https://walkingdead.fandom.com'
url = f'{base_url}/wiki/TV_Series_Characters'

# Fetch the main page
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Find the correct section containing character tables
character_links = []

# Find all 'td' elements that contain the character links and images
td_elements = soup.find_all('td')

for td in td_elements:
    # Find the link to the character page
    a_tag = td.find('a', href=True)
    if a_tag and '/wiki/' in a_tag['href']:
        # Extract character link and full URL
        character_link = base_url + a_tag['href']
        character_name = a_tag['title']

        # Find the character image in the same 'td' element
        img_tag = td.find('img')
        if img_tag:
            character_image_url = img_tag.get('data-src') or img_tag.get('src')

            # Store the character data
            character_links.append({
                'name': character_name,
                'url': character_link,
                'image_url': character_image_url
            })

# Convert the scraped character data into a pandas DataFrame
df = pd.DataFrame(character_links)

# Save to a CSV file in the 'data' directory
df.to_csv('./data/character_data_with_images.csv', index=False)

print("Character data saved to ./data/character_data_with_images.csv")
