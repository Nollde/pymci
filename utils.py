# -*- coding: utf-8 -*-

import os
import json


def crap_string_to_float(x):
    return float(x.replace(",", "."))


def extract_lat_lng(x):
    return x["location"]["lat"], x["location"]["lng"]


def get_coords(store, mode="lalo"):
    store_location = store["geometry"]["location"]
    if mode == "lalo":
        return store_location["lat"], store_location["lng"]
    if mode == "lola":
        return store_location["lng"], store_location["lat"]


def json_dump(dictionary, filepath):
    dirname = os.path.dirname(filepath)
    os.makedirs(dirname, exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(dictionary, f)
