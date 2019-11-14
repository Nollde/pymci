# -*- coding: utf-8 -*-

import os

import matplotlib.pyplot as plt
import geopandas as gpd


city_shp_files = {"bonn": "cities/bonn/Ortsteile__Bonn/Ortsteile__Bonn.shp"}


def plot_map(points_dfs=[], labels=[], city="bonn", path="cities/bonn", filename="map.pdf"):
    # load shp file
    map_df = gpd.read_file(city_shp_files[city])
    # to mercator projection
    map_df = map_df.to_crs({"init": "epsg:3857"})

    # create fig, plot and save
    fig, ax = plt.subplots(1, figsize=(10, 6))
    ax.axis("equal")
    # ax.axis("off")
    ax.set_title("Bonn", fontdict={"fontsize": "25", "fontweight": "3"})

    # plot map
    map_df.plot(ax=ax, color="white", edgecolor="black")

    ax.set_xlim(plt.xlim())
    ax.set_ylim(plt.ylim())

    # plot points
    if len(points_dfs) == len(labels):
        for points_df, label in zip(points_dfs, labels):
            points_df.plot(ax=ax, markersize=2.0, label=label)
    else:
        for points_df in points_dfs:
            points_df.plot(ax=ax, markersize=1.0)

    ax.legend()
    plt.savefig(os.path.join(path, filename))
