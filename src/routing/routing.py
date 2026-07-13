import transit
import walking


def route(start: tuple[float, float], end: tuple[float, float]):
    trip = transit.a_to_b(start, end)[0]
    starting_stop, ending_stop, trip_id = trip