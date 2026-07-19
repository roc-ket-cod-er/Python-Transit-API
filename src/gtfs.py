import ssl
import csv
import json
import time
import math
import pickle
import urllib3
import zipfile
import asyncio
import requests
from pathlib import Path
from os import remove, path
from datetime import datetime, timedelta
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context
from help_time import sseconds

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = {
    "GRT": {
        "BUS": "https://webapps.regionofwaterloo.ca/api/grt-routes/api/staticfeeds/1",
        "LRT": "https://webapps.regionofwaterloo.ca/api/grt-routes/api/staticfeeds/2",
    },
    "GO": {
        "ALL": "https://assets.metrolinx.com/raw/upload/Documents/Metrolinx/Open%20Data/GO-GTFS.zip",
    },
    "TTC": {
        "ALL": r"https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/b811ead4-6eaf-4adb-8408-d389fb5a069c/resource/c920e221-7a1c-488b-8c5b-6d8cd4e85eaf/download/Complete%20GTFS.zip"
    }
}

ALL = 'TTC&&GRT&&GO'

gtfs_cache_path = Path("GTFS/gtfs_cache.pkl")

all_stops = []
stop_trips = {}
sorted_stop_trips = {}  # agency -> stop_id -> [(departure_seconds, trip_id), ...] sorted ascending
trip_stops = {}
trips_route = {}
stoptrip_time = {}
trip_service = {}
service_date = {}

stop_coords = {}

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

async def update(agencies: str = ALL, rec: bool = True) -> None:
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
    if rec:
        await load_trips(agencies)

async def load_stops(agencies=ALL):
    global all_stops, stimes
    for agency in agencies.split("&&"):
        try:
            for key in list(URL[agency].keys()):
                with open(f"GTFS/{agency}/{key}/stops.txt", encoding="utf-8-sig") as f:
                    reader = csv.DictReader(f)

                    for stop in reader:
                        if stop["location_type"] != '3':
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
            await update(agency, rec=False)
            stimes.append([f"downloaded {agency} files", time.monotonic()])
            await load_stops(agency)

async def load_trips(agencies=ALL):
    global stimes
    stimes = [["start", time.monotonic()]]

    global stop_trips, sorted_stop_trips, trip_stops, trips_route, stoptrip_time, all_stops, trip_service, service_date

    for agency in agencies.split("&&"):
        await load_stops(agency)
        stimes.append(["load_stops", time.monotonic()])

        stop_trips[agency] = {}
        trip_stops[agency] = {}
        stoptrip_time[agency] = {}
        trips_route[agency] = {}
        trip_service[agency] = {}
        service_date[agency] = {}

        stop_trips_agency = stop_trips[agency]
        trip_stops_agency = trip_stops[agency]
        stoptrip_time_agency = stoptrip_time[agency]
        service_date_agency = service_date[agency]


        for service in URL[agency]:
            # ---------- stop_times.txt ----------
            with open(f"GTFS/{agency}/{service}/stop_times.txt", encoding="utf-8-sig", newline="") as f:
                reader = csv.reader(f)
                header = next(reader)

                trip_id_i   = header.index("trip_id")
                stop_id_i   = header.index("stop_id")
                arrival_i   = header.index("arrival_time")
                departure_i = header.index("departure_time")
                stop_seq_i  = header.index("stop_sequence")

                for row in reader:
                    trip_id = row[trip_id_i]
                    stop_id = row[stop_id_i]

                    trip_dict = trip_stops_agency.setdefault(trip_id, {})
                    time_dict = stoptrip_time_agency.setdefault(trip_id, {})

                    stop_trips_agency.setdefault(stop_id, []).append(trip_id)

                    trip_dict[stop_id] = int(row[stop_seq_i]) - 1
                    time_dict[stop_id] = (
                        row[arrival_i],
                        row[departure_i]
                    )

            stimes.append([f"{agency}/{service} stop_times", time.monotonic()])

            # ---------- trips.txt -----------
            with open(f"GTFS/{agency}/{service}/trips.txt", encoding="utf-8-sig", newline="") as f:
                reader = csv.reader(f)
                header = next(reader)

                trip_id_i = header.index("trip_id")
                route_id_i = header.index("route_id")
                headsign_i = header.index("trip_headsign")
                service_id_i = header.index("service_id")

                for row in reader:
                    if row:
                        trips_route[row[trip_id_i]] = (row[route_id_i], row[headsign_i])
                        trip_service[row[trip_id_i]] = row[service_id_i]

            stimes.append([f"{agency}/{service} trips", time.monotonic()])
            
            # ----------- calendar.txt -------------
            ctxt = Path(f"GTFS/{agency}/{service}/calendar.txt")
            if ctxt.exists():
                with ctxt.open(encoding="utf-8-sig") as f:
                    reader = csv.reader(f)
                    header = next(reader)
                    
                    for row in reader:
                        if not row:
                            continue

                        service_id = row[0]

                        weekdays = [
                            int(row[1]),  # monday
                            int(row[2]),
                            int(row[3]),
                            int(row[4]),
                            int(row[5]),
                            int(row[6]),
                            int(row[7])   # sunday
                        ]

                        start = datetime.strptime(row[8], "%Y%m%d")
                        end = datetime.strptime(row[9], "%Y%m%d")

                        dates = []

                        current = start

                        while current <= end:
                            if weekdays[current.weekday()]:
                                dates.append(current.strftime("%Y%m%d"))

                            current += timedelta(days=1)

                        service_date_agency[service_id] = dates
            
            # ----------- calendar_dates.txt --------
            with open(f"GTFS/{agency}/{service}/calendar_dates.txt") as f:
                reader = csv.reader(f)
                header = next(reader)

                date_i       = 1
                exception_i  = 2
                service_id_i = 0

                for row in reader:
                    if row:
                        if row[exception_i] == '1':
                            service_date_agency.setdefault(row[service_id_i], []).append(row[date_i])
                        '''elif row[exception_i] == '2':
                            service_date_agency[row[service_id_i]].remove(row[date_i])'''
            stimes.append([f"{agency}/{service} calendar", time.monotonic()])


            for trip in stoptrip_time_agency:
                try:
                    stoptrip_time_agency[trip]["run_dates"] = service_date_agency[trip_service[trip]]
                except Exception as e:
                    print(trip)
                    print(e)
                    print(trip_service[trip])
            
            stimes.append(["finished conversion", time.monotonic()])

        sorted_stop_trips[agency] = {
            sid: sorted(
                (sseconds(stoptrip_time_agency[trip][sid][1].split(":")), trip)
                for trip in trip_list
            )
            for sid, trip_list in stop_trips_agency.items()
        }
        stimes.append([f"{agency} sorted_stop_trips", time.monotonic()])

    print("loaded,", [(t[1] - stimes[0][1], t[0]) for t in stimes])
    with gtfs_cache_path.open("wb") as f:
        pickle.dump(
            (stop_trips, sorted_stop_trips, trip_stops, trips_route, stoptrip_time, all_stops, trip_service, service_date),
            f
        )

async def load_save(s=None):
    global stop_trips, sorted_stop_trips, trip_stops, trips_route, stoptrip_time, all_stops, trip_service, service_date

    if s == None:
        screen = False
    else:
        screen = True

    loaded_from_cache = False
    if gtfs_cache_path.exists():
        with gtfs_cache_path.open("rb") as f:
            stop_trips, sorted_stop_trips, trip_stops, trips_route, stoptrip_time, all_stops, trip_service, service_date = pickle.load(f)
    else:
        if screen:
            s.clear()
            await s.type("Please Wait: Downloading Transit Data Files...", delay=0.01)
        await load_trips()
        if screen:
            await s.type("Files loaded!")
            await asyncio.sleep(0.4)
            s.clear()



_EARTH_RADIUS_M = 6_371_000

def _haversine_m(lat1, lon1, lat2, lon2):
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * _EARTH_RADIUS_M * math.asin(math.sqrt(a))

def stops(coord, amount=50, max_dist=2000):
    global stop_coords
    lat0, lon0 = coord
    lat_margin = max_dist / 111_320
    lon_margin = max_dist / (111_320 * max(math.cos(math.radians(lat0)), 0.01))
    lat_min, lat_max = lat0 - lat_margin, lat0 + lat_margin
    lon_min, lon_max = lon0 - lon_margin, lon0 + lon_margin

    results = []
    for stop in all_stops:
        slat, slon = stop["coord"]
        if slat < lat_min or slat > lat_max or slon < lon_min or slon > lon_max:
            continue
        distance = _haversine_m(lat0, lon0, slat, slon)
        if distance > max_dist:
            continue
        results.append((round(distance, 1), stop))
        if stop["agency"] not in stop_coords:
            stop_coords[stop["agency"]] = {}
        stop_coords[stop["agency"]][stop["id"]] = stop["coord"]

    results.sort(key=lambda x: x[0])
    #print(len(results), results[:amount])
    return results[:amount]

async def main():
    print("\n\n\n")
    await load_trips()
    print(stoptrip_time["GRT"])
    print("\n\n\n")

if __name__ == '__main__':
    asyncio.run(main())
