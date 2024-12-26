"""
load_csv.py

A Django management command for loading observations from A CSV file,
either containing the eBird Basic Dataset or My eBird Data.

Usage:
    python manage.py load_csv  <path>

Arguments:
    <path> Required. The path to the CSV file.

Examples:
    python manage.py load_csv data/downloads/MyEBirdData.csv

Notes:
    1. The eBird Basic Dataset has a unique identifier, which never changes,
       for every observation, even if the species changes. That means you
       can load the dataset multiple times. If any of the data changes, the
       Observation will be updated.

    2. Conversely, downloads for My eBird Data do not have a unique identifier.
       That means you must delete all the records before you load the latest
       download, otherwise duplicate records will be created.
"""

from django.core.management.base import BaseCommand

from checklists.loaders import BasicDatasetLoader, MyDataLoader


class Command(BaseCommand):
    help = "Load checklists from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument("path", type=str)

    def _is_basic_dataset(self, path: str):
        with open(path) as csv_file:
            headers = csv_file.readline()
            return "GLOBAL UNIQUE IDENTIFIER" in headers

    def handle(self, *args, **options):
        path = options["path"]

        if not path.exists():
            raise IOError('File "%s" does not exist' % path)

        if self._is_basic_dataset(path):
            loader = BasicDatasetLoader()
        else:
            loader = MyDataLoader()

        loader.load(options["path"])
