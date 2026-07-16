import gtfs
import transit
import walking
import asyncio
from time import monotonic_ns

async def route(start: tuple[float, float], end: tuple[float, float], filter: int=10):
    startrun_time = monotonic_ns() // 1_000_000
    sstops_checked = {}
    estops_checked = {}
    trips = transit.a_to_b(start, end)
    if len(trips) == 0:
        trips = transit.a_to_b(start, end, True)
        if len(trips) == 0:
            walk = await walking.walk_route(start, end)
            time = walk[2]
            seconds = time % 60
            minutes = (time // 60) % 60
            hours = (minutes // 60) % 60
            return ([walk[0].split("\n")[:-1], walk[1], (hours, minutes, seconds)], 0)
    
    best_time = 99999999

    sstops = []
    estops = []
    walk_routes = []
    swalk_routes = []
    ewalk_routes = []

    for trip in trips:
        sstop = trip[0][1]
        estop = trip[1][1]

        if not estop["id"] in estops:
            estops.append(estop["id"])
            ewalk_routes.append((estop["coord"], end))
        if not sstop["id"] in sstops:
            sstops.append(sstop["id"])
            swalk_routes.append((start, sstop["coord"]))

    walk_routes = swalk_routes + ewalk_routes
    walked_routes = await walking.walk_routes(*walk_routes)

    start_amount = len(swalk_routes)

    for i, stop in enumerate(sstops):
        sstops_checked[stop] = walked_routes[i]

    for i, stop in enumerate(estops):
        estops_checked[stop] = walked_routes[start_amount + i]
    
    for trip in trips:
        starting_stop, ending_stop, trip_id, agency, time_for_transit, t1, st, et = trip

        sid = starting_stop[1]["id"]
        eid = ending_stop[1]["id"]

        starting_stop_name = starting_stop[1]["name"]
        ending_stop_name = ending_stop[1]["name"]

        route = []
        distance_walked = 0

        walk = sstops_checked[sid]
        route.extend(walk[0].split("\n")[:-2])
        distance_walked += walk[1]
        time = walk[2]

        s1 = time % 60
        m1 = (time // 60) % 60
        h1 = (m1 // 60) % 60

        if not transit.is_trip_valid(agency, t1, sid, offset=(h1, m1, s1)):
            continue

        ttime_str = f'{time_for_transit[0]}:{time_for_transit[1]}m)' if time_for_transit[0] else f'{time_for_transit[1]}m'

        route.append(
            f'From "{starting_stop_name}" to "{ending_stop_name}", ' +
            f'use route {trip_id[0]}, towards "{trip_id[1]}" ' +
            f'(run by {agency}) (Should take about ' +
            ttime_str +
            f' ({":".join(st)} to {":".join(et)})'
            +f' (trip id, sid, eid: {t1}, {sid}, {eid}))'# ({h1}, {m1}, {s1})'
        )
        time += time_for_transit[0] * 3600 + time_for_transit[1] * 60 + time_for_transit[2]
        et = tuple(map(int, et))
        diftime = et[0] * 3600 + et[1] * 60 + et[2]

        walk = estops_checked[eid]
        route.extend(walk[0].split("\n")[:-1])
        distance_walked += walk[1]
        time += walk[2]
        diftime += walk[2]

        seconds = time % 60
        minutes = (time // 60) % 60
        hours = (minutes // 60) % 60

        #comment to get fastest, uncomment for fastest from now.
        time += diftime

        if time < best_time:
            best_trip = [route, distance_walked, (hours, minutes, seconds)]
            best_time = time

    walk = await walking.walk_route(start, end)
    time = walk[2]
    h, m, s = (0, 0, 0)
    #comment to get fastest time, uncomment for fastest from now.
    h, m, s = transit.time_rn()[2]
    if walk[2] + h * 3600 + m * 60 + s < best_time*0.9:
        seconds = time % 60
        minutes = (time // 60) % 60
        hours = (minutes // 60) % 60
        return ([walk[0].split("\n")[:-1], walk[1], (hours, minutes, seconds)], 0)
    
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
