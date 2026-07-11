# Main.py
import geopy
import socket
import asyncio
from time import sleep
from gtfs import update
from print_color import *
from geopy.geocoders import Nominatim
from routing.walking import walk_route

s = Screen()
geolocator = Nominatim(user_agent="Python Transit API")

def addr_to_loc(address: str) -> list:
    try:
        location = geolocator.geocode(address)
        return [location.latitude, location.longitude]
    except (socket.gaierror, geopy.exc.GeocoderUnavailable):
        return ["NO WIFI"]
    
def pretty_coord(coord: list) -> str:
    lat, lon = coord

    ns = "N" if lat >= 0 else "S"
    ew = "E" if lon >= 0 else "W"

    return f"{abs(lat):.6f}° {ns}, {abs(lon):.6f}° {ew}"

async def get_start_coord():
    await s.type("I want to go from: ", end="")
    try:
        start_coord = await s.input()
        if start_coord.lower() == "update grt gtfs":
            return start_coord.lower()
        return list(map(float, start_coord.split(",")))
    except (ValueError, IndexError):
        try:
            return addr_to_loc(start_coord)
        except AttributeError as e:
            await s.type(red(f"\nInvalid input. Please try a different address/keyword or enter a coordinate ({e})"), delay=0.01)
            return await get_start_coord()

async def get_end_coord(start_coord: list, error: bool =False) -> list:
    if not error:
        s.delete_last_lines(2)
        s.print(f"I want to go from: {bold(blue(f'{pretty_coord(start_coord)}'))} to ", end="")
    else:
        s.delete_last_lines(1)
        await s.type(f"I want to go from: {bold(blue(f'{pretty_coord(start_coord)}'))} to ", end="", delay=0.01)

    try:
        end_coord = await s.input()
        return list(map(float, end_coord.split(",")))
    except (ValueError, IndexError):
        try:
            return addr_to_loc(end_coord)
        except AttributeError as e:
            await s.type(red(f"\nInvalid input. Please try a different address/keyword or enter a coordinate ({e})"), delay=0.01)
            return await get_end_coord(start_coord, error=True)

async def main() -> int:
    s.pinned_text = bold("\n-------------------- Welcome to the Transit API! --------------------\n")
    s.clear()
    await s.type(">>>", end='  ')
    inp = await s.input()

    if inp.lower() == "nav":
        await s.type("This program will help you find the best route between two locations.\n")

        start_coord = await get_start_coord()

        end_coord = await get_end_coord(start_coord)

        await s.type(
            f"\nCalculating the best route between {bold(blue(f'{pretty_coord(start_coord)}'))} and {bold(blue(f'{pretty_coord(end_coord)}'))} ...\n\n",
            delay=0.01
        )
        await s.scroll(s.nlines-8, time_per_row=0.05)
        await s.scroll(4)

        instructions = walk_route(start_coord, end_coord)
        await s.type(f"{instructions[0]}\n\nTotal distance: {instructions[1]/1000} km")

        await s.type("\n\nPress enter to restart", end="")
        await s.input()
        await main()
    elif inp.lower() == 'update':
        await s.type(bold(red("WARNING: Will create a GTFS folder in this directory. Continue? (Y/n) ")), end='', delay=0.01)
        if await s.input() == "n":
            return await main()
        s.print("updating gtfs for grt")
        update("GRT&&GO")
        return await main()
    elif inp.lower() == 'help':
        await s.type(
            f"{bold(yellow("-------------------- HELP ------------------"))}\n" +
             "A list of every command:\n\n" +
             "1. Help: List every command\n" +
            f"2. Update: Update GTFS Data\n" +
            bold("3. Nav: Start navigation software\n") +
             "Press enter to continue.",
            delay=0.01
        )
        await s.input()
        return await main()
    
    else:
        await s.type(
            red('Not a recognised command. Try "help" to get a list of commands.\nPress enter to continue.'),
            delay=0.01
        )
        await s.input()
        return await main()

    return 0

if __name__ == "__main__":
    asyncio.run(main())