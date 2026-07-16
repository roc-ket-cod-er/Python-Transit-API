import json
import gtfs
import time
import asyncio

tm_year = 0
tm_mon = 1
tm_mday = 2
tm_hour = 3
tm_min = 4
tm_sec = 5

def time_rn(offset: tuple=(0,0,0)):
    t = time.localtime()

    ctime = [
        f"{ t[tm_hour]+offset[0] }:{ t[tm_min]+offset[1] }:{ t[tm_sec]+offset[2] }",
        f"{ t[tm_year] }{ t[tm_mon] :02d}{ t[tm_mday] }",
        (t[tm_hour]+offset[0], t[tm_min]+offset[1], t[tm_sec]+offset[2])
    ]

    return ctime

def is_trip_valid(agency: str, trip: str, start_stop: str, runday: str="today", runtime="now", offset: tuple=(0,0,0)) -> bool:
    if runday == "today":
        runday = time_rn()[1]
    timing = gtfs.stoptrip_time[agency][trip]
    trip_dates = timing["run_dates"]

    if runday in trip_dates:
        trip_stoptime = tuple(map(int, timing[start_stop][1].split(":")))
        if trip_stoptime > time_rn(offset)[2]:
            return True
    return False

def a_to_b(start: tuple[float, float], end: tuple[float, float], err=False):

    if err:
        start_stops = gtfs.stops(start, 50, 8000)
        end_stops = gtfs.stops(end, 50, 8000)
    else:
        start_stops = gtfs.stops(start)
        end_stops = gtfs.stops(end)

    possible_trips = []

    for stop in start_stops:
        try:
            sid = stop[1]["id"]
            stop_agency = stop[1]["agency"]
            trips = gtfs.stop_trips[stop_agency][sid]
        except KeyError:
            #print("e", stop)
            pass
        for trip in trips:
            if not is_trip_valid(stop_agency, trip, sid):
                continue
            stime = gtfs.stoptrip_time[stop_agency][trip][sid][1].split(":")
            for end_stop in end_stops:
                eid = end_stop[1]["id"]
                try:
                    if eid in gtfs.trip_stops[stop_agency][trip]:
                        if gtfs.trip_stops[stop_agency][trip][sid] < gtfs.trip_stops[stop_agency][trip][eid]:
                            etime = gtfs.stoptrip_time[stop_agency][trip][eid][0].split(":")
                            time_for_transit = [int(x) - int(y) for x, y in zip(etime, stime)]
                            if time_for_transit[2] < 0:
                                time_for_transit[1] -= 1
                                time_for_transit[2] += 60
                            if time_for_transit[1] < 0:
                                time_for_transit[0] -= 1
                                time_for_transit[1] += 60
                            possible_trips.append((stop, end_stop, gtfs.trips_route[trip], stop_agency, time_for_transit, trip, stime, etime))
                except (KeyError, ValueError) as e:
                    #print("e2", end_stop, repr(e))
                    pass
    return possible_trips

async def main():
    print("\n\n\n")
    await gtfs.load_save()
    for trip in a_to_b((43.452821, -80.498260), (43.479346, -80.529788)):
        print(json.dumps(trip, indent=2), "\n\n\n")
    print("\n\n\n", flush=True)

if __name__ == '__main__':
    asyncio.run(main())