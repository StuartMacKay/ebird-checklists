import pytest
from django.core.management import call_command

pytestmark = pytest.mark.django_db


def test_load_checklists(country):
    call_command("load_api", "new", 7, country)
