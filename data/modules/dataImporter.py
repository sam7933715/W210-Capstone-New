"""This module defines functions to import the data."""

from modules.constants import YELP_DATASETS
import pandas as pd
import os

path = os.getcwd()
tail = ""

while tail != "/data":
    splits = os.path.split(path)
    path = splits[0]
    tail = splits[1]
    if tail in ["/c", "/Users"]:
        raise ValueError("Cannot find /data directory")


def yelp_import(size="large"):
    """This returns a dictionary of DFs with the Yelp Data.

    Args:
        size - str: A string denoting if the dataset import should be the full dataset or a smaller dataset.
    """

    if size == "small":
        path_start = "/yelp_dataset/smaller/"
    else:
        path_start = "/yelp_dataset/"

    end_dict = {}
    for name, file_name in YELP_DATASETS.items():
        end_dict[name] = pd.read_json(path_start + file_name, lines=True)
    return end_dict
