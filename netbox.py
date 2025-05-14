import requests
import urllib3
from config import NETBOX_API_URL, NETBOX_API_TOKEN

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {"Authorization": f"Token {NETBOX_API_TOKEN}"}

def get_mgmt_ips(tag_slugs=["mgmt-if"]):
    results = []
    url = NETBOX_API_URL + "?limit=1000&fields=address,dns_name,description,tags"
    while url:
        print(f"Abfrage: {url}")
        r = requests.get(url, headers=HEADERS, verify=False)
        r.raise_for_status()
        data = r.json()

        for ip in data["results"]:
            ip_tags = [t["slug"] for t in ip.get("tags", [])]
            if any(slug in ip_tags for slug in tag_slugs):
                if ip["description"] or ip["dns_name"]:
                    results.append({
                        "address": ip["address"],
                        "description": ip["description"],
                        "dns_name": ip["dns_name"],
                        "tags": ip_tags,
                    })

        url = data.get("next")
    return results
