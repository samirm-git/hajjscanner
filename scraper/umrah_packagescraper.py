import re
from scraper.packagescraper import PackageScraper
from scraper.regexHelpers import hasKeywordPattern, regexSearch
from scraper.regexConsts import ISLAMIC_MONTH_PATTERNS, ISLAMIC_MONTH_REGEX
from scraper.helpers import getProjectRoot
from scraper.fillMissingDateFields import fillMissingDateFields

class Umrah_PackageScraper(PackageScraper):
  SCHEMA_PATH = getProjectRoot() / "schema" / "umrahPackage.json"

  @classmethod
  def get_scrapers(cls):
    return {**super().get_scrapers(), 'isZiyaratIncluded': cls.scrapeIsZiyaratIncluded, 'season': cls.scrapeSeason,
            'month': cls.scrapeMonth, 'islamicMonth': cls.scrapeIslamicMonth}
  
  @classmethod
  def run(cls, soup, url=None, company=None):
    scrapedInfo = super().run(soup, url, company)
    inferedDateFields = fillMissingDateFields(scrapedInfo.get('year'), scrapedInfo.get('season'), scrapedInfo.get('month'), scrapedInfo.get('islamicMonth'))
    scrapedInfo.update(inferedDateFields)
    return scrapedInfo 

  @staticmethod
  def scrapeIsZiyaratIncluded(soup):
    ziyaratPattern = r"\bziy?ara[th]s?\b"
    return hasKeywordPattern(ziyaratPattern, soup)

  @staticmethod
  def scrapeSeason(soup):
    seasonRegex = re.compile(r"\b(winter|spring|summer|autumn|fall)\b", re.IGNORECASE)
    match = regexSearch(seasonRegex, soup)
    if not match:
      return None

    season = match.group(1).lower()
    if season == "fall":
      season = "autumn"

    return season.capitalize()

  @staticmethod
  def scrapeMonth(soup):
    monthRegex_withoutMay = re.compile(r"\b(january|february|march|april|june|july|august|september|october|november|december)\b", re.IGNORECASE)
    match = regexSearch(monthRegex_withoutMay, soup)
    if match:
      return match.group(1).capitalize()
    else:
      match = regexSearch(re.compile(r"\bMay\b"), soup) #NOTE: separating May with captilisation required may not be enough
                                                                #e.g. 'PRICES MAY VARY' this would match the month as May  
      if match:
        return "May"
      else:
        return None

  @staticmethod
  def scrapeIslamicMonth(soup):
    match = regexSearch(ISLAMIC_MONTH_REGEX, soup)
    if not match:
      return None

    matchedText = match.group(1)
    for canonicalName, pattern in ISLAMIC_MONTH_PATTERNS.items():
      if re.fullmatch(pattern, matchedText, re.IGNORECASE):
        return canonicalName

    return None