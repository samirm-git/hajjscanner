import re
from scraper.regexHelpers import regexSearch
from scraper.regexConsts import ISLAMIC_MONTH_PATTERNS, ISLAMIC_MONTH_REGEX
from hijridate import Hijri, Gregorian
from datetime import date

def scrapeYear(soup):
  yearRegex = re.compile(r"\b(20\d{2}|14\d{2})\b", re.IGNORECASE)
  match = regexSearch(yearRegex, soup)
  if not match:
    return None
  
  min_year = 2020
  max_year = date.today().year + 1
  year = int(match.group(1))

  if year >= 1400 and year < 1500:
    try:
       year = Hijri(year, 1, 1).to_gregorian().year
    except Exception:
      return None
  
  if year >= min_year and year <= max_year:
    return year
  else:
    return None 


def scrapeSeason(soup):
  seasonRegex = re.compile(r"\b(winter|spring|summer|autumn|fall)\b", re.IGNORECASE)
  match = regexSearch(seasonRegex, soup)
  if not match:
    return None

  season = match.group(1).lower()
  if season == "fall":
    season = "autumn"

  return season.capitalize()

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

def scrapeIslamicMonth(soup):
  match = regexSearch(ISLAMIC_MONTH_REGEX, soup)
  if not match:
    return None

  matchedText = match.group(1)
  for canonicalName, pattern in ISLAMIC_MONTH_PATTERNS.items():
    if re.fullmatch(pattern, matchedText, re.IGNORECASE):
      return canonicalName

  return None

gregorianMonths = ["January", "February", "March", "April", "May", "June","July", "August", "September", "October", "November", "December"] 
CONST_DAY = 5
def convertToIslamicMonth(year, month):
  """Picks a fixed day (5th) of the given Gregorian month/year and converts
  it to Hijri to read off the corresponding Islamic month. THIS IS NOT AN EXACT PROCESS"""
  monthIndex = gregorianMonths.index(month) + 1
  return Gregorian(year, monthIndex, CONST_DAY).to_hijri().month_name('en')
 
 
def _convertToGregorianMonth(year, islamicMonth):
  """Scans the 12 Gregorian months of the given year,
  picks a fixed day 5 of each, converts to Hijri, and returns the Gregorian month"""
  for monthIndex in range(1, 13):
    hijriMonthName = Gregorian(year, monthIndex, CONST_DAY).to_hijri().month_name('en')
    if hijriMonthName == islamicMonth:
      return gregorianMonths[monthIndex - 1]
  return None
 
 
def fillMissingDateFields(year, season, month, islamicMonth):
  # month <-> islamicMonth deduction needs a year to anchor the conversion,
  # since the same islamicMonth/month pairing shifts every Gregorian year.
  MONTH_TO_SEASON = {"December": "Winter", "January": "Winter", "February": "Winter",
                    "March": "Spring", "April": "Spring", "May": "Spring",
                    "June": "Summer", "July": "Summer", "August": "Summer",
                    "September": "Autumn", "October": "Autumn", "November": "Autumn"}
  if year is not None:
    if month is not None and islamicMonth is None:
      islamicMonth = convertToIslamicMonth(year, month)
 
    elif islamicMonth is not None and month is None:
      month = _convertToGregorianMonth(year, islamicMonth)
 
  # season <-> month is a fixed, certain mapping, no year needed
  if month is not None and season is None:
    season = MONTH_TO_SEASON.get(month)
 
  return [year, season, month, islamicMonth]