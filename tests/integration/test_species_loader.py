import pytest

from ebird.checklists.loaders import SpeciesLoader

pytestmark = pytest.mark.django_db


def test_load_taxonomy(api_key):
    loader = SpeciesLoader(api_key)
    loader.load()
