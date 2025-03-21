===============
Database Schema
===============
ebird-checklists loads the data into five Django model: Checklist, Location,
Observer, Observation and Species:

.. image:: models.png

The lightning tour in 15 seconds:

* A Checklist has a Location.
* A Checklist has an Observer.
* An Observation has a Species.
* An Observation has a Checklist.
* A Location has a Country.
* A Location has a Region (eBird's subnational1).
* A Location has a District (eBird's subnational2).
* A Location has a Area (so Locations can be grouped).

Performance optimisations to make queries faster, and statistics easier:

* A Checklist has a Country, Region, District, and Area.
* An Observation has a Country, Region, District, Area, and Location.
* An Observation has an Observer.
* An Observation has a date.

Notes
-----
1. Area is not supported by eBird. However it's immensely useful for grouping
   nearby locations together, particularly in isolated locations like islands,
   since eBird's subnational1 and subnational2 codes are based on administrative
   boundaries.

2. Using tables for locations, rather than adding the country, subnational1 and
   subnational2 codes to Checklist and Observation means the database filters
   on integer primary keys, rather than matching strings.

3. The models use TextField as it works equally well with SQLite3 and PostgreSQL
   as CharField. This means there will not be a problem if the size of strings
   from eBird get longer.

4. The Observer is the person who submitted the checklist to eBird. If the checklist
   was shared or other people in the group also submitted a checklist then the `group`
   attribute on `Checklist` will contain an identifier which can be used to link
   them together.

5. Each models has a JSONField for adding features without having to extend the
   models. Some examples:

   * On the Species model you can store a table of translations for the species
     common name

     .. code-block:: json

        {
           "en": "Gray Plover",
           "en-UK": "Grey Plover",
           "en-US": "Black-bellied Plover",
           "es": "Chorlito gris",
           "es-MX": "Chorlo Gris",
           "es-CL": "Chorlo ártico",
        }

   * Often the eBird site names have extra information added to help identify
     identify all the sites in a given area, and also indicate any access
     restrictions. For example:

     .. code-block:: console

        RN Estuário do Tejo--Ponta da Erva (acesso condicionado).

     You can add a display name value to the JSONField to show a shortened
     version instead of the "official" name:

     .. code-block:: json

        {
          "display-name": "Ponta da Erva"
        }

     The task pf processing the name is left as an exercise for the reader.

6. The is_identified() method on Species is used to count the number of species
   seen by an Observer or seen in an area or Location. It is mirrored as a flag
   on Observation to speed up the queries that perform the counts.

   IMPORTANT: If you look through the code for the Django Admin you will see
   that when the Country, Region, District or Area is changed for a Location,
   or the Location is changed, then the foreign keys on Checklist and Observation
   are updated also. A species status changes regularly (eBird release taxonomic
   updates around once a year), but the identified attribute on Observation is
   not updated as it represents the status of the species at the time the
   observation was made.
