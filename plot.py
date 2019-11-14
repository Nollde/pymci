# -*- coding: utf-8 -*-

import os

import json
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

from geo import epsg_trafo
from utils import crap_string_to_float, extract_lat_lng
from plotting import plot_map


def plot_centers():
    # load csv file
    points = pd.read_csv("cities/bonn/Ortsteile__Bonn/Ortsteile__Bonn.csv", sep=";")
    points["POINT_X"] = points["POINT_X"].apply(crap_string_to_float)
    points["POINT_Y"] = points["POINT_Y"].apply(crap_string_to_float)
    geometry = [
        Point(epsg_trafo(*xy, from_coords="epsg:4326", to_coords="epsg:3857"))
        for xy in zip(points["POINT_X"], points["POINT_Y"])
    ]
    crs = {"init": "epsg:3857"}

    points_df = gpd.GeoDataFrame(points, crs=crs, geometry=geometry)
    plot_map([points_df])


def plot_stores(category="essen"):
    # load store data
    store_path = os.path.join("cities", "bonn", "stores", "checked", category, "checked.json")
    df = pd.read_json(store_path)
    lat_lngs = pd.DataFrame(df["geometry"].apply(extract_lat_lng).tolist(), columns=["lat", "lng"])
    df = pd.concat([df, lat_lngs], axis=1)

    # geometry = [
    #     Point(epsg_trafo(xy["lng"], xy["lat"], from_coords="epsg:4326", to_coords="epsg:3857"))
    #     for index, xy in lat_lngs.iterrows()
    # ]
    geometry = gpd.points_from_xy(df.lng, df.lat)
    crs = {"init": "epsg:4326"}
    points_df = gpd.GeoDataFrame(df, crs=crs, geometry=geometry).to_crs({"init": "epsg:3857"})

    plot_map(
        points_dfs=[points_df[points_df.cat.apply(lambda x: x[0]) == val] for val in range(6)],
        labels=[
            "discounter",
            "supermarkt",
            "biosupermarkt",
            "bioladen",
            "unverpackladen",
            "biowochenmarkt",
        ],
    )


def main():
    plot_stores()


if __name__ == "__main__":
    main()
