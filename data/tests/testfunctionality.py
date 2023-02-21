import pytest
import numpy as np
import pandas as pd

# This enables the import of modules from the modules package. 
from tests.context import add_packages
add_packages()

from modules.dataImporter import yelp_import

@pytest.mark.parametrize("dataset_size", ["small", "large"])
def test_import_working(dataset_size):
    """Tests that the importer isn't broken."""
    print(dataset_size)
    data = yelp_import(dataset_size)
    assert len(data) > 0
