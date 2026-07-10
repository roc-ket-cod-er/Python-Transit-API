import requests
from geopy.distance import geodesic

WALK_SPEED_KMH = 6

def walking_time_minutes(start: list, end: list) -> float:
    distance_km = geodesic(start, end).km
    return distance_km / WALK_SPEED_KMH * 60

def find_best_route(start: list, end: list) -> list:
    distance_km = geodesic(start, end).km
    time_min = walking_time_minutes(start, end)