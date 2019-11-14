# -*- coding: utf-8 -*-

import os
import time
import glob

import pandas as pd
import json
import googlemaps
from geopy.geocoders import Nominatim

from cities.bonn.openstreetmap.city import city_names as bonn
from categories import categories
from utils import json_dump, get_coords
from keys import google_api_key


def locate_citycenters():
    city = {}
    geolocator = Nominatim(user_agent="test_01")

    geostring = ""

    for bezirk in bonn.keys():
        bezirk_dict = {}
        for stadtteil in bonn[bezirk]:
            st = geolocator.geocode(stadtteil)

            bezirk_dict[stadtteil] = {
                "address": st.address,
                "lat": st.latitude,
                "lon": st.longitude,
                "place_id": st.raw["place_id"],
            }
        city[bezirk] = bezirk_dict

    path = os.path.join("cities", "bonn", "city_centers.json")
    json_dump(city, path)


def make_queries(category="essen"):
    gmaps = googlemaps.Client(key=google_api_key)
    storage = []
    store_categories = categories[category]

    for store_category_name in store_categories.keys():
        index = 0
        store_category = store_categories[store_category_name]
        store_category_query = store_category["query"]

        next_page_token = ""
        if store_category_query is None:
            raise NameError
        while True:
            # make query
            query = store_category_query + " " + "Bonn"
            places = gmaps.places(query, page_token=next_page_token)
            # print(query, places)
            storage.append(places)

            # save query
            path = os.path.join(
                "cities",
                "bonn",
                "queries",
                category,
                store_category_name,
                "{}_{}.json".format(store_category_name, index),
            )
            json_dump(places, path)

            index += 1
            next_page_token = places.get("next_page_token", None)
            if next_page_token is None:
                break


def merge_queries(category="essen"):
    store_categories = categories[category]
    all_results = []

    for store_category_name in store_categories.keys():
        store_category = store_categories[store_category_name]
        path = os.path.join("cities", "bonn", "stores", "queries", category, store_category_name)
        fs = glob.glob(os.path.join(path, store_category_name + "_*.json"))
        for f in fs:
            with open(f) as json_file:
                data = json.load(json_file)
                results = data["results"]
                for result in results:
                    result["cat"] = store_category["id"]
                    all_results.append(result)

    path = os.path.join("cities", "bonn", "stores", "merged", category, "merged.json")
    json_dump(all_results, path)


def clean_queries(category="essen"):
    cleaned_results = []
    merged_path = os.path.join("cities", "bonn", "stores", "merged", category)

    with open(merged_path + "/merged.json") as json_file:
        data = json.load(json_file)

    for result in data:
        result["cat"] = [result["cat"]]
        for cleaned_result in cleaned_results:
            if result["id"] == cleaned_result["id"]:
                cleaned_result["cat"] += result["cat"]
                break
        else:
            cleaned_results.append(result)

    path = os.path.join("cities", "bonn", "stores", "cleaned", category, "cleaned.json")
    json_dump(cleaned_results, path)


def csv_clean_queries(category="essen"):
    duplicates = []
    csv = "ID;NAME;ADDRESS;CAT\n"

    cleaned_path = os.path.join("cities", "bonn", "stores", "cleaned", category)
    with open(os.path.join(cleaned_path, "cleaned.json")) as f:
        data = json.load(f)

    for result in data:
        id = result["id"]
        name = result["name"]
        address = result["formatted_address"].split(",")[0]
        cat = ",".join(str(c) for c in result["cat"])
        csv += "{};{};{};{}\n".format(id, name, address, cat)

    os.makedirs(cleaned_path, exist_ok=True)
    with open(os.path.join(cleaned_path, "cleaned.csv"), "w") as f:
        f.write(csv)


def find_store(stores, id):
    for store in stores:
        if id == store["id"]:
            return store


def handle_checked_queries(category="essen"):
    cleaned_file = "cleaned_added_missing.json"

    checked = []
    checked_path = os.path.join("cities", "bonn", "stores", "checked", category)
    checked_csv = pd.read_csv(os.path.join(checked_path, "checked.csv"), delimiter=";")

    cleaned_path = os.path.join("cities", "bonn", "stores", "cleaned", category)
    with open(os.path.join(cleaned_path, cleaned_file)) as f:
        cleaned_stores = json.load(f)

    for index, row in checked_csv.iterrows():
        id, cats = row["ID"], row["CAT"]

        store = find_store(cleaned_stores, id)
        if store is None:
            continue

        if isinstance(cats, int):
            cats = [cats]
        else:
            cats = [int(cat) for cat in cats.split(",")]
        store["cat"] = cats
        checked.append(store)

    path = os.path.join(checked_path, "checked.json")
    json_dump(checked, path)


def generate_checked_store_csv(category="essen"):
    checked_path = os.path.join("cities", "bonn", "stores", "checked", category)
    with open(os.path.join(checked_path, "checked.json")) as f:
        data = json.load(f)

    store_categories = categories[category]
    csv = "NAME;LAT;LON;CAT\n"
    for store in store_categories.values():
        store_id = store["id"]
        for result in data:
            if store_id in result["cat"]:
                name = result["name"]
                lat, lon = get_coords(result)
                csv += "{};{};{};{}\n".format(name, lat, lon, store_id)

    os.makedirs(checked_path, exist_ok=True)
    with open(os.path.join(checked_path, "checked_geom.csv".format(store_id)), "w") as f:
        f.write(csv)


def main():
    make_queries(category="essen")
    make_queries(category="bekleidung")

    merge_queries(category="essen")
    merge_queries(category="bekleidung")

    clean_queries(category="essen")
    clean_queries(category="bekleidung")

    csv_clean_queries(category="essen")
    csv_clean_queries(category="bekleidung")

    handle_checked_queries(category="essen")
    handle_checked_queries(category="bekleidung")

    generate_checked_store_csv(category="essen")
    generate_checked_store_csv(category="bekleidung")


if __name__ == "__main__":
    main()
