import re
from hijridate import Gregorian
from pageScraper.schema.fields import UmrahField, BaseField
from pageScraper.packageScraper.packageRegexConsts import ISLAMIC_MONTH_PATTERNS

gregorianMonths = ["January", "February", "March", "April", "May", "June","July", "August", "September", "October", "November", "December"]
CONST_DAY = 5

def normalizeIslamicMonth(monthName):
  """Maps any spelling variant of an Islamic month name (e.g. from the hijridate
  library or scraped page text) to the schema's canonical name."""
  for canonicalName, pattern in ISLAMIC_MONTH_PATTERNS.items():
    if re.fullmatch(pattern, monthName, re.IGNORECASE):
      return canonicalName
  return None

def convertToIslamicMonth(year, month):
  """Picks a fixed day (5th) of the given Gregorian month/year and converts
  it to Hijri to read off the corresponding Islamic month. THIS IS NOT AN EXACT PROCESS"""
  monthIndex = gregorianMonths.index(month) + 1
  hijriMonthName = Gregorian(year, monthIndex, CONST_DAY).to_hijri().month_name('en')
  return normalizeIslamicMonth(hijriMonthName)


def _convertToGregorianMonth(year, islamicMonth):
  """Scans the 12 Gregorian months of the given year,
  picks a fixed day 5 of each, converts to Hijri, and returns the Gregorian month"""
  for monthIndex in range(1, 13):
    hijriMonthName = Gregorian(year, monthIndex, CONST_DAY).to_hijri().month_name('en')
    if normalizeIslamicMonth(hijriMonthName) == islamicMonth:
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
 
  output = {BaseField.YEAR: year, UmrahField.SEASON: season, UmrahField.MONTH: month, UmrahField.ISLAMIC_MONTH: islamicMonth}
  return output