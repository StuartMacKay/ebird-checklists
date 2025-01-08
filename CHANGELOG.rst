Changelog
=========
All notable changes to this project will be documented in this file.
The format is inspired by `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

[0.3.0] - 2025-01-08
--------------------
Added
^^^^^
Updated APILoader to load the checklists for a sub-region if the number of results
returned matches the API's result limit.

Changed
^^^^^^^
Refactored APILoader to make it easier to reuse.

[0.2.0] - 2025-01-06
--------------------
Deleted
^^^^^^^
Removed APILoader.recent() - it's simply to call the ebird.api.get_visits() method,
extract the dates and then call APILoader.load()

[0.1.0] - 2024-12-28
--------------------
Added
^^^^^
Initial release with loaders and models for the database and a Django Admin module
for viewing the data downloaded from eBird.
