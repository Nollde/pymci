# -*- coding: utf-8 -*-

import os
import json
import numpy as np

measures = ["dur", "dist"]
mobilities = ["car", "foot", "bicycle", "transit"]

additional = ["coupling"]


def find_center_name(city, id):
    for bez in city.keys():
        for center_name in city[bez].keys():
            if city[bez][center_name]["id"] == id:
                return center_name


def sort_stores(store_list, metric="dist_food"):
    potential_stores = []
    dists = []
    for store in store_list:
        potential_stores.append(store)
        dists.append(store["dist_foot"])
    return [potential_stores[el] for el in np.argsort(dists)]


def csv_routed_queries(category="essen"):
    duplicates = []
    csv_head = "CENTER_ID;"
    center_csv = ""
    write_head = True
    routed_path = os.path.join("cities", "bonn", "stores", "routed", category)
    with open(os.path.join(routed_path, "routed.json")) as f:
        data = json.load(f)

    city_path = os.path.join("cities", "bonn", "city.json")
    with open(city_path) as json_file:
        city = json.load(json_file)

    for center_id in data.keys():
        center_csv += find_center_name(city, center_id)
        for cat in data[center_id].keys():
            meas = []
            stores = sort_stores(data[center_id][cat])
            for i_store, store in enumerate(stores):
                for measure in measures:
                    for mobility in mobilities:
                        if write_head:
                            csv_head = "_".join(
                                [
                                    csv_head,
                                    "CAT_%s" % cat,
                                    "STORE_%s" % i_store,
                                    measure.upper(),
                                    mobility.upper(),
                                ]
                            )
                            csv_head += ";"
                        value = store["_".join([measure, mobility])]
                        if measure == "dur" and mobility == "foot":
                            meas.append(value)
                        center_csv = ";".join([center_csv, str(value)])
                for add in additional:
                    if write_head:
                        csv_head = "_".join(
                            [csv_head, "CAT_%s" % cat, "STORE_%s" % i_store, add.upper()]
                        )
                        csv_head += ";"
                    center_csv = ";".join([center_csv, str(store[add])])
            if write_head:
                csv_head = "_".join([csv_head, "CAT_%s" % cat, "MEAN_FOOT_DUR"])
                csv_head += ";"
            center_csv = ";".join([center_csv, str(sum(meas) / len(meas))])
        if write_head:
            csv_head += "\n"
            write_head = False
        center_csv += "\n"

    csv = csv_head + center_csv
    csv = csv.replace(".", ",")
    os.makedirs(routed_path, exist_ok=True)
    with open(os.path.join(routed_path, "routed.csv"), "w") as f:
        f.write(csv)


def main():
    csv_routed_queries("essen")
    csv_routed_queries("bekleidung")


if __name__ == "__main__":
    main()
