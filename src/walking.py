import aiohttp
import asyncio
import orjson

WALK_SPEED_KMH = 6
WALK_SPEED_MPS = WALK_SPEED_KMH/3.6

Coordinate = tuple[float, float]
Segment = tuple[Coordinate, Coordinate]

async def get_walking_route(session, start: tuple[float, float], end: tuple[float, float]):
    url = (
        f"https://router.project-osrm.org/route/v1/foot/"
        f"{start[1]},{start[0]};"
        f"{end[1]},{end[0]}"
    )

    params = {
        "overview": "false",
        "steps": "true",
    }

    async with session.get(url, params=params) as response:
        return await orjson.loads(response.content)

async def get_walking_routes(*coords: tuple[tuple[float, float], tuple[float, float]]):

    async with aiohttp.ClientSession() as session:
        tasks = [get_walking_route(session, *coord) for coord in coords]
        results = await asyncio.gather(*tasks)
        return results

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

def print_route(route, which=0):
    for step in route[which]["routes"][0]["legs"][0]["steps"]:
        print(format_step(step))

async def walk_route(start: tuple[float, float], end: tuple[float, float]) -> list:
    route = await get_walking_routes((start, end))
    tbr = ''
    dist = 0

    for step in route[0]["routes"][0]["legs"][0]["steps"]:
        tbr += format_step(step) + "\n"
        dist += step["distance"]

    return (tbr, round(dist), round(dist) //WALK_SPEED_MPS)

async def walk_routes(*coords: tuple[tuple[float, float], tuple[float, float]]):
    routes = await get_walking_routes(*coords)
    tbr = []
    dist = []
    for i in range(len(routes)):
        tbr.append("")
        dist.append(0)
        for step in routes[i]["routes"][0]["legs"][0]["steps"]:
            tbr[i] += format_step(step) + "\n"
            dist[i] += step["distance"]

    return list((t, round(d), round(d) // WALK_SPEED_MPS) for t, d in zip(tbr, dist))

async def main():
    print("\n\n\n")
    print(
        await walk_routes(
            (
                (43.472871, -80.541298),
                (43.452821, -80.498260)
            ),
            (
                (43.472871, -80.541298),
                (43.452821, -80.498260)
            )
        ),
    )
    print("\n\n\n")


if __name__ == '__main__':
    asyncio.run(main())