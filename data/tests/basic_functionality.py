import pytest
import numpy as np

from modules.dataImporter import yelp_import

@pytest.mark.parametrize("dataset_size", ["small", "large"])
def test_import_working(dataset_size):
    """Tests that the importer isn't broken."""
    data = yelp_import(dataset_size)
    assert len(data) > 0
