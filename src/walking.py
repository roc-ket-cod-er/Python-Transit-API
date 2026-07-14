import requests

WALK_SPEED_KMH = 6

def get_walking_route(start: tuple[float, float], end: tuple[float, float]):
    url = (
        f"https://router.project-osrm.org/route/v1/foot/"
        f"{start[1]},{start[0]};"
        f"{end[1]},{end[0]}"
    )

    params = {
        "overview": "false",
        "steps": "true",
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def bearing_to_direction(bearing):
    directions = [
        "north",
        "northeast",
        "east",
        "southeast",
        "south",
        "southwest",
        "west",
        "northwest"
    ]

    index = round(bearing / 45) % 8
    return directions[index]

def format_depart(step):
    street = step["name"]
    distance = round(step["distance"])

    bearing = step["maneuver"]["bearing_after"]
    direction = bearing_to_direction(bearing)

    if street:
        return (
            f"Head {direction} on {street} "
            f"for {distance} m."
        )
    else:
        return (
            f"Head {direction} "
            f"for {distance} m."
        )

def format_step(step):
    maneuver = step["maneuver"]["type"]
    modifier = step["maneuver"].get("modifier")
    street = step["name"]
    distance = round(step["distance"])

    if maneuver == "depart":
        return format_depart(step)

    if maneuver == "turn":
        if street:
            return f"Turn {modifier} onto {street}, then continue for {distance} m."
        else:
            return f"Turn {modifier} and continue for {distance} m."

    if maneuver == "arrive":
        return "You have arrived."

    return f"Continue on {street} for {distance} m."

def print_route(route):
    for step in route["routes"][0]["legs"][0]["steps"]:
        print(format_step(step))

def walk_route(start: tuple[float, float], end: tuple[float, float]) -> list:
    route = get_walking_route(start, end)
    tbr = ''
    dist = 0

    for step in route["routes"][0]["legs"][0]["steps"]:
        tbr += format_step(step) + "\n"
        dist += step["distance"]

    return (tbr, round(dist))


if __name__ == '__main__':
    print("\n\n\n")
    print_route(
        get_walking_route(
                (43.505502, -80.522344),
                (43.50416, -80.522014)
        ),
    )
    print("\n\n\n")