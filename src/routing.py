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

    sid = starting_stop[1]["id"]
    eid = ending_stop[1]["id"]

    ttrip_start = starting_stop[1]["coord"]
    ttrip_end = ending_stop[1]["coord"]

    starting_stop_name = starting_stop[1]["name"]
    ending_stop_name = ending_stop[1]["name"]

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
    gtfs.load_trips()
    print(route((43.505502, -80.522344), (43.479346, -80.529788)))
    print("\n\n\n\n")