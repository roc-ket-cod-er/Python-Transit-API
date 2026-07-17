import time

tm_year = 0
tm_mon = 1
tm_mday = 2
tm_hour = 3
tm_min = 4
tm_sec = 5

def hms(seconds: int) -> tuple[int, int, int]:
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return hours, minutes, seconds

def sseconds(t: tuple[str, str, str]) -> int:
    t = tuple(map(int, t))
    return t[0] * 3600 + t[1] * 60 + t[2]


def seconds(t: tuple[int, int, int]) -> int:
    return t[0] * 3600 + t[1] * 60 + t[2]

def time_rn(offset: tuple=(0,0,0), base=None):
    t = base if base is not None else time.localtime()

    ctime = [
        f"{ t[tm_hour]+offset[0] }:{ t[tm_min]+offset[1] }:{ t[tm_sec]+offset[2] }",
        f"{ t[tm_year] }{ t[tm_mon] :02d}{ t[tm_mday] }",
        (t[tm_hour]+offset[0], t[tm_min]+offset[1], t[tm_sec]+offset[2])
    ]

    return ctime