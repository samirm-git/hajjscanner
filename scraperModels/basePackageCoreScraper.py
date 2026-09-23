import re
from .utils import hasKeywordPattern, iterMatches, regexSearch, regexConsts
from .baseScraper import BaseScraper, scrapes
from schema import models, enums
from hijridate import Hijri
from datetime import date

class BasePackageCoreScraper(BaseScraper):
  MODEL = models.BasePackageCore

  @scrapes("total_days")
  def scrapeTotalDays(self):
    for match in iterMatches(regexConsts.TOTAL_DAYS_REGEX, self.headingsList):
      totalDays = int(match.group(1))        
      if self.isFieldValid("total_days", totalDays):
        return totalDays

    return None

  @scrapes("ppp")
  def scrapePPP(self): 
    FX = {"GBP": 1.0, "USD": 0.75, "EUR": 0.86, "SAR": 0.20}
    SYMBOLS = {
        "£": "GBP", "gbp": "GBP",
        "€": "EUR", "eur": "EUR",
        "us$": "USD", "$": "USD", "usd": "USD",
        "sar": "SAR",
    }
    _s = "|".join(re.escape(k) for k in SYMBOLS)
    _n = r"\d[\d,]*(?:\.\d{1,2})?"
    PRICE_REGEX = re.compile(rf"(?:({_s})\s*({_n})|({_n})\s*({_s}))", re.IGNORECASE)

    for match in iterMatches(PRICE_REGEX, self.textList):

      symbol = (match.group(1) or match.group(4)).lower()
      number = (match.group(2) or match.group(3)).replace(",", "")
      cur = SYMBOLS.get(symbol)

      if not cur or cur not in FX:
        return None      

      gbp = round(float(number) * FX[cur])
      if self.isFieldValid("ppp", gbp):
        return gbp

    return None

    
  @scrapes("year")
  def scrapeYear(self):
    yearRegex = re.compile(r"\b(20\d{2}|14\d{2})\b", re.IGNORECASE)
    for match in iterMatches(yearRegex, self.textList): 
      year = int(match.group(1))
      if year >= 1400 and year < 1500:
        try:
          year = Hijri(year, 1, 1).to_gregorian().year
        except Exception:
          continue

      if self.isFieldValid("year", year):
        return year

    return None

  @scrapes("tier")
  def scrapeTier(self):
    tierRegex = re.compile(r"\b(?:(?P<LUXURY>luxury)|(?P<PREMIUM>premium)|(?P<ECONOMY>economy))\b", re.IGNORECASE)
    match = regexSearch(tierRegex, self.textList)
    if match:
      return enums.Tier[match.lastgroup]

    return None

  @scrapes("stars")
  def scrapeStars(self):
    for match in iterMatches(regexConsts.STARS_REGEX, self.textList):
      stars = int(match.group(1))
      if self.isFieldValid("stars", stars):
        return stars

    return None

  @scrapes("departure_city")
  def scrapeDepartureCity(self):
    for match in iterMatches(regexConsts.DEPARTURE_CITY_RE, self.textList):
      city = match.lastgroup
      if self.isFieldValid("departure_city", city):
        return city

    return None

  @scrapes("is_visa_included")
  def scrapeIsVisaIncluded(self):
    visaPattern = r"\bvisas?\b"
    result = hasKeywordPattern(visaPattern, self.textList)
    return False if result is None else result
