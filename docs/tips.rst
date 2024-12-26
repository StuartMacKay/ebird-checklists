====
Tips
====

1. Don't mix data from different sources in the database. You can, but it's not
   a good idea. The reason is that the sources differ in quality.

   Checklists from the eBird API identify the observer by name. That means
   if there are two David Sibley's in your area they will be treated as one
   person.

   Checklists from the eBird API have not been reviewed. As a result some
   observations will be incorrect. Annoyingly, or amusingly, this is often
   the case with rare birds that are mis-identified. There can be confusion
   over two similar species which occur in different continents. Western
   Swamphen (found in Europe) and Purple Gallinule (found the Americas, and
   a mega-rarity in Europe) is a good example.

   Checklists are often updated after they have been submitted. Some observers
   only submit their checklists periodically. Unless you are re-downloading data
   from the API regularly you won't pick up all the changes. It's best to treat
   data from the eBird API as news and accept that there will occasionally be
   errors and omissions.

   The eBird Basic Dataset will give the best results, though it is only published
   on the 15th of each month.

2. When using the eBird API, be nice and don't overload the servers by downloading
   all the checklists for large countries, or where there are a lot of birders.
   Servers and bandwidth cost money. The API key belongs to your eBird account, and
   abusing the service will likely get you banned. Instead limit downloads to your
   local area and get in touch with the eBird team if you want to scale up. Again,
   for large volumes of records, the eBird Basic Dataset is the better option.
