import json
from gtfs import stop_trips, trip_stops, stops, load_trips, trips_route, stoptrip_time


def a_to_b(start: tuple[float, float], end: tuple[float, float], err=False):
    global trip_route

    if err:
        start_stops = stops(start, 50, 8000)
        end_stops = stops(end, 50, 8000)
    else:
        start_stops = stops(start)
        end_stops = stops(end)

    possible_trips = []

    for stop in start_stops:
        #print(stop)
        try:
            sid = stop[1]["id"]
            stop_agency = stop[1]["agency"]
            trips = stop_trips[stop_agency][sid]
        except KeyError:
            #print("e", stop)
            pass
        for trip in trips:
            #print(trip)
            for end_stop in end_stops:
                eid = end_stop[1]["id"]
                try:
                    #print("e", end_stop)
                    if eid in trip_stops[stop_agency][trip]:
                        start_index = trip_stops[stop_agency][trip].index(sid)
                        stop_index = trip_stops[stop_agency][trip].index(eid)
                        if start_index < stop_index:
                            stime = stoptrip_time[stop_agency][trip][sid][1].split(":")
                            etime = stoptrip_time[stop_agency][trip][eid][0].split(":")
                            time_for_transit = [int(x) - int(y) for x, y in zip(etime, stime)]
                            possible_trips.append((stop, end_stop, trips_route[trip], stop_agency, time_for_transit, trip))
                except KeyError:
                    #print("e2", end_stop)
                    pass
    return possible_trips

if __name__ == '__main__':
    print("\n\n\n")
    load_trips()
    for trip in a_to_b((43.452821, -80.498260), (43.479346, -80.529788)):
        print(json.dumps(trip, indent=2), "\n\n\n")
    print("\n\n\n", flush=True)