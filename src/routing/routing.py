import transit
import walking
import gtfs


def route(start: tuple[float, float], end: tuple[float, float]):
    trip = transit.a_to_b(start, end)[0]
    starting_stop, ending_stop, trip_id, agency = trip

    for stop in gtfs.all_stops:
        if stop["id"] == starting_stop:
            starting_stop_name = stop["name"]
        elif stop["id"] == ending_stop:
            ending_stop_name = stop["name"]

    route = []

    print(f"from {starting_stop_name} to {ending_stop_name}, use trip number {trip_id} (run by {agency})")

if __name__ == '__main__':
    print("\n\n\n\n")
    route((43.498310, -80.529517), (43.462290, -80.523532))
    print("\n\n\n\n")