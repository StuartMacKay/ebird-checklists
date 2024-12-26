"""
load_api.py

A Django management command for loading observations from the eBird API.

Usage:
    python manage.py load_api [--key=<apikey>] [--days=<integer>] <region>+

Arguments:
    <region> Required. One or more national, subnational1, subnational2, or hotspot
             codes used by eBird. For example, US, US-NY, US-NY-109, L1379126

Options:
    --key <apikey>    Optional. Your eBird API key. If you do not specify this
                      option, the key will be taken from the EBIRD_API_KEY
                      setting.

    --days <integer>  Optional. The number of days to fetch checklists for.
                      The default is three, starting with today, i.e. today,
                      yesterday and the day before.

Examples:
    python manage.py load_api <apikey> US
    python manage.py load_api <apikey> US-NY
    python manage.py load_api <apikey> US-NY-109
    python manage.py load_api <apikey> L1379126
    python manage.py load_api <apikey> US-NY-109 US-NY-110
    python manage.py --days 5 <apikey> US-NY-109

Notes:
    1. The eBird API returns a maximum of 200 results. Downloading checklists
       once a day should be sufficient for all hotspots or subnational2 areas.
       For large countries or places with lots of birders downloads will have
       to be more frequent. For really large area, i.e. the USA you probably
       shouldn't be using the API at all. Instead use the data from the eBird
       Basic Dataset.

    2. The default number of three days is a trade-off between getting checklists
       that were submitted "late" and repeatedly downloading the same, unchanged,
       checklists multiple times.

    3. You could use a more sophisticated strategy by running a download every day,
       then once a week, or even once month running a download for each day in the
       period. That would catch all the late submissions and edits.

    4. The API is really a news service. For accuracy and completeness you should
       really use the eBird Basic Dataset, which is published on the 15th of each
       month.

    5. It's important to note that the data from the API has limitations. Observers
       are only identified by name. So if there are two Juan Garcias birding in a
       region, then all the observations will appear to belong to one person. Also
       the observations will not have been reviewed by moderators, so there are
       likely to be records where the identification is incorrect.

    6. You automate running the command using a scheduler such as cron. If you use
       the absolute paths to python and the command, then you don't need to deal
       with activating the virtual environment, for example:

       0 0 * * * /home/me/my-project/.venv/bin/python /home/me/my-project/manage.py load_api US-NY

       Downloads all the checklists for US-NY, every day, at midnight.

"""

import datetime

from django.conf import settings
from django.core.management.base import BaseCommand

from ebird.checklists.loaders import APILoader


class Command(BaseCommand):
    help = "Load checklists from the eBird API"

    def add_arguments(self, parser):
        parser.add_argument("regions", nargs="+", type=str)

        parser.add_argument("--key",
            action="store",
            dest="key",
            default="",
            type=str,
            help="Your key to access the eBird API")

        parser.add_argument("--days",
            action="store",
            dest="days",
            default=3,
            type=int,
            help="Load checklists for the past 'n' days")


    def handle(self, *args, **options):
        today = datetime.date.today()
        key = getattr(settings, "EBIRD_API_KEY") or options["key"]
        loader = APILoader(key)
        dates = [today - datetime.timedelta(days=n) for n in range(options["days"])]

        for region in options["regions"]:
            for date in dates:
                loader.load(region, date)
