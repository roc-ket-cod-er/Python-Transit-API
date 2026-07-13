import transit
import walking
import gtfs


def route(start: tuple[float, float], end: tuple[float, float]):
    try:
        trip = transit.a_to_b(start, end).pop()
    except IndexError:
        try:
            trip = transit.a_to_b(start, end, True).pop()
        except IndexError:
            walk = walking.walk_route(start, end)
            return [walk[0].split("\n")[:-1], walk[1]]
    starting_stop, ending_stop, trip_id, agency = trip

    for stop in gtfs.all_stops:
        if stop["id"] == starting_stop:
            ttrip_start = stop["coord"]
        if stop["id"] == ending_stop:
            ttrip_end = stop["coord"]

    for stop in gtfs.all_stops:
        if stop["id"] == starting_stop:
            starting_stop_name = stop["name"]
        elif stop["id"] == ending_stop:
            ending_stop_name = stop["name"]

    route = []
    distance_walked = 0

    walk = walking.walk_route(start, ttrip_start)
    route.extend(walk[0].split("\n")[:-2])
    distance_walked += walk[1]

    route.append(f'From "{starting_stop_name}" to "{ending_stop_name}", use route {trip_id[0]}, towards "{trip_id[1]}" (run by {agency})')

    walk = walking.walk_route(ttrip_end, end)
    route.extend(walk[0].split("\n")[:-1])
    distance_walked += walk[1]

    #print(route)
    return([route, distance_walked])

if __name__ == '__main__':
    print("\n\n\n\n")
    route((43.453181, -80.499048), (43.651181, -79.378753))
    print("\n\n\n\n")