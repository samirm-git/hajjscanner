import re
import json
from .baseFieldScraper import BaseFieldScraper
from utils import getProjectRoot
from pageScraper.packageScraper.packageRegexConsts import AZIZIYAH_RE
from pageScraper.regexHelpers import hasKeywordPattern, regexSearch
from pageScraper.schema.fields import HajjField

class Hajj_FieldScraper(BaseFieldScraper):
  SCHEMA = json.loads((getProjectRoot() / "pageScraper" /  "schema" / "hajjPackage.json").read_text())

  @staticmethod
  def scrapeIsShifting(textList):
    shiftingPattern = r"\bshifting\b"
    result = hasKeywordPattern(shiftingPattern, textList)
    if result is not None:
      return result
    else:
      return regexSearch(AZIZIYAH_RE, textList) is not None

    # nonshiftingRegex = re.compile(r"\bnon[-\s]?shifting\b", re.IGNORECASE)
    # match = regexSearch(nonshiftingRegex, textList)  
    # print(f"isShifting match: {match}")
    # if match:
    #   return False
    # else:
    #   return True
  
  @classmethod
  def get_scrapers(cls):
    return {**super().get_scrapers(), HajjField.IS_SHIFTING: cls.scrapeIsShifting}