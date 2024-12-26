from pathlib import Path

import pytest

from demo.settings import DOWNLOAD_DIR
from ebird.checklists.loaders import BasicDatasetLoader

pytestmark = pytest.mark.django_db


@pytest.fixture
def csv_file():
    return Path(DOWNLOAD_DIR).joinpath("ebird_basic_dataset_sample.csv")


def test_load_sample_dataset(csv_file):
    loader = BasicDatasetLoader()
    loader.load(csv_file)
