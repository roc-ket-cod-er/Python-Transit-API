import gtfs
import transit
import walking
from walking import WALK_SPEED_MPS
from geopy.distance import geodesic

def route(start: tuple[float, float], end: tuple[float, float], filter: int=10):
    sstops_checked = {}
    estops_checked = {}
    filtered_trips = []
    best_times = []
    trips = transit.a_to_b(start, end)
    if len(trips) == 0:
        trips = transit.a_to_b(start, end, True)
        if len(trips) == 0:
            walk = walking.walk_route(start, end)
            return [walk[0].split("\n")[:-1], walk[1]]
    
    for trip in trips:
        starting_stop, ending_stop, trip_id, agency, time_for_transit, t1 = trip

        ttrip_start = starting_stop[1]["coord"]
        ttrip_end = ending_stop[1]["coord"]

        time  = (geodesic(start, ttrip_start).meters * 1.3) // WALK_SPEED_MPS
        time += time_for_transit[0] * 3600 + time_for_transit[1] * 60 + time_for_transit[2]
        time += (geodesic(ttrip_end, end) * 1.3).meters // WALK_SPEED_MPS

        best_times.append(time)
        best_times.sort()
        best_times = best_times[:filter]
        if time in best_times:
            filtered_trips.insert(best_times.index(time), trip)
            filtered_trips = filtered_trips[:filter]
    
    best_time = 99999999

    scoords = []
    ecoords = []

    for trip in filtered_trips:
        scoord = trip[0][1]["coord"]
        ecoord = trip[1][1]["coord"]

        scoords.append(scoord)
        ecoords.append(ecoord)

    walk_trips = list((start, s) for s in dict.fromkeys(scoords))
    walk_trips.append(list((e, end) for e in dict.fromkeys(ecoords)))

    print(list((s, e) for s, e in zip(start, scoords)))
    exit()

    walking.walk_routes((s, e) for s, e in zip(scoords, ecoords))

    for trip in filtered_trips:
        starting_stop, ending_stop, trip_id, agency, time_for_transit, t1 = trip

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

        if time_for_transit[2] < 0:
            time_for_transit[1] -= 1
            time_for_transit[2] += 60
        if time_for_transit[1] < 0:
            time_for_transit[0] -= 1
            time_for_transit[1] += 60

        route.append(f'From "{starting_stop_name}" to "{ending_stop_name}", use route {trip_id[0]}, towards "{trip_id[1]}" (run by {agency}) (Should take about {time_for_transit[0]}:{time_for_transit[1]}m)')
        time += time_for_transit[0] * 3600 + time_for_transit[1] * 60 + time_for_transit[2]

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
            #print(best_time, time_for_transit, trip_id, sid, eid, t1)

    #print(route)
    return(best_trip)

if __name__ == '__main__':
    print("\n\n\n")
    gtfs.load_trips()

    rt = route((43.452821, -80.498260), (43.479346, -80.529788))

    print("\n".join(rt[0]))
    print(rt[1:])
    print("\n\n\n")