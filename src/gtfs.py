import ssl
import csv
import json
import requests
import urllib3
import zipfile
from pathlib import Path
from os import remove, path
from geopy.distance import geodesic
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = {
    "GRT": {
        "ALL": "https://webapps.regionofwaterloo.ca/api/grt-routes/api/staticfeeds/0",
    },
    "GO": {
        "ALL": "https://assets.metrolinx.com/raw/upload/Documents/Metrolinx/Open%20Data/GO-GTFS.zip"
    }
}

all_stops = []

class WeakDHAdapter(HTTPAdapter):
    """HTTPAdapter that lowers OpenSSL's security level and disables
    certificate verification entirely — most permissive TLS possible."""
    def init_poolmanager(self, *args, **kwargs):
        ctx = create_urllib3_context()
        ctx.set_ciphers("DEFAULT@SECLEVEL=1")
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        kwargs["ssl_context"] = ctx
        return super().init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        ctx = create_urllib3_context()
        ctx.set_ciphers("DEFAULT@SECLEVEL=1")
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        kwargs["ssl_context"] = ctx
        return super().proxy_manager_for(*args, **kwargs)
    
def find_gtfs_dir():
    return path.isdir("GTFS")


def update(agencies: str) -> None:
    if agencies.lower() == 'all':
        agencies = 'GRT&&GO'
    for agency in agencies.split("&&"):
        try:
            keys = list(URL[agency].keys())
        except KeyError as e:
            print(f"ERROR: {e}")
            continue

        session = requests.Session()
        session.mount("https://", WeakDHAdapter())

        for key in keys:
            url = URL[agency][key]
            local_path = f"GTFS\\{agency}\\{key}" if key != "ALL" else f"GTFS\\{agency}"
            Path(local_path).mkdir(parents=True, exist_ok=True)
            print(f"Fetching {url}")

            response = session.get(url, verify=False)
            if response.status_code == 200:
                print(f"wrtiting to {local_path + "\\data.zip"}")
                with open(local_path + r"\data.zip", "wb") as file:
                    file.write(response.content)
                print("Download complete!")
            else:
                print(f"Failed to download. Status code: {response.status_code}")
                continue

            with zipfile.ZipFile(local_path + "\\data.zip", 'r') as zip_ref:
                zip_ref.extractall(local_path)

            remove(local_path + "\\data.zip")

def load_stops():
    global all_stops

    with open("GTFS/GRT/stops.txt", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for stop in reader:
            all_stops.append({
                "id": stop["stop_id"],
                "name": stop["stop_name"],
                "coord": (
                    float(stop["stop_lat"]),
                    float(stop["stop_lon"])
                )
            })

def stops(coord, amount=20):
    results = []

    for stop in all_stops:
        distance = geodesic(coord, stop["coord"]).meters

        results.append(
            (distance, stop)
        )

    results.sort(key=lambda x: x[0])

    return results[:amount]


if __name__ == '__main__':
    print("\n\n\n")
    print(find_gtfs_dir())
    load_stops()
    print(json.dumps(stops((43.505502, -80.522344)), indent=4))
    print(find_gtfs_dir())
    print("\n\n\n")