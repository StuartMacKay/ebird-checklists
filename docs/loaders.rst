============
Loading Data
============
eBird Checklists has loaders for the following data sources:

1. The `eBird Basic Dataset`_, published on the 15th of each month
2. Records from `Download My Data`_ in your eBird account
3. Checklists downloaded from the `eBird API 2.0`_

.. _eBird Basic Dataset: https://support.ebird.org/en/support/solutions/articles/48000838205-download-ebird-data#anchorEBD
.. _Download My Data: https://ebird.org/downloadMyData
.. _eBird API 2.0: https://documenter.getpostman.com/view/664302/S1ENwy59


eBird Basic Dataset
-------------------
The eBird Basic Dataset is published as a zipped, tab-delimited CSV file. The
files are very large so loading them is going to take a while:

.. code-block:: console

    python manage.py load_csv ebird_basic_dataset.csv


My eBird Data
-------------
If you have an eBird account, you can download all your observations. Visit
`Download My Data`_ and download the file to the ``data/downloads`` directory.
The management command to load the data is the same one to load the eBird
Basic Dataset:

.. code-block:: console

    python manage.py load_csv data/downloads/MyEBirdData.csv


eBird API
---------
The API provides access to the checklists submitted to eBird, world-wide.

You will need to `sign up`_ for an access key first, then add it to your
Django settings:

.. code-block:: python

    EBIRD_API_KEY = <your api key>

The first step is to initialize the Species table. You need to do this because
the data from the API identifies the species seen using a simple code, e.g.
'horlar1' (Horned Lark). By downloading the complete taxonomy you initialize
the Species table with the common name, and scientific name, along with subspecies
names and other useful taxonomic information:

.. code-block:: console

    python manage.py load_species

By default, the command will load the English common names for each species.
If you want to load any other language supported by eBird, using the ``--locale``
option:

.. code-block:: console

    python manage.py load_species --locale es

You can also specify the API key on the command line:

.. code-block:: console

    python manage.py load_species --key <your api key>

Now load some checklists:

.. code-block:: console

    python manage.py load_api US-NY-109

This will load checklists for Tompkins county Ney York, USA, where the Cornell
Lab of Ornithology is located. You can use any country code (US), state code (US-NY),
county code (US-NY-109), or hotspot identifier (L97555). The management command also
allows you to pass multiple codes in a single call.

By default, the `load_api` command loads checklists for the past three days. This
is a reasonable trade-off between downloading checklists repeatedly and picking
up edits or late submissions. You can download checklist from further back in time
with the `--days` option:

.. code-block:: console

    python manage.py load_api --days 5 US-NY-109

As with the ``local_species`` command you can pass the API key on the command-line:

.. code-block:: console

    python manage.py load_api --key <your api key> US-NY-109

The API returns a maximum of 200 results for any call. For countries or regions where
there are a lot of birders you may have to schedule downloads multiple times a day.
However it's important to remember that servers and bandwidth cost money. The API is
best used as a local news service. If you want to analyse observations for large areas
then using the eBird Basic Dataset is your best option.

.. _sign up: https://ebird.org/api/keygen
