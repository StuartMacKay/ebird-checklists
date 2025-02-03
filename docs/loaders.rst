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

Next, select which locale (language) you want to use for the Species' common
name, and add it to the Django settings:

.. code-block:: python

    EBIRD_LOCALE = <language code>

A complete list of locales is returned by ebird.api.get_taxonomy_locales().

Now load some checklists:

.. code-block:: console

    python manage.py load_api new 7 US-NY-109

This will load checklists added in the past week for Tompkins county Ney York, USA,
where the Cornell Lab of Ornithology is located. You can use any country code (US),
state code (US-NY), county code (US-NY-109), or hotspot identifier (L97555). The
management command also allows you to pass multiple codes in a single call.

The management commands calls get_visits() from the ebird.api, which lists the
visits made on each day. The eBird API limits the number of results to 200. To
workaround this, if the limit is reached then the visits to each sub-region are
fetched. That way you can still download all the checklists submitted. Since
this command only downloads checklists that don't already exist in the database
you can run it frequently and be sure you are getting all the submissions.

You automate running the command using a scheduler such as cron. If you use the
absolute paths to python and the command, then you don't need to deal with activating
the virtual environment, for example:

.. code-block:: console

    # Every 4 hours, load all new checklists, for New York state, submitted for the past week
    0 */4 * * * /home/me/my-project/.venv/bin/python /home/me/my-project/manage.py load_api new 7 US-NY

That way you can be pretty sure you're getting all the observations for a region.

This however, does not download any checklists which have been updated. For that
you can run the following:

.. code-block:: console

    python manage.py load_api all 2025-02-04 US-NY-109

This will download all the checklists submitted for a given date, and add new
checklists, or update all existing ones.

Why the difference arguments? The reason is that only about 1% of submitted
checklists are updated, and because of the limitations of the eBird API, you can
only find out if a checklist has changed by downloading it. So, to pick up all the
changes you have to repeatedly download all the checklists for a given period in
case something changed. That is more or less practical for small windows of time,
for example, the past three days. However, you are still downloading hundreds or
maybe thousands of checklist to pick up the handful which were edited. For larger
windows it becomes really expensive in terms of load on the eBird servers. They
also have to pay for the network connections and bandwidth too. You can't download
everything, all the time, in case something changed. You should really treat the
API as a news service, and accept that there will be gaps in the data. For accuracy
and completeness, sign up to get access to the eBird Basic Dataset.

Using cron, you can schedule running the load_api management command, to pick up
most of the submissions:

.. code-block:: console

    # Every hour, load new checklists submitted today
    0 * * * * /home/me/my-project/.venv/bin/python /home/me/my-project/manage.py load_api new 1 US-NY
    # Every 4 hours, load new checklists submitted today and yesterday
    0 */4 * * * /home/me/my-project/.venv/bin/python /home/me/my-project/manage.py load_api new 2 US-NY
    # Every day at midnight, load new checklists submitted in the past week
    0 0 * * * /home/me/my-project/.venv/bin/python /home/me/my-project/manage.py load_api new 7 US-NY
    # Every Sunday at midnight, load all checklists submitted one month ago
    0 0 * * 0 /home/me/my-project/my-scripts/updates.sh US-NY

The last command calls a shell script, not the load_api management command. The
reason that we need to select a specific date. The unix ``date`` command is
perfect for this:

.. code-block:: console

    #! /usr/bin/env bash
    # updates.sh

    PROJECT=/home/me/my-project/
    PYTHON=${PROJECT}/.venv/bin/python
    DJANGO=${PROJECT}/manage.py
    ONE_WEEK_AGO=`date -d "-1 week" "+%Y-%m-%d"`

    ${PYTHON} ${DJANGO} load_api all ${ONE_WEEK_AGO} $@

This schedule, or something similar, should ensure that the database contains the
majority of the checklists that eBird has.

These examples showed how to do it with Linux. For Windows you will need to write
scripts, and use the Scheduler to run them at a given time.

.. _sign up: https://ebird.org/api/keygen
