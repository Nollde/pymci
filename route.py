# -*- coding: utf-8 -*-

import os
from collections import defaultdict
from datetime import datetime

import json
import osrm
import geopy.distance
from tqdm import tqdm
import googlemaps

from categories import categories
from utils import json_dump, get_coords
from keys import google_api_key

ports = {"car": 5000, "bicycle": 5001, "foot": 5002}

transit_queries = []


def route_gmaps(start, stop, mobility="transit"):
    if start[0] < 25.0 and start[1] > 25:
        # change lat and longitude
        start = (start[1], start[0])
        stop = (stop[1], stop[0])

    gmaps = googlemaps.Client(key=google_api_key)
    departure_time = datetime(2019, 11, 13, 16, 0)
    directions_result = gmaps.directions(start, stop, mode="transit", departure_time=departure_time)

    global transit_queries
    transit_queries += directions_result

    distance = directions_result[0]["legs"][0]["distance"]["value"]
    duration = directions_result[0]["legs"][0]["duration"]["value"]

    return distance, duration


def route_osrm(start, stop, mobility="car"):
    port = ports[mobility]
    client = osrm.Client(host="http://localhost:{}".format(port))
    response = client.route(coordinates=[start, stop])
    distance = response["routes"][0]["distance"]
    duration = response["routes"][0]["duration"]
    return distance, duration


def route(start, stop, mobility="car"):
    if mobility in ports.keys():
        distance = route_osrm(start, stop, mobility)
    else:
        distance = route_gmaps(start, stop, mobility)
    return distance


def routes(city, stores, mobility="car", category="essen", test=False):
    path = os.path.join("cities", "bonn", "routes", category, mobility, "routes.json")
    if os.path.exists(path):
        with open(path) as f:
            routes = json.load(f)
    else:
        routes = {}
        query_counter = 0
        for bezirk in city.keys():
            for center in tqdm(city[bezirk].values()):
                center_id = center["id"]
                center_coords = center["lon"], center["lat"]
                routes[center_id] = {}
                for store in stores:
                    store_id = store["id"]
                    store_location = store["geometry"]["location"]
                    store_coords = store_location["lng"], store_location["lat"]

                    query_counter += 1
                    distance, duration = route(center_coords, store_coords, mobility)

                    routes[center_id][store_id] = {"dist": distance, "dur": duration}
                    if test:
                        print("Did 1 test-query")
                        json_dump(routes, path)
                        return routes
                if mobility == "transit":
                    global transit_queries
                    json_dump(
                        {"queries": transit_queries},
                        os.path.join(
                            "cities", "bonn", "routes", category, mobility, "queries.json"
                        ),
                    )
        print("Did ", query_counter, " queries")
        json_dump(routes, path)
    return routes


def centers_to_stores(city, stores, category="essen", max_stores=3):
    routed_city = {}
    car_routes = routes(city, stores, "car", category)
    bicycle_routes = routes(city, stores, "bicycle", category)
    foot_routes = routes(city, stores, "foot", category)
    transit_routes = routes(city, stores, "transit", category)

    for bezirk in city.keys():
        for center in tqdm(city[bezirk].values()):
            center_id = center["id"]
            routed_city[center_id] = defaultdict(list)
            for cat in categories[category].values():
                all_stores = []
                all_distances_foot = []
                for store in stores:
                    store_copy = store.copy()

                    if cat["id"] in store_copy["cat"]:
                        store_id = store_copy["id"]

                        store_copy["dur_car"] = car_routes[center_id][store_id]["dur"]
                        store_copy["dist_car"] = car_routes[center_id][store_id]["dist"]

                        store_copy["dur_bicycle"] = bicycle_routes[center_id][store_id]["dur"]
                        store_copy["dist_bicycle"] = bicycle_routes[center_id][store_id]["dist"]

                        store_copy["dur_foot"] = foot_routes[center_id][store_id]["dur"]
                        store_copy["dist_foot"] = foot_routes[center_id][store_id]["dist"]

                        store_copy["dur_transit"] = transit_routes[center_id][store_id]["dur"]
                        store_copy["dist_transit"] = transit_routes[center_id][store_id]["dist"]

                        coupling = 0
                        store_coords = get_coords(store)

                        for coupling_store in stores:
                            coupling_store_coords = get_coords(coupling_store)
                            if (
                                geopy.distance.distance(store_coords, coupling_store_coords).km
                                < 0.5
                            ):
                                coupling += 1

                        store_copy["coupling"] = coupling
                        # store["duration_bicycle"] = duration_bicycle
                        # store["distance_bicycle"] = distance_bicycle
                        # store["duration_foot"] = duration_foot
                        # store["distance_foot"] = distance_foot

                        # first append all stores to list
                        all_stores.append(store_copy)
                        all_distances_foot.append(store_copy["dist_foot"])

                max_distance_foot = (
                    sorted(all_distances_foot)[max_stores - 1]
                    if max_stores <= len(all_distances_foot)
                    else 1e9
                )

                # only take "max_stores" closest stores when going by foot
                for store in all_stores:
                    if store["dist_foot"] <= max_distance_foot:
                        routed_city[center_id][cat["id"]].append(store)
    return routed_city


def route_city(category="essen"):
    # load city data
    city_path = os.path.join("cities", "bonn", "city.json")
    with open(city_path) as json_file:
        city = json.load(json_file)

    # load store data
    store_path = os.path.join("cities", "bonn", "stores", "checked", category, "checked.json")
    with open(store_path) as json_file:
        stores = json.load(json_file)

    # make routed city
    routed_city = centers_to_stores(city, stores, category)

    # save routed city
    path = os.path.join("cities", "bonn", "stores", "routed", category)
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, "routed.json"), "w") as f:
        json.dump(routed_city, f)


def main():
    # route_city("essen")
    route_city("bekleidung")


if __name__ == "__main__":
    main()
