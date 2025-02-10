# scraper/base_scraper.py

from abc import ABC, abstractmethod
from typing import List, Dict

class BaseScraper(ABC):
    """
    Abstract base class for scraping websites.
    Each concrete scraper will parse HTML and return
    a standardized list of pricing records.
    """

    @abstractmethod
    def scrape(self) -> List[Dict]:
        """
        Scrapes data from a website and returns a list of dictionaries,
        each containing all relevant mooring rates info.
        Example fields:
        {
          "port_name": "Benalmadena",
          "boat_length_min": 0,
          "boat_length_max": 6,
          "price_low_season": 50.0,
          "price_high_season": 70.0,
          "electricity_included": False,
          "water_included": False,
          "iva_included": False,
          "valid_for_year": 2024,
          "timestamp": "...",
          ...
        }
        """
        pass
