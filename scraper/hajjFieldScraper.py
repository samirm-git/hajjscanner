import re
from scraper.baseFieldScraper import BaseFieldScraper
from scraper.helpers import getProjectRoot
from scraper.regexHelpers import regexSearch

class Hajj_FieldScraper(BaseFieldScraper):
  SCHEMA_PATH = getProjectRoot() / "schema" / "hajjPackage.json"

  @staticmethod
  def scrapeIsShifting(soup):
    nonshiftingRegex = re.compile(r"\bnon[-\s]?shifting\b", re.IGNORECASE)
    match = regexSearch(nonshiftingRegex, soup)  
    if match:
      return False
    else:
      return True
  
  @classmethod
  def get_scrapers(cls):
    return {**super().get_scrapers(), 'isShifting': cls.scrapeIsShifting}