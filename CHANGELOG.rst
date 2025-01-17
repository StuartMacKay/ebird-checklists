Changelog
=========
All notable changes to this project will be documented in this file.
The format is inspired by `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

Latest
------

0.4.1 (2025-01-19)
------------------
* Changed ChecklistQuerySet methods for_country(), for_state() and for_county()
  so the argument can be either an eBird code or a name.

* Added LocationManager with methods to return lists of choice for country, state,
  and county names to make it easy to build autocomplete fields.

0.4.0 (2025-01-18)
------------------
* Changed QuerySet methods for Checklists, Observations and Locations. These are
  breaking changes.

[0.3.1] - 2025-01-08
--------------------
* Fixed bug where checklists would be downloaded twice if checklists were fetched
  from sub-regions.

[0.3.0] - 2025-01-08
--------------------
* Changed APILoader to load the checklists for a sub-region if the number of results
  returned matches the API's result limit.

* Refactored APILoader to make it easier to reuse.

[0.2.0] - 2025-01-06
--------------------
* Removed APILoader.recent() - it's simply to call the ebird.api.get_visits() method,
  extract the dates and then call APILoader.load()

[0.1.0] - 2024-12-28
--------------------
* Initial release with loaders and models for the database and a Django Admin module
  for viewing the data downloaded from eBird.
