eBird Checklists
================
eBird Checklists is a reusable Django app for loading data from eBird into a database.

Overview
--------
.. overview-start

Observations submitted to eBird are available from three sources:

1. The `eBird Basic Dataset`_
2. Records from `Download My Data`_ in your eBird account
3. Records downloaded from the `eBird API 2.0`_

This project contains loaders and models to take data from each of these
sources and load it into a database. The models also have custom QuerySets
which implement the most common queries, providing an easy to use API for
accessing the data.

.. _eBird Basic Dataset: https://support.ebird.org/en/support/solutions/articles/48000838205-download-ebird-data#anchorEBD
.. _Download My Data: https://ebird.org/downloadMyData
.. _eBird API 2.0: https://documenter.getpostman.com/view/664302/S1ENwy59

.. overview-end

Install
-------
.. install-start

You can use either `pip`_ or `uv`_ to download the `package`_ from PyPI and
install it into a virtualenv:

.. code-block:: console

    pip install ebird-checklists

or:

.. code-block:: console

    uv add ebird-checklists

Update ``INSTALLED_APPS`` in your Django setting:

.. code-block:: python

    INSTALLED_APPS = [
        ...
        ebird.checklists
    ]

Finally, run the migrations to create the tables:

.. code-block:: python

    python manage.py migrate

Everything is now ready to load data from one of the sources above. The
project documentation has detailed instructions in the ``Loading Data``
section. Please see 'Project Information' below.

.. _pip: https://pip.pypa.io/en/stable/
.. _uv: https://docs.astral.sh/uv/
.. _package: https://pypi.org/project/ebird-checklists/

.. install-end

Demo
----

.. demo-start

If you check out the code from the repository there is a fully functioning
Django site, and a sample data file for the eBird Basic Dataset, that you
can use to see the app in action.

.. code-block:: console

    git clone git@github.com:StuartMacKay/ebird-checklists.git
    cd ebird-checklists

Create the virtual environment:

.. code-block:: console

    uv venv

Activate it:

.. code-block:: console

    source venv/bin/activate

Install the requirements:

.. code-block:: console

    uv sync

Run the database migrations:

.. code-block:: console

    python manage.py migrate

Load the sample data from the eBird Basic Dataset:

.. code-block:: console

    python manage.py load_csv data/downloads/ebird_basic_dataset_sample.csv

Create a user:

.. code-block:: console

    python manage.py createsuperuser

Run the demo:

.. code-block:: console

    python manage.py runserver

Now log into the `Django Admin <http:localhost:8000/admin>` to browse the tables.

.. demo-end

Project Information
-------------------

* Documentation: https://ebird-checklists.readthedocs.io/en/latest/
* Issues: https://github.com/StuartMacKay/ebird-checklists/issues
* Repository: https://github.com/StuartMacKay/ebird-checklists

The app is tested on Python 3.8+, and officially supports Django 4.2, 5.0 and 5.1.

eBird Checklists is released under the terms of the `MIT`_ license.

.. _MIT: https://opensource.org/licenses/MIT
