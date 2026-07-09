import os
import time
import asyncio

#----------- Text Colors -----------
IS_WINDOWS = True if os.name == 'nt' else False
NORMAL_TEXT = "\033[0m"

RED = '\033[31m'
BLUE = '\033[0;34m'	
GREEN = '\033[0;32m'
YELLOW = '\033[0;33m'
NORMAL = 'normal'

BOLD = '\033[1;37m'

async def clear(screen, after=0):
    await asyncio.sleep(after)
    if IS_WINDOWS:
        os.system("cls")
    else:
        os.system("clear")
    screen = ""

def red(*strings, end=''):
    tbr = RED
    for string in strings:
        tbr += str(string)
        if string != strings[-1]:
            tbr += ' '
    tbr += NORMAL_TEXT
    tbr += end
    return tbr

def green(*strings, end=''):
    tbr = GREEN
    for string in strings:
        tbr += str(string)
        if string != strings[-1]:
            tbr += ' '
    tbr += NORMAL_TEXT
    tbr += end
    return tbr

def blue(*strings, end=''):
    tbr = BLUE
    for string in strings:
        tbr += str(string)
        if string != strings[-1]:
            tbr += ' '
    tbr += NORMAL_TEXT
    tbr += end
    return tbr

def yellow(*strings, end=''):
    tbr = YELLOW
    for string in strings:
        tbr += str(string)
        if string != strings[-1]:
            tbr += ' '
    tbr += NORMAL_TEXT
    tbr += end
    return tbr

def bold(*strings, end=''):
    tbr = BOLD
    for string in strings:
        tbr += str(string)
        if string != strings[-1]:
            tbr += ' '
    tbr += NORMAL_TEXT
    tbr += end
    return tbr

async def print_slowly(screen, *all_to_print, delay=0.03, end='\n'):
    for to_print in all_to_print:
        to_print = str(to_print)
        screen += to_print
        escape_detected = False
        for char in to_print:
            if char == '\033':
                escape_detected=True

            if escape_detected:
                if char != 'm':
                    print(char, end='', flush=True)
                    continue
                else:
                    escape_detected=False

            print(char, end='', flush=True)
            if char == '\n':
                continue
            await asyncio.sleep(delay)
        print(end=end)
    return screen

async def sprint(screen, *all_to_print, end='\n'):
    return await print_slowly(screen, *all_to_print, end=end)