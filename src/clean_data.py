import pandas as pd

# Load the scraped data from the CSV file in the 'data' directory (one level up)
df = pd.read_csv('./data/character_data_with_images.csv')

# Print initial data
print("Initial Data:")
print(df.head())

# Step 2: Clean the data

# 1. Clean Character Names
# Remove any extra spaces or newline characters from the character names
df['name'] = df['name'].str.strip()

# 2. Handle Missing or Empty Values

# Check for missing values in the 'name', 'url', and 'image_url' columns
print("\nMissing values before cleaning:")
print(df.isnull().sum())

# Optionally, drop rows with missing 'name' or 'url' since they are essential
df.dropna(subset=['name', 'url'], inplace=True)

# If the image URL is missing, set it to a placeholder or mark it for later
df['image_url'].fillna('https://example.com/placeholder.png', inplace=True)

# 3. Validate and Clean URLs
# Ensure URLs are well-formed (start with 'http' or 'https')
def validate_url(url):
    if not url.startswith('http'):
        return 'https://example.com/invalid-url'
    return url

df['url'] = df['url'].apply(validate_url)
df['image_url'] = df['image_url'].apply(validate_url)

# Step 3: Save the cleaned data into the 'data' directory
df.to_csv('./data/cleaned_character_data.csv', index=False)

# Print cleaned data
print("\nCleaned Data:")
print(df.head())
print("\nMissing values after cleaning:")
print(df.isnull().sum())
