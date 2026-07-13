from gtfs import stop_trips, trip_stops, stops, load_trips, trips_route


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
            stop_id = stop[1]["id"]
            stop_agency = stop[1]["agency"]
            trips = stop_trips[stop_agency][stop_id]
        except KeyError:
            #print("e", stop)
            pass
        for trip in trips:
            #print(trip)
            for end_stop in end_stops:
                try:
                    #print("e", end_stop)
                    if end_stop[1]["id"] in trip_stops[stop_agency][trip]:
                        if trip_stops[stop_agency][trip].index(stop_id) < trip_stops[stop_agency][trip].index(end_stop[1]["id"]):
                            possible_trips.append((stop_id, end_stop[1]["id"], trips_route[trip], stop_agency))
                except KeyError:
                    #print("e2", end_stop)
                    pass
    return possible_trips

if __name__ == '__main__':
    print("\n\n\n")
    for trip in a_to_b((43.454894, -80.493729), (43.645261, -79.380684)):
        print(trip)
    print("\n\n\n", flush=True)