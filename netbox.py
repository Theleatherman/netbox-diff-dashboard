import requests
import urllib3
from config import NETBOX_API_URL, NETBOX_API_TOKEN

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {"Authorization": f"Token {NETBOX_API_TOKEN}"} if NETBOX_API_TOKEN else {}

def get_mgmt_ips(tag_slug_filter="mgmt-if"):
    result = []
    base_url = NETBOX_API_URL + "?limit=1000&fields=address,dns_name,description,tags"
    params = {
        "limit": 1000,
        "fields": "address,dns_name,description,tags"
    }
    url = base_url
    while url:
        print(f"Abfrage: {url}")
        r = requests.get(url, headers=HEADERS, params=params if url == base_url else {}, verify=False)
        r.raise_for_status()
        data = r.json()
        for entry in data.get("results", []):
            tags = [t["slug"] for t in entry.get("tags", []) if isinstance(t, dict)]
            if tag_slug_filter not in tags:
                continue  # Tag nicht enthalten → überspringen

            ip = entry.get("address", "").strip()
            dns = entry.get("dns_name", "").strip()
            desc = entry.get("description", "").strip()
            result.append((ip, desc, dns, tags))
        url = data.get("next")
    return result
