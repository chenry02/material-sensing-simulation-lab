import requests
import yaml

# Replace with your actual idHal
ID_HAL = "clement-henry" 

# Query the HAL API
url = f"https://api.archives-ouvertes.fr/search/?q=authIdHal_s:{ID_HAL}&fl=doiId_s,uri_s&wt=json&rows=100"
response = requests.get(url).json()

sources = []
for doc in response['response']['docs']:
    if 'doiId_s' in doc:
        # If the HAL entry has a DOI, use it!
        sources.append({"id": f"doi:{doc['doiId_s']}"})
    else:
        # Otherwise, fall back to the HAL URL
        sources.append({"id": f"url:{doc['uri_s']}"})

# Save to the template's data folder
with open("_data/sources-hal.yaml", "w") as f:
    yaml.dump(sources, f, default_flow_style=False)
    
print("Successfully pulled HAL citations!")