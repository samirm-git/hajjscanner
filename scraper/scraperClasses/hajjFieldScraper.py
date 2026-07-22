import re
import json
from scraper.scraperClasses.baseFieldScraper import BaseFieldScraper
from scraper.helpers import getProjectRoot
from scraper.regexHelpers import regexSearch
from schema.fields import HajjField

class Hajj_FieldScraper(BaseFieldScraper):
  SCHEMA = json.loads((getProjectRoot() / "schema" / "hajjPackage.json").read_text())

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
    return {**super().get_scrapers(), HajjField.IS_SHIFTING: cls.scrapeIsShifting}