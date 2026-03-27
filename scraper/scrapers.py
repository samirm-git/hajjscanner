import re
from scraper.consts import HEADING_TAGS 
from scraper.hotelScraper.hotelNamesScraper import HOTEL_NAMES_RE
from scraper.regexHelpers import hasKeywordPattern, regexSearch
from scraper.regexConsts import DISTANCE_RE, TO_METRES, WALK_TIME_RE, WORD_TO_NUM, BAD_IMAGE_RE 

#MAIN FUNCTION
def runScrapers(soup, scraperName):
  scrapedInfo = {}
  
  assert scraperName.lower() in {'package info', 'hotel info'}, f"{scraperName.lower()} should be either 'package info' or 'hotel info'."
  scrapers = PACKAGEINFO_SCRAPERS if scraperName.lower() == 'package info' else HOTEL_SCRAPERS
  for key in scrapers.keys():
      scrapedInfo[key] = scrapers[key](soup)

  return scrapedInfo

def updateScrapedInfo(oldScrapedInfo, newScrapedInfo):
  try:
    for key in newScrapedInfo.keys(): 
      if key not in oldScrapedInfo:
          oldScrapedInfo[key] = newScrapedInfo[key]
      else:
          if isinstance(oldScrapedInfo[key], set):
            oldScrapedInfo[key] = list(oldScrapedInfo[key])
          
          if isinstance(newScrapedInfo[key], set):
            newScrapedInfo[key] = list(newScrapedInfo[key])

          if newScrapedInfo[key] == oldScrapedInfo[key] or newScrapedInfo[key] is None:
            pass

          elif oldScrapedInfo[key] is None:
            oldScrapedInfo[key] = newScrapedInfo[key]
          
          elif oldScrapedInfo[key] == True or newScrapedInfo[key] == True:
            oldScrapedInfo[key] = True 

          elif isinstance(oldScrapedInfo[key], list):
            oldScrapedInfo[key].append(newScrapedInfo[key])
          
          else:
            oldScrapedInfo[key] = ["COLLISION", oldScrapedInfo[key], newScrapedInfo[key]]

  except ValueError:
    print("error")
  
  return oldScrapedInfo

#==============================================
#PACKAGE INFO SCRAPERS
#==============================================
def scrapeTotalDays(soup):
  totalDays = -1
  for tag in soup.find_all(HEADING_TAGS):
    daysRegex = re.compile(r"\b(\d{1,2})[-\s]?(?:night|day)s?\b",re.IGNORECASE)
    match = regexSearch(daysRegex, tag)
    if match:
      totalDays = int(match.group(1))
      break
  
  if totalDays >= 10 and totalDays <= 30:
    return totalDays
  else:
    return None

def scrapeCompanyFromUrl(url):
  match = re.search(r'(?:www\.)?([^.]+)\.', url.split('//')[-1])
  return match.group(1) if match else ''

def scrapePPP(soup): 
  #can do re.search(r"...", soup.get_text(strip=True)) for faster searching (not sure how much faster)
  #but then we would not know which container the matching text comes from which may be useful e.g. finding the parent container for more context (although not doing this currently).
  #moreover, with soup.find(...) we can filter the containers we are searching through e.g heading [h1, h2, ..., h6] containers.
  priceRegex = re.compile(r"([£$€])\s*(\d[\d,]*(?:\.\d{2})?)", re.IGNORECASE)
  price = -1 
  match = regexSearch(priceRegex, soup)
  if match:
    currency = match.group(1)
    #TODO: CONVERT CURRENCY TO STANDARD CURRENCY PRICE TO STANDARD CURRENCY E.G £
    price = match.group(2)
    price = int(price.replace(",", '').strip())
  
  if price >= 2000 and price <= 25000:
    return price
  else:
    return None

def scrapeTier(soup):
  tierRegex = re.compile(r"\b(luxury|premium|economy)\b", re.IGNORECASE)
  match = regexSearch(tierRegex, soup)
  if match:
    return match.group(1)
  else: 
    return None

def scrapeStars(soup):
  starsRegex = re.compile(r'\b([1-5])\s*(?:-?\s*star|stars?)\b', re.IGNORECASE)
  stars = -1
  match = regexSearch(starsRegex, soup)
  if match:
    stars = int(match.group(1))
  
  if stars >= 1 and stars <= 5:
    return stars
  else:
    return None

def scrapeIsShifting(soup):
  nonshiftingRegex = re.compile(r"\bnon[-\s]?shifting\b", re.IGNORECASE)
  match = regexSearch(nonshiftingRegex, soup)  
  if match:
    return False
  else:
    return True

def scrapeIsVisaIncluded(soup):
  visaPattern = r"\bvisas?\b"
  return hasKeywordPattern(visaPattern, soup)


PACKAGEINFO_SCRAPERS = {
    'ppp': scrapePPP,
    'total_days': scrapeTotalDays,
    # 'tier': scrapeTier,
    'stars': scrapeStars,
    'isShifting': scrapeIsShifting,
    'isVisaIncluded': scrapeIsVisaIncluded
  }


#==============================================
#HOTEL SCRAPERS
#==============================================

def scrapeTotalDaysHotel(soup):
  totalDays = -1
  daysRegex = re.compile(r"(\d+)[-\s]?(?:night|day)s?", re.IGNORECASE)
  match = regexSearch(daysRegex, soup)
  if match:
    totalDays = int(match.group(1))
  
  if totalDays >= 1 and totalDays <= 20:
    return totalDays
  else:
   return None

def scrapeHotelName(soup, city):
  match = regexSearch(HOTEL_NAMES_RE[city], soup)
  if match:
    return match.group(0)
  
  return None

def scrapeHotelImages(soup):
  hotelImgs = set()
  imgs = soup.find_all("img") #I think you can add a regex expression as a another parameter to make sure the image src does not include 'placeholder'
  if not len(imgs) > 3:
    return None
  for img in imgs:
    src = (img.get("data-src") or img.get("data-original") or img.get("data-lazy") or img.get("src"))
    if not src:
      continue
    elif bool(BAD_IMAGE_RE.search(src)):
        continue
    else:
       hotelImgs.add(src)

  if len(hotelImgs) > 0: 
    return hotelImgs
  else:
    return None

def scrapeHasWifi(soup):
  wifiPattern =  r"\bwi[-\s]*fi\b"
  return hasKeywordPattern(wifiPattern, soup)
  # return soup.find(string=wifiRegex) is not None 

def scrapeHasAC(soup):
  acPattern = r"\bac\b"
  airconditionPattern = r"\bair[-\s]*condition\w*\b"
  if hasKeywordPattern(acPattern, soup) or hasKeywordPattern(airconditionPattern, soup):
    return True
  else:
    return False
  # return soup.find(string=acRegex) is not None

def scrapeDistanceToHaram(soup):
  match = regexSearch(DISTANCE_RE, soup)
  distanceMetres = -1
  if match:
    distance = float(match.group("distance"))
    unit = match.group("unit").lower()
    if unit not in TO_METRES:
      print(f"ERROR: unknown unit {unit}. Acceptable units: {TO_METRES.keys()}")
    
    distanceMetres = distance * TO_METRES[unit]

  if distanceMetres >= 500 and distanceMetres <= 4000:
    return distanceMetres
  else:
    return None
  

def scrapeWalkToHaram(soup):

  def parse_time(value):
    value = value.lower()
    if value.isdigit():
      return int(value)
    else:
      return WORD_TO_NUM.get(value)

  minutes = -1 
  match = regexSearch(WALK_TIME_RE, soup)
  if match:
    t1 = match.group("time1") or match.group("time1b")
    t2 = match.group("time2") or match.group("time2b")
    
    t1 = parse_time(t1) if t1 else None
    t2 = parse_time(t2) if t2 else None

    if t2 is not None:
        minutes = t2
    elif t1 is not None:
        minutes = t1

  if minutes >=2 and minutes <= 40:
    return minutes
  else: 
    return None

def scrapeNumberOfBeds(soup):
  #complete later
  return None


HOTEL_SCRAPERS = {
  #name is scrapped separately in hotelInfoScraper.py
  'total_days': scrapeTotalDaysHotel,
  'images': scrapeHotelImages,
  'stars': scrapeStars,
  'hasWifi': scrapeHasWifi,
  'hasAC': scrapeHasAC,
  'distanceToHaram': scrapeDistanceToHaram,
  'walkToHaram': scrapeWalkToHaram,
  'numberOfBeds': scrapeNumberOfBeds
}