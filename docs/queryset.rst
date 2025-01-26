==================
QuerySet Reference
==================

The Checklist and Observation models each have a custom QuerySet with a rich set of
methods for querying the database.

Checklists
==========

+-----------------------------------------+----------------------------------------+
| QuerySet Method                         | Fetch Checklists...                    |
+-----------------------------------------+----------------------------------------+
| for_country(self, value: str)           | for a given country code               |
+-----------------------------------------+----------------------------------------+
| for_state(self, value: str)             | for a given state code                 |
+-----------------------------------------+----------------------------------------+
| for_county(self, value: str)            | for a given county code                |
+-----------------------------------------+----------------------------------------+
| for_location(self, value: str)          | for a given location                   |
+-----------------------------------------+----------------------------------------+
| for_identifier(self, value: str)        | get a specific checklist               |
+-----------------------------------------+----------------------------------------+
| for_date(self, date: date)              | for a given date                       |
+-----------------------------------------+----------------------------------------+
| for_dates(self, start: date, end: date) | for a given range of dates             |
+-----------------------------------------+----------------------------------------+
| for_protocol(self, value: str)          | for a given protocol code              |
+-----------------------------------------+----------------------------------------+
| for_observer(self, name: str)           | for a given observer's code or name    |
+-----------------------------------------+----------------------------------------+
| for_hotspots(self)                      | exclude private locations              |
+-----------------------------------------+----------------------------------------+
| complete(self, name: str)               | only include full checklists           |
+-----------------------------------------+----------------------------------------+

Examples:

.. code-block:: python

    Checklist.objects.for_country("US")
    Checklist.objects.for_state("New York")
    Checklist.objects.for_county("US-NY-109")
    Checklist.objects.for_location("L901738")
    Checklist.objects.for_identifier("S108412716")
    Checklist.objects.for_date(datetime.date.today())
    Checklist.objects.for_protocol("P21")
    Checklist.objects.for_observer("obsr2929208")
    Checklist.objects.for_observer("Etta Lemon")
    Checklist.objects.for_hotspots()
    Checklist.objects.complete()

IMPORTANT: The ``for_dates()`` methods includes checklist submitted on the start
date, up to, but **not** including the end date. That makes it easier to construct
ranges of dates with out needing to know how many days are in a month:

.. code-block:: python

    import datetime
    from dateutil.relativedelta import relativedelta

    # Get checklists for each month
    for month in range(1, 13):
        start = datetime.date(2025, month, 1)
        end = start + relativedelta(months=+1)
        checklists = Checklist.objects.for_dates(start, end)
        ...

The great thing about Django QuerySets is that you can combine the methods
to build more complex queries:

.. code-block:: python

    Checklist.objects.for_county("US-NY-109").for_hotspots().complete()


Observations
============

The Observation model has an almost identical set of methods:

+-----------------------------------------------------------+--------------------------------+
| QuerySet Method                                           | Fetch Checklists...            |
+-----------------------------------------------------------+--------------------------------+
| for_country(self, value: str)                             | for a given country code       |
+-----------------------------------------------------------+--------------------------------+
| for_state(self, value: str)                               | for a given state code         |
+-----------------------------------------------------------+--------------------------------+
| for_county(self, value: str)                              | for a given county code        |
+-----------------------------------------------------------+--------------------------------+
| for_location(self, value: str)                            | for a given location           |
+-----------------------------------------------------------+--------------------------------+
| for_identifier(self, value: str)                          | get a specific observation     |
+-----------------------------------------------------------+--------------------------------+
| for_date(self, date: datetime.date)                       | for a given date               |
+-----------------------------------------------------------+--------------------------------+
| for_dates(self, start: datetime.date, end: datetime.date) | for a given range of dates     |
+-----------------------------------------------------------+--------------------------------+
| for_observer(self, name: str)                             | for a given observer's name    |
+-----------------------------------------------------------+--------------------------------+

Examples:

.. code-block:: python

    Observation.objects.for_country("US")
    Observation.objects.for_state("New York")
    Observation.objects.for_county("US-NY-109")
    Observation.objects.for_location("L901738")
    Observation.objects.for_identifier("OBS1408495335")
    Observation.objects.for_date(datetime.date.today())
    Observation.objects.for_dates(start, end)
    Observation.objects.for_observer("obsr2929208")
    Observation.objects.for_observer("Etta Lemon")
