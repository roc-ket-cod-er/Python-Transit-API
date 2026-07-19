import json
import gtfs
import time
import bisect
import asyncio
from help_time import *

start_stops = []
end_stops = []

def is_trip_valid(agency: str, trip: str, start_stop: str, runday: str="today", runtime="now", offset: tuple=(0,0,0), now_base=None) -> bool:
    if runday == "today":
        runday = time_rn(base=now_base)[1]
    timing = gtfs.stoptrip_time[agency][trip]
    trip_dates = timing["run_dates"]

    if runday in trip_dates:
        try:
            trip_stoptime = tuple(map(int, timing[start_stop][1].split(":")))
        except KeyError:
            return False
        if trip_stoptime > time_rn(offset, base=now_base)[2]:
            return True
    return False

def depart_at(agency: str, trip: str, start_stop: str, runday: str="today", runtime="now", offset: tuple=(0,0,0), now_base=None) -> bool:
    if runday == "today":
        runday = time_rn(base=now_base)[1]
    timing = gtfs.stoptrip_time[agency][trip]
    trip_dates = timing["run_dates"]

    if runday in trip_dates:
        try:
            trip_stoptime = tuple(map(int, timing[start_stop][1].split(":")))
        except KeyError:
            return False
        if trip_stoptime > time_rn(offset, base=now_base)[2]:
            return hms(
                seconds(trip_stoptime) - seconds(offset)
            )
    return False

def a_to_b(start: tuple[float, float], end: tuple[float, float], err=False, offset: tuple=(0,0,0), now_base=None):
    global start_stops, end_stops
    if now_base is None:
        now_base = time.localtime()  # one clock read, shared by every trip check below

    now_seconds = seconds(time_rn(offset, base=now_base)[2])

    if err:
        start_stops = gtfs.stops(start, 150, 8000)
        end_stops = gtfs.stops(end, 150, 8000)
    else:
        start_stops = gtfs.stops(start)
        end_stops = gtfs.stops(end)

    possible_trips = []

    for stop in start_stops:
        try:
            sid = stop[1]["id"]
            stop_agency = stop[1]["agency"]
            sorted_trips = gtfs.sorted_stop_trips[stop_agency][sid]
        except KeyError:
            #print("e", stop)
            continue
        
        start_idx = bisect.bisect_left(sorted_trips, (now_seconds,))

        for _, trip in sorted_trips[start_idx:]:
            if not is_trip_valid(stop_agency, trip, sid, offset=offset, now_base=now_base):
                continue
            stime = gtfs.stoptrip_time[stop_agency][trip][sid][1].split(":")
            for end_stop in end_stops:
                eid = end_stop[1]["id"]
                try:
                    if eid in gtfs.trip_stops[stop_agency][trip]:
                        if gtfs.trip_stops[stop_agency][trip][sid] < gtfs.trip_stops[stop_agency][trip][eid]:
                            etime = gtfs.stoptrip_time[stop_agency][trip][eid][0].split(":")
                            time_for_transit = hms(
                                sseconds(etime) - sseconds(stime)
                            )
                            possible_trips.append((stop, end_stop, gtfs.trips_route[trip], stop_agency, time_for_transit, trip, stime, etime))
                except (KeyError, ValueError) as e:
                    #print("e2", end_stop, repr(e))
                    pass
    return possible_trips

def b_to_c(start: tuple[float, float], endstops: list, ctrip, best=-1, offset: tuple=(0,0,0), now_base=None,):
    if now_base is None:
        now_base = time.localtime()

    now_seconds = seconds(time_rn(offset, base=now_base)[2])
    start_stops = gtfs.stops(start, max_dist=50)
    ogbest = best
    btrips = []

    for stop in start_stops:
        try:
            sid = stop[1]["id"]
            stop_agency = stop[1]["agency"]
            sorted_trips = gtfs.sorted_stop_trips[stop_agency][sid]
        except KeyError:
            #print("e", stop)
            continue
        start_idx = bisect.bisect_left(sorted_trips, (now_seconds,))

        for _, trip in sorted_trips[start_idx:]:
            if trip == ctrip:
                continue
            if not is_trip_valid(stop_agency, trip, sid, offset=offset, now_base=now_base):
                continue
            stime = gtfs.stoptrip_time[stop_agency][trip][sid][1].split(":")
            for end_stop in endstops:
                eid = end_stop[1]["id"]
                try:
                    if eid in gtfs.trip_stops[stop_agency][trip]:
                        etime = gtfs.stoptrip_time[stop_agency][trip][eid][0].split(":")
                        if best == -1 or sseconds(etime) < best:
                            time_for_transit = hms(
                                sseconds(etime) - sseconds(stime)
                            )
                            btrips.append([stop, end_stop, gtfs.trips_route[trip], stop_agency, time_for_transit, trip, stime, etime])
                            #best = sseconds(etime)
                except (KeyError, ValueError) as e:
                    pass

    if best != ogbest:
        return True, best, btrips
    return False, -1, []

def a_to_b_with_transfers(start: tuple[float, float], end: tuple[float, float], offset: tuple=(0,0,0), now_base=None):
    global start_stops, end_stops
    best = float("inf")
    if now_base is None:
        now_base = time.localtime()

    now_seconds = seconds(time_rn(offset, base=now_base)[2])
    start_stops = gtfs.stops(start)
    end_stops = gtfs.stops(end)
    btrips = []

    for stop in start_stops:
        try:
            sid     = stop[1]["id"]
            sagency = stop[1]["agency"]
            sorted_trips = gtfs.sorted_stop_trips[sagency][sid]
        except KeyError:
            continue

        start_idx = bisect.bisect_left(sorted_trips, (now_seconds,))
        for time_s, trip in sorted_trips[start_idx:]:
            if not is_trip_valid(sagency, trip, sid, offset=offset, now_base=now_base):
                continue

            try:
                tsstopid = gtfs.trip_stops[sagency][trip][sid]
            except KeyError:
                continue
            
            for tstop in gtfs.trip_stops[sagency][trip]:
                if gtfs.trip_stops[sagency][trip][tstop] < tsstopid:
                    continue
                a_time = sseconds(gtfs.stoptrip_time[sagency][trip][tstop][0].split(":"))
                try:
                    btc = b_to_c(gtfs.stop_coords[sagency][tstop], end_stops, trip, offset=hms(a_time-now_seconds))
                except KeyError:
                    continue
                if btc[0]:
                    btrips.append([stop, trip, hms(btc[1]), btc[2]])

            btrips.extend(a_to_b(start, end, offset, now_base))
    
    return btrips


def get_last_startend_stops():
    return start_stops, end_stops

async def main():
    print("\n\n\n")
    await gtfs.load_save()
    print( a_to_b_with_transfers((43.452821, -80.498260), (43.479346, -80.529788)))#:
        #print(json.dumps(trip, indent=2), "\n\n\n")
    print("\n\n\n", flush=True)

if __name__ == '__main__':
    asyncio.run(main())