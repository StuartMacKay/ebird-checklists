Changelog
=========
All notable changes to this project will be documented in this file.
The format is inspired by `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

Latest
------

0.7.0 (2025-01-31)
------------------
* Added APILoader.load_species() for adding Species records to the database.
* Changed APILoader to load species from the eBird taxonomy when loading a checklist.
* Removed SpeciesLoader. It is no longer needed.

0.6.5 (2025-01-29)
------------------
* Added APILoader.load_location() for adding or updating database records.
* Changed APILoader so it accurately counts the number of checklists added.
* Changed APILoader so it handles checklists where the time is not set.

0.6.4 (2025-01-27)
------------------
* Added tests for the APILoader and fixed several bugs from the recent refactoring.

0.6.3 (2025-01-26)
------------------
* Updated docs to include all recent changes.

* Fixed an error/oversight where the observations were always updated
  when a checklist was downloaded.

0.6.2 (2025-01-25)
------------------
* Reorganised the APILoader to simplify adding new features - stay tuned.

0.6.1 (2025-01-24)
------------------
* Added check for number of observers, which is optional for incidental checklists.

0.6.0 (2025-01-23)
------------------
* Added flag to APILoader so checklists can be updated even if the edited
  timestamp is unchanged.

* Added field to Checklist for recording the date and time the checklist
  added to eBird.

* Added JSON fields to each model so projects using this app can add their
  own features.

* Removed created and modified timestamp fields from models.

0.5.0 (2025-01-20)
------------------
* Added load_checklist() to APILoader so individual checklists can be updated.
* Changed APILoader method names; load becomes load_checklists, etc.

0.4.2 (2025-01-20)
------------------
* Changed APILoader to handle the fields for distance and area which were renamed
  by eBird, but the change was not documented.

* Changed APILoader to round decimal values for distance and area to three decimal
  places to address any precision issues when converted from floats.

* Removed LocationManager with methods to return lists of choices. This was really
  the wrong place to put code like this.

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
