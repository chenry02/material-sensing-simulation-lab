import requests
import yaml
import os

# --- CHANGE THIS TO YOUR ACTUAL HAL ID ---
HAL_ID = "clement-henry"
# -----------------------------------------

# Papers to permanently exclude (co-authored outside the lab's scope)
BLOCKLIST_DOIS = {
    "10.1109/TAP.2023.3283043",
    "10.1109/TAP.2022.3161390",
    "10.1109/IEEECONF35879.2020.9330486",
    "10.3390/ijerph17072586",
    "10.1109/CLEOE-EQEC.2019.8873045",
    "10.1364/OE.27.021069",
    "10.1109/AP-S/INC-USNC-URSI52054.2024.10686275",
    "10.1109/AP-S/INC-USNC-URSI52054.2024.10687162",
    "10.1109/AP-S/INC-USNC-URSI52054.2024.10686480",
    "10.1109/CAMA57522.2023.10352703",
    "10.1109/CAMA57522.2023.10352886",
    "10.23919/EuCAP57121.2023.10133635",
    "10.1109/ICEAA49419.2022.9899870",
    "10.1109/AP-S/USNC-URSI47032.2022.9886398",
    "10.1109/AP-S/USNC-URSI47032.2022.9886850",
}

BLOCKLIST_HAL_IDS = {
    "hal-04169310",
    "hal-04342598",
    "tel-04642819",
}

print(f"Fetching publications from HAL for {HAL_ID}...")

# Query the HAL API for your papers (asking specifically for the DOI and title)
url = f"https://api.archives-ouvertes.fr/search/?q=authIdHal_s:{HAL_ID}&fl=title_s,doiId_s,uri_s,producedDate_s&wt=json&rows=100&sort=producedDate_s desc"
response = requests.get(url)
data = response.json()

# Load existing sources.yaml to preserve custom fields (image, tags, etc.)
existing_meta = {}
try:
    with open("_data/sources.yaml") as f:
        for entry in yaml.safe_load(f) or []:
            if "id" in entry:
                existing_meta[entry["id"]] = {
                    k: v for k, v in entry.items()
                    if k not in ("id", "title", "date", "publisher")
                }
except FileNotFoundError:
    pass

sources = []

# Check if we have papers
if 'response' in data and 'docs' in data['response']:
    for doc in data['response']['docs']:
        # We only want to give Manubot the papers that have a DOI attached to them in HAL
        if 'doiId_s' in doc:
            doi = doc['doiId_s']
            if doi in BLOCKLIST_DOIS:
                continue
            entry = {"id": f"doi:{doi}"}
            entry.update(existing_meta.get(f"doi:{doi}", {}))
            sources.append(entry)
        else:
            uri = doc['uri_s']
            # Extract HAL ID (e.g. hal-04169310) from URI for blocklist check
            hal_id = uri.rstrip("/").split("/")[-1].split("v")[0]
            if hal_id in BLOCKLIST_HAL_IDS:
                continue
            # If no DOI is available, we fall back to manual formatting using the HAL URL
            # By supplying the title and date manually, Manubot won't crash trying to guess them
            title = doc.get('title_s', ['Untitled'])[0]
            date = doc.get('producedDate_s', '2020-01-01')
            entry = {
                "id": f"url:{uri}",
                "title": title,
                "date": date,
                "publisher": "HAL Archive Ouverte"
            }
            entry.update(existing_meta.get(f"url:{uri}", {}))
            sources.append(entry)

# Ensure the _data directory exists
os.makedirs("_data", exist_ok=True)

# Save this list to the file Manubot reads
with open("_data/sources.yaml", "w") as f:
    yaml.dump(sources, f, default_flow_style=False)

print(f"Successfully saved {len(sources)} citations to _data/sources.yaml!")