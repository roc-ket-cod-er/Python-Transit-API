import sys
from pathlib import Path

# Calculate the parent directory path
parent_dir = str(Path(__file__).resolve().parent.parent)

# Insert the parent directory into sys.path
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from gtfs import stop_trips, trip_stops, stops, load_trips


def a_to_b(start: tuple[float, float], end: tuple[float, float]):
    load_trips()

    start_stops = stops(start)
    end_stops = stops(end)

    possible_trips = []

    for stop in start_stops:
        #print(stop)
        try:
            stop_id = stop[1]["id"]
            stop_agency = stop[1]["agency"]
            trips = stop_trips[stop_agency][stop_id]
        except KeyError:
            print("e", stop)
        for trip in trips:
            #print(trip)
            for end_stop in end_stops:
                try:
                    #print("e", end_stop)
                    if end_stop[1]["id"] in trip_stops[stop_agency][trip]:
                        if trip_stops[stop_agency][trip].index(stop_id) < trip_stops[stop_agency][trip].index(end_stop[1]["id"]):
                            possible_trips.append([stop_id, end_stop[1]["id"], trip])
                except KeyError:
                    print("e2", end_stop)
    return possible_trips

if __name__ == '__main__':
    print("\n\n\n")
    for trip in a_to_b((43.454894, -80.493729), (43.645261, -79.380684)):
        print(trip)
    print("\n\n\n", flush=True)