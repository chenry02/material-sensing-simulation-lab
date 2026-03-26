import requests
import yaml
import os

# --- CHANGE THIS TO YOUR ACTUAL HAL ID ---
HAL_ID = "clement-henry" 
# -----------------------------------------

print(f"Fetching publications from HAL for {HAL_ID}...")

# Query the HAL API for your papers (asking specifically for the DOI and title)
url = f"https://api.archives-ouvertes.fr/search/?q=authIdHal_s:{HAL_ID}&fl=title_s,doiId_s,uri_s,producedDate_s&wt=json&rows=100&sort=producedDate_s desc"
response = requests.get(url)
data = response.json()

sources = []

# Check if we have papers
if 'response' in data and 'docs' in data['response']:
    for doc in data['response']['docs']:
        # We only want to give Manubot the papers that have a DOI attached to them in HAL
        if 'doiId_s' in doc:
            sources.append({"id": f"doi:{doc['doiId_s']}"})
        else:
            # If no DOI is available, we fall back to manual formatting using the HAL URL
            # By supplying the title and date manually, Manubot won't crash trying to guess them
            title = doc.get('title_s', ['Untitled'])[0]
            date = doc.get('producedDate_s', '2020-01-01')
            sources.append({
                "id": f"url:{doc['uri_s']}",
                "title": title,
                "date": date,
                "publisher": "HAL Archive Ouverte"
            })

# Ensure the _data directory exists
os.makedirs("_data", exist_ok=True)

# Save this list to the file Manubot reads
with open("_data/sources.yaml", "w") as f:
    yaml.dump(sources, f, default_flow_style=False)

print(f"Successfully saved {len(sources)} citations to _data/sources.yaml!")