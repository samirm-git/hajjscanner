import re
from .baseScraper import scrapes
from .basePackageCoreScraper import BasePackageCoreScraper
from .utils import regexConsts, hasKeywordPattern, regexSearch 
from schema import models, enums

class UmrahPackageCoreScraper(BasePackageCoreScraper):
  MODEL = models.UmrahPackageCore

  @scrapes("is_ziyarat_included")
  def scrapeIsZiyaratIncluded(self):
    ziyaratPattern = r"\bziy?ara[th]s?\b"
    result = hasKeywordPattern(ziyaratPattern, self.textList)
    return False if result is None else result

  @scrapes("season")
  def scrapeSeason(self):
    seasonRegex = re.compile(
      r"\b(?:(?P<WINTER>winter)|(?P<SPRING>spring)|(?P<SUMMER>summer)|(?P<AUTUMN>autumn|fall))\b",
      re.IGNORECASE
    )
    match = regexSearch(seasonRegex, self.textList)
    if not match:
      return None

    return enums.Season[match.lastgroup]

  @scrapes("month")
  def scrapeMonth(self):
    monthRegex_withoutMay = re.compile(
      r"\b(?:(?P<JANUARY>january)|(?P<FEBRUARY>february)|(?P<MARCH>march)|(?P<APRIL>april)|"
      r"(?P<JUNE>june)|(?P<JULY>july)|(?P<AUGUST>august)|(?P<SEPTEMBER>september)|"
      r"(?P<OCTOBER>october)|(?P<NOVEMBER>november)|(?P<DECEMBER>december))\b",
      re.IGNORECASE
    )
    match = regexSearch(monthRegex_withoutMay, self.textList)
    if match:
      return enums.Month[match.lastgroup]
    
    match = regexSearch(re.compile(r"\b(?P<MAY>May)\b"), self.textList)
    #NOTE: separating May with captilisation required may not be enough
    #e.g. 'PRICES MAY VARY' this would match the month as May
    if match:
      return enums.Month[match.lastgroup]

    return None

  @scrapes("islamic_month")
  def scrapeIslamicMonth(self):
    match = regexSearch(regexConsts.ISLAMIC_MONTH_RE, self.textList)
    if not match:
      return None
    else:
      return enums.IslamicMonth[match.lastgroup]
