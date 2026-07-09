import os
import asyncio
from time import sleep
from aioconsole import ainput

#----------- Text Colors -----------
NORMAL_TEXT = "\033[0m"

RED = '\033[31m'
BLUE = '\033[0;34m'	
GREEN = '\033[0;32m'
YELLOW = '\033[0;33m'
NORMAL = 'normal'

BOLD = '\033[1;37m'

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

"""async def print_slowly(screen, *all_to_print, delay=0.03, end='\n'):
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

def sprint(screen, *all_to_print, end='\n'):
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
        print(end=end)
    return screen

async def sinput(screen):
    return screen + await ainput() """


class Screen:
    def __init__(self):
        self.screen = ''
        self.IS_WINDOWS = True if os.name == 'nt' else False
    
    def clear(self):
        if self.IS_WINDOWS:
            os.system("cls")
        else:
            os.system("clear")
        self.screen = ''

    def print(self, *all_to_print, end='\n'):
        for to_print in all_to_print:
            to_print = str(to_print)
            self.screen += to_print
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
        self.screen += end
        print(end=end)

    async def type(self, *all_to_print, delay: float = 0.03, end: str = '\n'):
        for to_print in all_to_print:
            to_print = str(to_print)
            escape_detected = False
            for char in to_print:
                if char == '\033':
                    escape_detected=True
                    print(char, end='', flush=True)
                    self.screen += char
                    continue

                if escape_detected:
                    if char != 'm':
                        print(char, end='', flush=True)
                        self.screen += char
                        continue
                    else:
                        escape_detected=False
                        print(char, end='', flush=True)
                        self.screen += char
                        continue

                print(char, end='', flush=True)
                self.screen += char
                await asyncio.sleep(delay)
        self.print(end=end)

    async def input(self):
        inp = await ainput()
        self.screen += inp + '\n'
        return inp
    
    def _scroll(self, rows=1):
        temp_screen = self.screen.split('\n')
        temp_screen = temp_screen[rows:]
        self.clear()
        self.screen = '\n'.join(temp_screen)
        print(self.screen, end='', flush=True)

    async def scroll(self, rows, time_per_row=0.4):
        for _ in range(rows):
            self._scroll(1)
            await asyncio.sleep(time_per_row)

    def delete_last_lines(self, lines=1):
        temp_screen = self.screen.split('\n')
        temp_screen = temp_screen[:-lines]

        self.clear()
        self.screen = '\n'.join(temp_screen) + '\n'
        print(self.screen, end='', flush=True)

    def remove_to_line(self, line):
        temp_screen = self.screen.split('\n')
        temp_screen = temp_screen[:line]

        self.clear()
        self.screen = '\n'.join(temp_screen) + '\n'
        print(self.screen, end='', flush=True)

    @property
    def lines(self):
        return self.screen.split('\n')
    
    @property
    def nlines(self):
        return len(self.lines)