import requests
from geopy.distance import great_circle as GC
import json
from bs4 import BeautifulSoup

def get_distance_between_ip(ip1,ip2):
    coord1=json.loads(requests.get(f"https://ipinfo.io/{ip1}/json").text)["loc"]
    coord2 = json.loads(requests.get(f"https://ipinfo.io/{ip2}/json").text)["loc"]
    return int(str(GC(coord1,coord2).km).split(".")[0])

def get_info_by_ip(ip):
    return json.loads(requests.get(f"https://ipinfo.io/{ip}/json").text)

def get_distance_between_coord(coord1,coord2):
    return int(str(GC(coord1,coord2).km).split(".")[0])

