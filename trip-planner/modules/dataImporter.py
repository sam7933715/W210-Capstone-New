"""This module defines functions to import the data."""

from modules.constants import YELP_DATASETS
import pandas as pd
import os
from pyspark.sql import SparkSession

path = os.getcwd()

splits = os.path.split(path)
tail = splits[1]
while tail != "data":
    splits = os.path.split(path)
    path = splits[0]
    tail = splits[1]
    if tail in ["/c", "/Users"]:
        raise ValueError("Cannot find /data directory")


def yelp_import(size="large", application="pandas", path=path):
    """This returns a dictionary of DFs with the Yelp Data.

    Args:
        size - str: A string denoting if the dataset import should be the full dataset or a smaller dataset.
    """

    if size == "small":
        path_start = os.path.join(path, "yelp_dataset", "smaller")
    else:
        path_start = os.path.join(path, "yelp_dataset")

    spark = (
        None
        if application == "pandas"
        else SparkSession.builder.master("local[1]")
        .appName("tripPlanning")
        .getOrCreate()
    )

    end_dict = {}
    for name, file_name in YELP_DATASETS.items():
        path = os.path.join(path_start, file_name)
        if application == "pandas":
            end_dict[name] = pd.read_json(path, lines=True)
        else:
            end_dict[name] = spark.read.json(path)
    return end_dict, spark
