import re
import json
from scraper.regexHelpers import hasKeywordPattern, regexSearch
from scraper.regexConsts import DEPARTURE_CITY_RE, TOTAL_DAYS_REGEX 
from hijridate import Hijri
from datetime import date

class BaseFieldScraper:
  SCHEMA_PATH = None
  PPP_MINMAX = [None, None]
  TOTALDAYS_MINMAX = [None, None]
  YEAR_MIN = None

  @classmethod
  def __init_subclass__(cls, **kwargs):
    super().__init_subclass__(**kwargs)
    if cls.SCHEMA_PATH is not None:
        cls._load_bounds()
  
  @classmethod
  def _load_bounds(cls):
    with open(cls.SCHEMA_PATH) as f:
        schema = json.load(f)
        properties = schema["properties"]

    cls.PPP_MINMAX = [properties["ppp"]["minimum"], properties["ppp"]["maximum"]]
    cls.TOTALDAYS_MINMAX = [properties["total_days"]["minimum"], properties["total_days"]["maximum"]]
    cls.YEAR_MIN = properties["year"]["minimum"]
  
  @classmethod
  def get_scrapers(cls):
    scrapers = {'ppp': cls.scrapePPP, 'year':cls.scrapeYear, 'total_days': cls.scrapeTotalDays, 
                'tier': cls.scrapeTier, 'stars': cls.scrapeStars, 'departureCity': cls.scrapeDepartureCity,
                'isVisaIncluded': cls.scrapeIsVisaIncluded}
    return scrapers

  @classmethod
  def run(cls, soup, url=None, company=None):
    scrapedInfo = {'url': url, 'company': company}
    for field, fn in cls.get_scrapers().items():
      scrapedInfo[field] = fn(soup)
    return scrapedInfo

  @classmethod
  def scrapeTotalDays(cls, soup):
    totalDays = -1
    HEADING_TAGS = ["h1", "h2", "h3", "h4", "h5", "h6", "small", "strong"]
    for tag in soup.find_all(HEADING_TAGS):
      match = regexSearch(TOTAL_DAYS_REGEX, tag)
      if match:
        totalDays = int(match.group(1))
        break
    
    if totalDays >= cls.TOTALDAYS_MINMAX[0] and totalDays <= cls.TOTALDAYS_MINMAX[1]:
      return totalDays
    else:
      return None

  @classmethod
  def scrapePPP(cls, soup): 
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

    match = regexSearch(PRICE_REGEX, soup)
    if not match:
      return None
    else:
      symbol = (match.group(1) or match.group(4)).lower()
      number = (match.group(2) or match.group(3)).replace(",", "")
      cur = SYMBOLS.get(symbol)

      if not cur or cur not in FX:
        return None
      
      gbp = round(float(number) * FX[cur])
      if gbp >= cls.PPP_MINMAX[0] and gbp <= cls.PPP_MINMAX[1]:
        return gbp
      else:
        return None
    
  @classmethod
  def scrapeYear(cls, soup):
    yearRegex = re.compile(r"\b(20\d{2}|14\d{2})\b", re.IGNORECASE)
    match = regexSearch(yearRegex, soup)
    if not match:
      return None
    
    max_year = date.today().year + 1
    year = int(match.group(1))

    if year >= 1400 and year < 1500:
      try:
        year = Hijri(year, 1, 1).to_gregorian().year
      except Exception:
        return None
    
    if year >= cls.YEAR_MIN and year <= max_year:
      return year
    else:
      return None 

  @staticmethod
  def scrapeTier(soup):
    tierRegex = re.compile(r"\b(luxury|premium|economy)\b", re.IGNORECASE)
    match = regexSearch(tierRegex, soup)
    if match:
      return match.group(1).lower()
    else: 
      return None

  @staticmethod
  def scrapeStars(soup):
    starsRegex = re.compile(r'\b([1-5])\s*(?:-?\s*star|stars?)\b', re.IGNORECASE)
    match = regexSearch(starsRegex, soup)
    if match:
      return int(match.group(1))
    else:
      return None

  @staticmethod
  def scrapeDepartureCity(soup):
    match = regexSearch(DEPARTURE_CITY_RE, soup)
    if not match:
      return None

    return match.lastgroup 

  @staticmethod
  def scrapeIsVisaIncluded(soup):
    visaPattern = r"\bvisas?\b"
    return hasKeywordPattern(visaPattern, soup)
