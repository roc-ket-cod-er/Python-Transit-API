import transit
import walking
import gtfs

def route(start: tuple[float, float], end: tuple[float, float]):
    sstops_checked = {}
    estops_checked = {}
    best_time = 99999999
    trips = transit.a_to_b(start, end)
    if len(trips) == 0:
        trips = transit.a_to_b(start, end, True)
        if len(trips) == 0:
            walk = walking.walk_route(start, end)
            return [walk[0].split("\n")[:-1], walk[1]]
    
    for trip in trips:
        starting_stop, ending_stop, trip_id, agency = trip

        sid = starting_stop[1]["id"]
        eid = ending_stop[1]["id"]

        ttrip_start = starting_stop[1]["coord"]
        ttrip_end = ending_stop[1]["coord"]

        starting_stop_name = starting_stop[1]["name"]
        ending_stop_name = ending_stop[1]["name"]

        route = []
        distance_walked = 0
        time = 0

        if not sid in sstops_checked:
            walk = walking.walk_route(start, ttrip_start)
            sstops_checked[sid] = walk
        else:
            walk = sstops_checked[sid]
        route.extend(walk[0].split("\n")[:-2])
        distance_walked += walk[1]
        time += walk[2]

        route.append(f'From "{starting_stop_name}" to "{ending_stop_name}", use route {trip_id[0]}, towards "{trip_id[1]}" (run by {agency})')

        if not eid in estops_checked:
            walk = walking.walk_route(ttrip_end, end)
            estops_checked[eid] = walk
        else:
            walk = estops_checked[eid]
        route.extend(walk[0].split("\n")[:-1])
        distance_walked += walk[1]
        time += walk[2]

        seconds = time % 60
        minutes = (time // 60) % 60
        hours = (minutes // 60) % 60

        if time < best_time:
            best_trip = [route, distance_walked, (hours, minutes, seconds)]
            best_time = time

    #print(route)
    return(best_trip)

if __name__ == '__main__':
    print("\n\n\n\n")
    gtfs.load_trips()
    print(route((43.505502, -80.522344), (43.479346, -80.529788)))
    print("\n\n\n\n")