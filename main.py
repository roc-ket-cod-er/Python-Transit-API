# Main.py

from print_color import *
from time import sleep
import asyncio


async def main():
    screen = ''
    screen = await clear()
    screen = await print_slowly(screen, bold("Welcome to the Transit API!\n\n"))
    await asyncio.sleep(0.4)
    screen = await print_slowly(screen, "This program will help you find the best route between two locations.")
    await asyncio.sleep(1)
    screen = await clear()
    screen = await print_slowly(screen, "I want to go from (", end="")
    screen = await print_slowly(screen, "latitude, longitu", delay=0.01, end="")
    screen = await print_slowly(screen, "de): ", end="")

    start_coord = await ainput(screen)
    start_coord = list(map(float, start_coord.split(",")))

    if start_coord[0] < 0:
        start_coord[0] = [abs(start_coord[0]), "S"]
    else:
        start_coord[0] = [start_coord[0], "N"]

    if start_coord[1] < 0:
        start_coord[1] = [abs(start_coord[1]), "W"]
    else:
        start_coord[1] = [start_coord[1], "E"]

    screen = await clear(screen)
    screen = sprint(screen, f"I want to go from (latitude, longitude): {bold(blue(f'{start_coord[0][0]} {start_coord[0][1]}, {start_coord[1][0]} {start_coord[1][1]}'))}", end="")
    screen = await print_slowly(screen, " (latitude, longitude) to ", end="")

    end_coord = await ainput(screen)
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
    await clear()
    sprint(f"\n\nThank you for providing the coordinates. Calculating the best route between {bold(blue(f'{start_coord[0][0]} {start_coord[0][1]}, {start_coord[1][0]} {start_coord[1][1]}'))} and {bold(blue(f'{end_coord[0][0]} {end_coord[0][1]}, {end_coord[1][0]} {end_coord[1][1]}'))} ...\n\n")

    await asyncio.sleep(0.3)
    await clear()
    sprint(f"\nThank you for providing the coordinates. Calculating the best route between {bold(blue(f'{start_coord[0][0]} {start_coord[0][1]}, {start_coord[1][0]} {start_coord[1][1]}'))} and {bold(blue(f'{end_coord[0][0]} {end_coord[0][1]}, {end_coord[1][0]} {end_coord[1][1]}'))} ......\n\n")
    
    await asyncio.sleep(0.3)
    await clear()
    sprint(f"Thank you for providing the coordinates. Calculating the best route between {bold(blue(f'{start_coord[0][0]} {start_coord[0][1]}, {start_coord[1][0]} {start_coord[1][1]}'))} and {bold(blue(f'{end_coord[0][0]} {end_coord[0][1]}, {end_coord[1][0]} {end_coord[1][1]}'))} .........\n\n")

asyncio.run(main())