import logging
from urllib.error import HTTPError, URLError

from ebird.api import get_taxonomy

from ..models import Species

logger = logging.getLogger(__name__)


class SpeciesLoader:
    def __init__(self, api_key: str, locale="en"):
        self.api_key: str = api_key
        self.locale: str = locale

    def load(self):
        entries: list

        logger.info("Loading eBird taxonomy", extra={"locale": self.locale})

        try:
            entries = get_taxonomy(self.api_key, locale=self.locale)
        except (HTTPError, URLError):
            logger.exception("eBird taxonomy not loaded")
            raise

        for entry in entries:
            Species.objects.update_or_create(
                species_code=entry["speciesCode"],
                defaults={
                    "taxon_order": int(entry["taxonOrder"]),
                    "order": entry.get("order", ""),
                    "category": entry["category"],
                    "species_code": entry["speciesCode"],
                    "family_code": entry.get("familyCode", ""),
                    "common_name": entry["comName"],
                    "scientific_name": entry["sciName"],
                    "family_common_name": entry.get("familyComName", ""),
                    "family_scientific_name": entry.get("familySciName", ""),
                    "subspecies_common_name": "",
                    "subspecies_scientific_name": "",
                    "exotic_code": "",
                }
            )

        logger.info("Loaded eBird taxonomy", extra={"loaded": len(entries)})
