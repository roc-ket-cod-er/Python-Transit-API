import gtfs
from time import monotonic_ns
import transit
import walking
import asyncio
from walking import WALK_SPEED_MPS
from geopy.distance import geodesic

async def route(start: tuple[float, float], end: tuple[float, float], filter: int=10):
    startrun_time = monotonic_ns() // 1_000_000
    sstops_checked = {}
    estops_checked = {}
    trips = transit.a_to_b(start, end)
    if len(trips) == 0:
        trips = transit.a_to_b(start, end, True)
        if len(trips) == 0:
            walk = await walking.walk_route(start, end)
            return [[walk[0].split("\n")[:-1], walk[1]], 0]
    
    best_time = 99999999

    sstops = []
    estops = []
    walk_routes = []
    swalk_routes = []
    ewalk_routes = []

    for trip in trips:
        sstop = trip[0][1]
        estop = trip[1][1]

        swalk_routes.append((start, sstop["coord"]))
        ewalk_routes.append((estop["coord"], end))

        sstops.append(sstop["id"])
        estops.append(estop["id"])

    swalk_routes = list(dict.fromkeys(swalk_routes))
    ewalk_routes = list(dict.fromkeys(ewalk_routes))
    sstops = list(dict.fromkeys(sstops))
    estops = list(dict.fromkeys(estops))

    walk_routes = swalk_routes + ewalk_routes
    walked_routes = await walking.walk_routes(*walk_routes)

    amount = len(walked_routes)
    middle = amount // 2

    for i in range(middle):
        estops_checked[estops[i]] = walked_routes[middle + i]
        sstops_checked[sstops[i]] = walked_routes[i]
    
    for trip in trips:
        starting_stop, ending_stop, trip_id, agency, time_for_transit, t1 = trip

        sid = starting_stop[1]["id"]
        eid = ending_stop[1]["id"]

        starting_stop_name = starting_stop[1]["name"]
        ending_stop_name = ending_stop[1]["name"]

        route = []
        distance_walked = 0
        time = 0

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

        ttime_str = f'{time_for_transit[0]}:{time_for_transit[1]}m)' if time_for_transit[0] else f'{time_for_transit[1]}m'

        route.append(
            f'From "{starting_stop_name}" to "{ending_stop_name}", ' + 
            f'use route {trip_id[0]}, towards "{trip_id[1]}" ' +
            f'(run by {agency}) (Should take about ' +
            ttime_str +
            f' (trip id, sid, eid: {t1}, {sid}, {eid})'
        )
        time += time_for_transit[0] * 3600 + time_for_transit[1] * 60 + time_for_transit[2]

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

    
    return(best_trip, (monotonic_ns()//1_000_000 - startrun_time)/1000)

async def main():
    print("\n\n\n")
    await gtfs.load_save()

    rt = await route((43.452821, -80.498260), (43.479346, -80.529788))

    print("\n".join(rt[0][0]))
    print(rt[0][1:])
    print(rt[1])
    print("\n\n\n")

if __name__ == '__main__':
    asyncio.run(main())
