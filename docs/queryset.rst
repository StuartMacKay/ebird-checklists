==================
QuerySet Reference
==================

The Checklist and Observation models each have a custom QuerySet with a rich set of
methods for querying the database.

Checklists
==========

+------------------------------------------------+----------------------------------------+
| QuerySet Method                                | Fetch Checklists...                    |
+------------------------------------------------+----------------------------------------+
| for_country(self, value: str)                  | for a given country or country code    |
+------------------------------------------------+----------------------------------------+
| for_state(self, value: str)                    | for a given state or state code        |
+------------------------------------------------+----------------------------------------+
| for_county(self, value: str)                   | for a given county name or county code |
+------------------------------------------------+----------------------------------------+
| for_year(self, year: int)                      | for a given year                       |
+------------------------------------------------+----------------------------------------+
| for_month(self, year: int, month: int)         | for a given month                      |
+------------------------------------------------+----------------------------------------+
| for_day(self, year: int, month: int, day: int) | for a given date                       |
+------------------------------------------------+----------------------------------------+
| for_date(self, date: datetime.date)            | for a given date                       |
+------------------------------------------------+----------------------------------------+

Examples:

.. code-block:: python

    Checklists.objects.for_country("US")
    Checklists.objects.for_state("New York")
    Checklists.objects.for_county("US-NY-109")
    Checklists.objects.for_year(2024)
    Checklists.objects.for_month(2024)

The great thing about Django QuerySets is that you can combine the methods
to build more complex queries:

.. code-block:: python

    Checklist.objects.for_county("US-NY-109").for_month(2024, 12)


Observations
============

+------------------------------------------------+----------------------------------------+
| QuerySet Method                                | Fetch Observations...                  |
+------------------------------------------------+----------------------------------------+
| for_country(self, value: str)                  | for a given country or country code    |
+------------------------------------------------+----------------------------------------+
| for_state(self, value: str)                    | for a given state or state code        |
+------------------------------------------------+----------------------------------------+
| for_county(self, value: str)                   | for a given county name or county code |
+------------------------------------------------+----------------------------------------+
| for_year(self, year: int)                      | for a given year                       |
+------------------------------------------------+----------------------------------------+
| for_month(self, year: int, month: int)         | for a given month                      |
+------------------------------------------------+----------------------------------------+
| for_day(self, year: int, month: int, day: int) | for a given date                       |
+------------------------------------------------+----------------------------------------+
| for_date(self, date: datetime.date)            | for a given date                       |
+------------------------------------------------+----------------------------------------+

Examples:

.. code-block:: python

    Observations.objects.for_country("US")
    Observations.objects.for_state("New York")
    Observations.objects.for_county("US-NY-109")
    Observations.objects.for_year(2024)
    Observations.objects.for_month(2024, 12)
