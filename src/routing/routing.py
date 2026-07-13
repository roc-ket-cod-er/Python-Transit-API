import transit
import walking


def route(start: tuple[float, float], end: tuple[float, float]):
    trip = transit.a_to_b(start, end)[0]
    starting_stop, ending_stop, trip_id = trip

    print(starting_stop, ending_stop, trip_id)

if __name__ == '__main__':
    route((43.498310, -80.529517), (43.462290, -80.523532))