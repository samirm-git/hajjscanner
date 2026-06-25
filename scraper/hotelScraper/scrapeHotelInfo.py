from bs4 import BeautifulSoup
import copy
import re
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
  # CONTAINER_TAGS = ["div", "section", "article", "td", "tr"]
  out = set()
  for descendant in container.find_all(True):
    out.add(id(descendant))
  
  return out

# def getSiblingImages(container, otherCity):
#   """After `container` resolves to a single city, walk forward siblings
#   (at the same tree level) and collect any <img> tags they contain — even
#   though the siblings themselves don't resolve as city matches (e.g. an
#   image gallery whose alt text never says the city name).

#   Stops as soon as a sibling mentions the OTHER city, since that marks the
#   start of the next hotel's block. A sibling that incidentally also mentions
#   the current city (e.g. a blurb saying "located in Mecca") is NOT a stop
#   condition — it's still part of the current hotel.
#   """
#   images = []
#   seenImgIds = set()

#   for sibling in container.find_next_siblings(True):
#     siblingText = sibling.get_text(separator=" ", strip=True)

#     if checkCityinText(siblingText, otherCity):
#       break

#     for img in sibling.find_all("img"):
#       if id(img) not in seenImgIds:
#         seenImgIds.add(id(img))
#         images.append(img)

#   return images

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
