from bs4 import BeautifulSoup
import copy
import re
from scraper.consts import CONTAINER_TAGS
from scraper.regexConsts import CITY_PATTERNS
from scraper.hotelScraper.hotelFieldScraper import HotelFieldScraper

def _mergeContainers(containers):
  """Combine multiple non-overlapping soup containers into a single soup without modifying the original soup."""
  merged = BeautifulSoup("<div></div>", "html.parser")
  wrapper = merged.div

  for container in containers:
    wrapper.append(copy.copy(container))  # copies the tag tree instead of moving it

  return merged


def checkCityinText(text, city):
  if re.search(CITY_PATTERNS[city], text, re.IGNORECASE):
    return True
  else:
    return False


def getChildContainerIDs(container):
  out = set()
  for descendant in container.find_all(CONTAINER_TAGS):
    out.add(id(descendant))
  
  return out

def findCityContainers(soup, city):
  """Walk the soup once and collect all containers that mention `city`
  but not the other city."""
  city = city.lower()
  assert city in {'makkah', 'madinah'}, f"{city} should be either 'makkah' or 'madinah'"

  otherCity = 'madinah' if city == 'makkah' else 'makkah'
  
  matchedContainers = []
  seen = set()

  for container in soup.find_all(True):
    if id(container) in seen:
      continue

    fullText = container.get_text(separator=" ", strip=True)

    if not checkCityinText(fullText, city):
      seen.update(getChildContainerIDs(container))
    elif checkCityinText(fullText, otherCity):
      pass
    else:
      seen.update(getChildContainerIDs(container))
      matchedContainers.append(container)

  return matchedContainers


def scrapeHotelInfo(soup, city, url):
  matchedContainers = findCityContainers(soup, city)
  if not matchedContainers:
      return None

  mergedSoup = _mergeContainers(matchedContainers)
  hotelInfo = HotelFieldScraper.run(mergedSoup, city, url)  

  if hotelInfo == {}:
    return None
  
  for key in hotelInfo.keys():
    if isinstance(hotelInfo[key], set):
      hotelInfo[key] = list(hotelInfo[key])
  
  return hotelInfo
