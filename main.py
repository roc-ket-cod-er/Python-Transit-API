# Main.py

from print_color import *
from time import sleep
import asyncio
import socket
import geopy
from geopy.geocoders import Nominatim

s = Screen()
geolocator = Nominatim(user_agent="Python Transit API")

def addr_to_loc(address: str) -> list:
    try:
        location = geolocator.geocode(address)
        return [location.latitude, location.longitude]
    except (socket.gaierror, geopy.exc.GeocoderUnavailable):
        return ["NO WIFI"]

async def get_start_coord():
    await s.type("I want to go from: ", end="")
    try:
        start_coord = await s.input()
        start_coord = list(map(float, start_coord.split(",")))

        if start_coord[0] < 0:
            start_coord[0] = [abs(start_coord[0]), "S"]
        else:
            start_coord[0] = [start_coord[0], "N"]

        if start_coord[1] < 0:
            start_coord[1] = [abs(start_coord[1]), "W"]
        else:
            start_coord[1] = [start_coord[1], "E"]
        return start_coord
    except (ValueError, IndexError):
        start_coord = addr_to_loc(start_coord)

        if start_coord[0] < 0:
            start_coord[0] = [abs(start_coord[0]), "S"]
        else:
            start_coord[0] = [start_coord[0], "N"]

        if start_coord[1] < 0:
            start_coord[1] = [abs(start_coord[1]), "W"]
        else:
            start_coord[1] = [start_coord[1], "E"]
        return start_coord

        await s.type(red("Invalid input. Please enter the coordinates in the format: latitude, longitude\n"), delay=0.01)
        return await get_start_coord()

async def get_end_coord(start_coord, error=False):
    if not error:
        s.delete_last_lines(2)
        s.print(f"I want to go from : {bold(blue(f'{start_coord[0][0]} {start_coord[0][1]}, {start_coord[1][0]} {start_coord[1][1]}'))}", end="")
    else:
        s.delete_last_lines(1)
        await s.type(f"I want to go from : {bold(blue(f'{start_coord[0][0]} {start_coord[0][1]}, {start_coord[1][0]} {start_coord[1][1]}'))}", end="", delay=0.01)
    await s.type("  to ", end="")

    try:
        end_coord = await s.input()
        end_coord = list(map(float, end_coord.split(",")))

        if end_coord[0] < 0:
            end_coord[0] = [abs(end_coord[0]), "S"]
        else:
            end_coord[0] = [end_coord[0], "N"]

        if end_coord[1] <= 0:
            end_coord[1] = [abs(end_coord[1]), "W"]
        else:
            end_coord[1] = [end_coord[1], "E"]
        return end_coord
    except (ValueError, IndexError):
        end_coord = addr_to_loc(end_coord)
        
        if end_coord[0] < 0:
            end_coord[0] = [abs(end_coord[0]), "S"]
        else:
            end_coord[0] = [end_coord[0], "N"]

        if end_coord[1] < 0:
            end_coord[1] = [abs(end_coord[1]), "W"]
        else:
            end_coord[1] = [end_coord[1], "E"]
        return end_coord

        await s.type(red("\nInvalid input. Please enter the coordinates in the format: latitude, longitude"), delay=0.01)
        return await get_end_coord(start_coord, error=True)

async def main():
    s.pinned_text = bold("\n-------------------- Welcome to the Transit API! --------------------\n")
    s.clear()
    await asyncio.sleep(0.4)
    await s.type("This program will help you find the best route between two locations.\n")

    start_coord = await get_start_coord()
    end_coord = await get_end_coord(start_coord)

    await s.type(
        f"\nCalculating the best route between {bold(blue(f'{start_coord[0][0]} {start_coord[0][1]}, {start_coord[1][0]} {start_coord[1][1]}'))} and {bold(blue(f'{end_coord[0][0]} {end_coord[0][1]}, {end_coord[1][0]} {end_coord[1][1]}'))} ...\n\n",
         delay=0.01
    )
    await s.scroll(s.nlines-8, time_per_row=0.05)
    await s.scroll(4)

asyncio.run(main())