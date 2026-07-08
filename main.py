# Main.py

from print_color import *
from time import sleep
import asyncio
from aioconsole import ainput


async def main():
    clear()
    await print_slowly(bold("Welcome to the Transit API!\n\n"))
    await asyncio.sleep(0.4)
    await print_slowly("This program will help you find the best route between two locations.")
    await asyncio.sleep(1)
    clear()
    await print_slowly("I want to go from (", end="")
    await print_slowly("latitude, longitu", delay=0.01, end="")
    await print_slowly("de): ", end="")

    start_coord = await ainput()
    start_coord = list(map(float, start_coord.split(",")))

    if start_coord[0] < 0:
        start_coord[0] = [abs(start_coord[0]), "S"]
    else:
        start_coord[0] = [start_coord[0], "N"]

    if start_coord[1] < 0:
        start_coord[1] = [abs(start_coord[1]), "W"]
    else:
        start_coord[1] = [start_coord[1], "E"]

    clear()
    print(f"I want to go from (latitude, longitude): {bold(blue(f'{start_coord[0][0]} {start_coord[0][1]}, {start_coord[1][0]} {start_coord[1][1]}'))}", end="")
    await print_slowly(" (latitude, longitude) to ", end="")

    end_coord = await ainput()
    end_coord = list(map(float, end_coord.split(",")))

    if end_coord[0] < 0:
        end_coord[0] = [abs(end_coord[0]), "S"]
    else:
        end_coord[0] = [end_coord[0], "N"]

    if end_coord[1] < 0:
        end_coord[1] = [abs(end_coord[1]), "W"]
    else:
        end_coord[1] = [end_coord[1], "E"]

    await print_slowly(
        f"\n\nThank you for providing the coordinates. Calculating the best route between {bold(blue(f'{start_coord[0][0]} {start_coord[0][1]}, {start_coord[1][0]} {start_coord[1][1]}'))} and {bold(blue(f'{end_coord[0][0]} {end_coord[0][1]}, {end_coord[1][0]} {end_coord[1][1]}'))} ...\n\n",
         delay=0.01
    )
    clear()
    print(f"\n\nThank you for providing the coordinates. Calculating the best route between {bold(blue(f'{start_coord[0][0]} {start_coord[0][1]}, {start_coord[1][0]} {start_coord[1][1]}'))} and {bold(blue(f'{end_coord[0][0]} {end_coord[0][1]}, {end_coord[1][0]} {end_coord[1][1]}'))} ...\n\n")

    await asyncio.sleep(0.3)
    clear()
    print(f"\nThank you for providing the coordinates. Calculating the best route between {bold(blue(f'{start_coord[0][0]} {start_coord[0][1]}, {start_coord[1][0]} {start_coord[1][1]}'))} and {bold(blue(f'{end_coord[0][0]} {end_coord[0][1]}, {end_coord[1][0]} {end_coord[1][1]}'))} ......\n\n")
    
    await asyncio.sleep(0.3)
    clear()
    print(f"Thank you for providing the coordinates. Calculating the best route between {bold(blue(f'{start_coord[0][0]} {start_coord[0][1]}, {start_coord[1][0]} {start_coord[1][1]}'))} and {bold(blue(f'{end_coord[0][0]} {end_coord[0][1]}, {end_coord[1][0]} {end_coord[1][1]}'))} .........\n\n")

asyncio.run(main())