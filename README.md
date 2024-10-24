# Fandom ETL

## Setup
```
conda create --name torch-env python=3.9
conda activate torch-env
conda install pytorch torchvision torchaudio -c pytorch
pip install beautifulsoup4 requests sentence-transformers pinecone-client pandas
```

## Steps

1. Crawl all character pages
```
python src/scrape_characters.py
```

2. Clean data
```
python src/clean_data.py
```

3. Scrape each character page into CSV files
```
python src/scrape_character_pages.py
```

4. Clean CSV files
```
python src/clean_csv_files.py
```

5. CSV to JSON
```
python src/csv_to_json.py
```

6. Remove empty fields
```
python src/remove_keys.py
```

7. Rename firt KV pair (name):
```
python src/update_name_kv.py
```

8. Delete first KV pair (now that it has been copied):
```
python src/delete_first_kv.py
```

9. Upsert to Pinecone (vector DB):
```
python src/upsert.py
```