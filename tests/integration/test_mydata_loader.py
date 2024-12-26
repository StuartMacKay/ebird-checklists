from pathlib import Path

import pytest

from demo.settings import DOWNLOAD_DIR
from ebird.checklists.loaders import MyDataLoader

pytestmark = pytest.mark.django_db


@pytest.fixture
def csv_file():
    return Path(DOWNLOAD_DIR).joinpath("MyEBirdData.csv")


def test_load_sample_dataset(csv_file):
    loader = MyDataLoader()
    loader.load(csv_file, "Etta Lemon")
