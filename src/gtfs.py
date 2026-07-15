import ssl
import csv
import json
import time
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
        "BUS": "https://webapps.regionofwaterloo.ca/api/grt-routes/api/staticfeeds/1",
        "LRT": "https://webapps.regionofwaterloo.ca/api/grt-routes/api/staticfeeds/2",
    },
    "GO": {
        "ALL": "https://assets.metrolinx.com/raw/upload/Documents/Metrolinx/Open%20Data/GO-GTFS.zip",
    }
}

ALL = 'GRT&&GO'

all_stops = []
stop_trips = {}
trip_stops = {}
trips_route = {}
stoptrip_time = {}

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


def update(agencies: str = ALL) -> None:
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
            local_path = f"GTFS\\{agency}\\{key}"
            Path(local_path).mkdir(parents=True, exist_ok=True)
            #print(f"Fetching {url}")

            response = session.get(url, verify=False)
            if response.status_code == 200:
                #print(f"wrtiting to {local_path + "\\data.zip"}")
                with open(local_path + r"\data.zip", "wb") as file:
                    file.write(response.content)
                #print("Download complete!")
            else:
                #print(f"Failed to download. Status code: {response.status_code}")
                continue

            with zipfile.ZipFile(local_path + "\\data.zip", 'r') as zip_ref:
                zip_ref.extractall(local_path)

            remove(local_path + "\\data.zip")

def load_stops(agencies=ALL):
    global all_stops
    for agency in agencies.split("&&"):
        try:
            for key in list(URL[agency].keys()):
                with open(f"GTFS/{agency}/{key}/stops.txt", encoding="utf-8-sig") as f:
                    reader = csv.DictReader(f)

                    for stop in reader:
                        try:
                            all_stops.append({
                                "agency": agency,
                                "type": key,
                                "id": stop["stop_id"],
                                "name": stop["stop_name"],
                                "coord": (
                                    float(stop["stop_lat"]),
                                    float(stop["stop_lon"])
                                )
                            })
                        except KeyError:
                            print(json.dumps(stop, indent=2), agency, key)
                            time.sleep(1)
        except FileNotFoundError:
            update(agency)
            load_stops(agencies)

def load_trips(agencies=ALL):
    #print("loading")
    global stop_trips, trip_stops, trips_route, stoptrip_time
    
    for agency in agencies.split("&&"):
        load_stops(agency)
        stop_trips[agency]    = {}
        trip_stops[agency]    = {}
        stoptrip_time[agency] = {}
        
        for service in list(URL[agency].keys()):
            with open(f"GTFS/{agency}/{service}/stop_times.txt", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for trip in reader:
                    stop_trips[agency].setdefault(trip["stop_id"], []).append(trip["trip_id"])
                    
                    if trip["trip_id"] not in trip_stops[agency]:
                        trip_stops[agency][trip["trip_id"]] = {}
                    
                    if trip["trip_id"] not in stoptrip_time[agency]:
                        stoptrip_time[agency][trip["trip_id"]] = {}
                    
                    trip_stops[agency][trip["trip_id"]][trip["stop_id"]] = int(trip["stop_sequence"]) - 1
                    stoptrip_time[agency][trip["trip_id"]].setdefault(trip["stop_id"], []).extend(
                        [trip["arrival_time"], trip["departure_time"]]
                    )

            with open(f"GTFS/{agency}/{service}/trips.txt", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for trip in reader:
                    trips_route.setdefault(trip["trip_id"], []).extend(
                        (trip["route_id"], trip["trip_headsign"])
                    )
    #print("loaded")
        


def stops(coord, amount=70, max_dist=2000):
    results = []
    for stop in all_stops:
        distance = geodesic(coord, stop["coord"]).meters
        if distance > max_dist:
            continue
        results.append(
            (round(distance, 1), stop)
        )
    results.sort(key=lambda x: x[0])
    #print(len(results), results[:amount])
    return results[:amount]


if __name__ == '__main__':
    print("\n\n\n")
    print(find_gtfs_dir())
    load_trips(ALL)
    print(find_gtfs_dir())
    print(json.dumps(stoptrip_time["GRT"], indent=2))
    print("\n\n\n")