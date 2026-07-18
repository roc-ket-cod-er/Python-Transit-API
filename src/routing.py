import gtfs
import time as taaaaa
import transit
import walking
import asyncio
from print_color import *
from time import monotonic_ns
from help_time import hms, sseconds, seconds

async def route(start: tuple[float, float], end: tuple[float, float], filter: int=10):
    startrun_time = monotonic_ns() // 1_000_000
    now_base = taaaaa.localtime()  # one clock read, reused for every trip in this route() call
    sstops_checked = {}
    estops_checked = {}

    t0 = taaaaa.monotonic()
    trips = transit.a_to_b(start, end, now_base=now_base)
    if len(trips) == 0:
        trips = transit.a_to_b(start, end, True, now_base=now_base)
        if len(trips) == 0:
            walk = await walking.walk_route(start, end)
            return ([walk[0].split("\n")[:-1], walk[1], hms(walk[2])], 0)
    mt1 = taaaaa.monotonic()
    
    best_time = float("inf")

    sstops, estops = transit.get_last_startend_stops()
    walk_routes = []
    swalk_routes = []
    ewalk_routes = []

    '''for trip in trips:
        sstop = trip[0][1]
        estop = trip[1][1]

        if estop["id"] not in estops:
            estops.append(estop["id"])
            ewalk_routes.append((estop["coord"], end))
        if sstop["id"] not in sstops:
            sstops.append(sstop["id"])
            swalk_routes.append((start, sstop["coord"]))'''

    for stop in sstops:
        swalk_routes.append((start, stop[1]["coord"]))
    for stop in estops:
        ewalk_routes.append((stop[1]["coord"], end))

    walk_routes = swalk_routes + ewalk_routes + [(start, end)]
    walked_routes = await walking.walk_routes(*walk_routes)
    start_amount = len(swalk_routes)
    end_amount = len(ewalk_routes)

    for i, stop in enumerate(sstops):
        sstops_checked[stop[1]["id"]] = walked_routes[i]

    for i, stop in enumerate(estops):
        estops_checked[stop[1]["id"]] = walked_routes[start_amount + i]

    direct_walk = walked_routes[start_amount + end_amount]  # the (start, end) entry we appended above
    t2 = taaaaa.monotonic()
    
    for trip in trips:
        starting_stop, ending_stop, trip_id, agency, time_for_transit, t1, st, et = trip

        sid = starting_stop[1]["id"]
        eid = ending_stop[1]["id"]

        starting_stop_name = starting_stop[1]["name"]
        ending_stop_name = ending_stop[1]["name"]

        walk = sstops_checked[sid]
        distance_walked = walk[1]
        time = walk[2]

        h1, m1, s1 = hms(walk[2])
        depart_at = transit.depart_at(agency, t1, sid, offset=(h1, m1, s1), now_base=now_base)

        if not depart_at:
            continue

        h, m, s = depart_at
        route_steps = [bold(magenta(f"Depart at {h:02d}:{m:02d}"))]

        if m1 and not h1:   route_steps.append(green(f"Walk for about {int(m1)} min"))
        elif h1:            route_steps.append(green(f"Walk for about {int(h1)} hr and {int(m1)} min"))

        if len(route_steps) == 2:
            route_steps.extend(walk[0].split("\n")[:-2])

        ttime_str = f'{time_for_transit[0]}:{time_for_transit[1]}m)' if time_for_transit[0] else f'{time_for_transit[1]}m'

        route_steps.append(bold(blue(
            f'From "{starting_stop_name}" to "{ending_stop_name}", ' +
            f'use route {trip_id[0]}, towards "{trip_id[1]}" ')) +
            f'(run by {agency}) (Should take about ' +
            ttime_str +
            f', {":".join(st)} to {":".join(et)})'
            #+f' (trip id, sid, eid: {t1}, {sid}, {eid})'# ({h1}, {m1}, {s1})'
        )
        time += seconds(time_for_transit)
        diftime = sseconds(et)

        walk = estops_checked[eid]
        distance_walked += walk[1]
        time += walk[2]
        diftime += walk[2]

        h2, m2, s2 = hms(walk[2])

        if m2 and not h2:   route_steps.append(green(f"Walk for about {int(m2)} min"))
        elif h2:            route_steps.append(green(f"Walk for about {int(h2)} hr and {int(m2):02d} min"))
        route_steps.extend(walk[0].split("\n")[:-1])

        arrive_time_h, arrive_time_m, arrive_time_s = hms(diftime)
        ftime = hms(time)

        #comment to get fastest, uncomment for fastest from now.
        time = diftime

        if time < best_time:
            route_steps.append(bold(magenta(f"Arrive at {arrive_time_h}:{arrive_time_m:02d}")))
            best_trip = [route_steps, distance_walked, ftime]
            best_time = time

    walk = direct_walk
    time = walk[2]
    h, m, s = (0, 0, 0)
    #comment to get fastest time, uncomment for fastest from now.
    h, m, s = transit.time_rn(base=now_base)[2]
    if walk[2] + h * 3600 + m * 60 + s < best_time*0.9:
        return ([walk[0].split("\n")[:-1], walk[1], hms(time)], 0)

    t3 = taaaaa.monotonic()
    print(f"[timing] trip_search={mt1-t0:.3f}s  walking_api={t2-mt1:.3f}s  scoring={t3-t2:.3f}s  total={t3-t0:.3f}s")
 
    return(best_trip, (monotonic_ns()//1_000_000 - startrun_time)/1000)

async def main():
    await gtfs.load_save()

    st = taaaaa.monotonic()
    rt = await route((43.452821, -80.498260), (43.479346, -80.529788))

    #print("\n".join(rt[0][0]))
    #print(rt[0][1:])
    #print(rt[1])
    print(taaaaa.monotonic()-st)
if __name__ == '__main__':
    print("\n\n\n")
    for i in range(200):
        asyncio.run(main())
    print("\n\n\n")
