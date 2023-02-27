import pytest
import numpy as np
import pandas as pd

# This enables the import of modules from the modules package.
from tests.context import add_packages

add_packages()

from modules.dataImporter import yelp_import
from modules import textPreProcess as tpp


@pytest.mark.parametrize(
    "dataset, app",
    [("small", "pandas"), ("small", "spark")],
)
def test_import_working(dataset, app):
    """Tests that the importer isn't broken."""
    data, spark = yelp_import(dataset, app)
    assert len(data) > 0


text_one = pd.DataFrame.from_dict(
    {"record": [1, 2, 3], "text": ["hi Bill! a the", "hi 90324 PINK", "NEVER * a to"]}
)

text_two = pd.DataFrame.from_dict(
    {
        "record": [1, 2, 3],
        "text": [
            "devil Bill! a the (*^&*&*())",
            "devil 90324 PINK (*^&&%)",
            "NEVER * a to",
        ],
    }
)


@pytest.mark.parametrize(
    "df_input,expected_map,expected_vectorizer",
    [
        (
            text_one,
            pd.Series(["hi bill a the", "hi pink", "never a to"]),
            ["hi", "pink"],
        ),
        (
            text_two,
            pd.Series(["devil bill a the", "devil pink", "never a to"]),
            ["devil", "pink"],
        ),
    ],
)
def test_textPreProcess(df_input, expected_map, expected_vectorizer):
    """Tests that the text preprocess manages the basic steps."""
    mapped_text = df_input["text"].map(tpp.map_func)
    vect = tpp.get_tokenizer(df_input, "text")

    features = vect.get_feature_names_out()

    print("FEATURES: ", features)
    print("EXPECTED_VEC: ", expected_vectorizer)

    for word in expected_vectorizer:
        assert word in features
    for word in features:
        assert word in expected_vectorizer

    print(mapped_text)

    for i in range(len(expected_map)):
        assert mapped_text[i] == expected_map[i]
