import logging
from collections import Counter

logger = logging.getLogger(__name__)
_typeMismatchCounts = Counter()
_mergeErrorCounts = Counter()

#MAIN FUNCTION
def runScrapers(soup, scraperName):
  scraperName = scraperName.lower()
  assert scraperName in {'hajj', 'umrah', 'hotel'}, f"{scraperName} should be either 'hajj', 'umrah', or 'hotel' "
  
  if scraperName == 'hajj':
    scrapers = HAJJPACKAGE_SCRAPERS
  elif scraperName == 'umrah':
    scrapers = UMRAHPACKAGE_SCRAPERS
  else:
    scrapers = HOTEL_SCRAPERS

  scrapedInfo = {}
  for key in scrapers.keys():
      scrapedInfo[key] = scrapers[key](soup)

  return scrapedInfo

def updateScrapedInfo(oldScrapedInfo, newScrapedInfo):
  for key in newScrapedInfo.keys(): 
    try:
      if key not in oldScrapedInfo:
          oldScrapedInfo[key] = newScrapedInfo[key]
      else:
        oldVal = oldScrapedInfo[key]
        newVal = newScrapedInfo[key]

        if newVal == oldVal or newVal is None:
          pass

        elif oldVal is None:
          oldScrapedInfo[key] = newVal

        elif type(oldVal) is not type(newVal):
          _typeMismatchCounts[key] += 1
          logger.debug("Type mismatch for key=%s: old=%r (%s), new=%r (%s)", key, oldVal, type(oldVal), newVal, type(newVal))
        
        elif oldVal is True or newVal is True:
          oldScrapedInfo[key] = True 
        
        elif isinstance(oldVal, list):
          #THIS IS NOT USED IN CURRENT SCHEMA (16/06/2026), BUT KEEPING IT HERE FOR FUTURE PROOF
          oldScrapedInfo[key] = list(dict.fromkeys(oldVal + newVal))
        
        elif isinstance(oldVal, set):
          oldScrapedInfo[key] = oldVal.union(newVal)

        elif key == "ppp":
          oldScrapedInfo[key] = max(oldVal, newVal)
        
        else:
          oldScrapedInfo[key] = newVal
            
    except Exception:
      _mergeErrorCounts[key] += 1
      logger.exception("Failed merging key=%s (old=%r, new=%r)", key, oldScrapedInfo.get(key), newScrapedInfo.get(key))
  
  return oldScrapedInfo

def logScrapeMergeSummary(reset: bool = True):
  """Call once after a full pipeline run (all webpages scraped)."""
  if _typeMismatchCounts:
    for key, count in _typeMismatchCounts.most_common():
      logger.warning("Type mismatch occurred %d times for key=%s", count, key)
  if _mergeErrorCounts:
    for key, count in _mergeErrorCounts.most_common():
      logger.warning("Merge error occurred %d times for key=%s", count, key)

  if reset:
    _typeMismatchCounts.clear()
    _mergeErrorCounts.clear()
