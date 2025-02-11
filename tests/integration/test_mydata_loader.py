from pathlib import Path

import pytest
from django.core.management import call_command

from demo.settings import DOWNLOAD_DIR

pytestmark = pytest.mark.django_db


@pytest.fixture
def csv_file():
    return Path(DOWNLOAD_DIR).joinpath("MyEBirdData.csv")


def test_load_sample_dataset(csv_file):
    call_command("load_mydata", csv_file, "Etta Lemon")
