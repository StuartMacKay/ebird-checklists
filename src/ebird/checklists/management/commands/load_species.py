"""
load.py

A Django management command for loading the complete taxonomy used by eBird.

Usage:
    python manage.py [--key=<apikey>] [--locale=<code>] load_species

Options:
    --key <apikey>   Optional. Your eBird API key. If you do not specify this
                     option, the key will be taken from the EBIRD_API_KEY setting.

    --locale <code>  Optional. The two-letter language for the species common name.
                     The default is 'en' (English). You can used any language
                     supported by eBird.

You can sign up for an API key at https://ebird.org/api/keygen. You will need an
eBird account first.

Notes:
    1. You can run this command multiple times, to pick up any changes
       made by eBird, for example, to the common or scientific names of
       a species.
"""

from django.conf import settings
from django.core.management.base import BaseCommand

from ebird.checklists.loaders import SpeciesLoader


class Command(BaseCommand):
    help = "Load the complete eBird taxonomy"

    def add_arguments(self, parser):
        parser.add_argument("--key",
            action="store",
            dest="key",
            default="",
            type=str,
            help="Your key to access the eBird API")
        parser.add_argument("--locale",
            action="store_true",
            dest="locale",
            default='en',
            help="The language used for species common names")

    def handle(self, *args, **options):
        key = getattr(settings, "EBIRD_API_KEY") or options["key"]
        SpeciesLoader(key, options["locale"]).load()
