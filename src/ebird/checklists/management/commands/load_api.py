"""
load_api.py

A Django management command for loading observations from the eBird API.

Modes:

    add-checklists     Only load new checklists
    update-checklists  Update existing checklists

Arguments:
    <days>   Required The number of days to fetch checklists for.

    <region> Required. One or more national, subnational1, subnational2, or hotspot
             codes used by eBird. For example, US, US-NY, US-NY-109, L1379126

Examples:
    python manage.py load_api add-checklists 7 US
    python manage.py load_api add-checklists 7 US-NY
    python manage.py load_api add-checklists 7 US-NY-109
    python manage.py load_api add-checklists 7 L1379126
    python manage.py load_api add-checklists 7 US-NY-109 US-NY-110
    python manage.py load_api update-checklists 3

Notes:
    1. The eBird API returns a maximum of 200 results. The APILoader works
       around this by fetching checklists from sub-regions if necessary.
       Downloading checklists once a day should be sufficient for all hotspots
       or subnational2 areas. For large countries or places with lots of birders
       downloads will have to be more frequent. For really large area, i.e. the
       USA you shouldn't be using the API at all. Instead use the data from the
       eBird Basic Dataset.

    2. The number of checklists that are updated is relatively small, typically
       less than 1%. The problem with the eBird API is that you can only find
       out whether a checklist has changed by downloading it. In order to minimise
       the load on the eBird servers you should just add checklists and ignore
       any updates.

    3. The API is really a news service. For accuracy and completeness you should
       really use the eBird Basic Dataset, which is published on the 15th of each
       month.

    4. It's important to note that the data from the API has limitations. Observers
       are only identified by name. So if there are two Juan Garcias birding in a
       region, then all the observations will appear to belong to one person. Also
       the observations will not have been reviewed by moderators, so there are
       likely to be records where the identification is incorrect.

    5. You automate running the command using a scheduler such as cron. If you use
       the absolute paths to python and the command, then you don't need to deal
       with activating the virtual environment, for example:

       0 0 * * * /home/me/my-project/.venv/bin/python /home/me/my-project/manage.py load_api add-checklists 7 US-NY

       Downloads all the checklists for US-NY, every day, at midnight.

"""

import datetime as dt

from django.conf import settings
from django.core.management.base import BaseCommand

from ebird.checklists.loaders import APILoader


class Command(BaseCommand):
    help = "Load checklists from the eBird API"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(
            title="sub-commands",
            required=True,
        )

        add_parser = subparsers.add_parser(
            "add-checklists",
            help="Load new checklists.",
        )
        add_parser.set_defaults(method=self.add_checklists)
        add_parser.add_argument(
            "days", type=int, help="The number of previous days to load"
        )
        add_parser.add_argument(
            "regions",
            nargs="+",
            type=str,
            help="Codes for the eBird regions, e.g US-NY",
        )

        update_parser = subparsers.add_parser(
            "update-checklists",
            help="Update existing checklists.",
        )
        update_parser.set_defaults(method=self.update_checklists)
        update_parser.add_argument(
            "days", nargs=1, type=int, help="The number of previous days to load"
        )

    @staticmethod
    def get_loader() -> APILoader:
        key: str = getattr(settings, "EBIRD_API_KEY")
        locale: str = getattr(settings, "EBIRD_LOCALE")
        return APILoader(key, locale)

    @staticmethod
    def get_dates(days) -> list[dt.date]:
        today: dt.date = dt.date.today()
        return [today - dt.timedelta(days=n) for n in range(days)]

    def handle(self, *args, method, **options):
        method(*args, **options)

    def add_checklists(self, *args, **options) -> None:
        loader: APILoader = self.get_loader()
        dates: list[dt.date] = self.get_dates(options["days"])
        region: str
        date: dt.date

        for region in options["regions"]:
            for date in dates:
                loader.load_checklists(region, date)

    def update_checklists(self, *args, **options) -> None:
        loader: APILoader = self.get_loader()
        dates: list[dt.date] = self.get_dates(options["days"])
        date: dt.date

        for date in dates:
            loader.update_checklists(date)
