import re
from consts import HEADING_TAGS, BAD_IMAGE_RE, DISTANCE_RE, TO_METRES
from helpers import isKeywordIncludedRegex


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
      if oldScrapedInfo.get(key, False) == False:
          oldScrapedInfo[key] = newScrapedInfo[key]
      else:
          if isinstance(oldScrapedInfo[key], list):
            if isinstance(newScrapedInfo[key], list):
              oldScrapedInfo[key].extend(newScrapedInfo[key])
            else:
              oldScrapedInfo[key].append(newScrapedInfo[key])
              pass

          elif isinstance(oldScrapedInfo[key], set):
            if isinstance(newScrapedInfo[key], set):
              oldScrapedInfo[key].update(newScrapedInfo[key])
            else:
              oldScrapedInfo[key].add(newScrapedInfo[key])

          else:
            #NON LIST/SET TYPES. NEED TO HANDLE THIS COLISION. MAYBE USE LLM?
            oldScrapedInfo[key] = [["COLLISION", oldScrapedInfo[key], newScrapedInfo[key]]]
  except ValueError:
    print("error")
  
  return oldScrapedInfo


#==============================================
#PACKAGE INFO SCRAPERS
#==============================================
def scrapeTotalDays(soup):
  for tag in soup.find_all(HEADING_TAGS):
    text = tag.get_text(strip = True)
    match = re.search(r"(\d+)[-\s]?(?:night|day)s?", text, re.IGNORECASE)
    if match:
      return int(match.group(1))
  return None

def scrapeCompanyFromUrl(url):
  match = re.search(r'(?:www\.)?([^.]+)\.', url.split('//')[-1])
  return match.group(1) if match else ''

def scrapePPP(soup): 
  priceRegex = re.compile(r"([£$€])\s?(\d+(?:,\d{3})*(?:\.\d{2})?)", re.IGNORECASE)
  #can do re.search(r"...", soup.get_text(strip=True)) for faster searching (not sure how much faster)
  #but then we would not know which container the matching text comes from which may be useful e.g. finding the parent container for more context (although not doing this currently).
  #moreover, with soup.find(...) we can filter the containers we are searching through e.g heading [h1, h2, ..., h6] containers.
  priceContainer = soup.find(string=priceRegex)
  if priceContainer:
    match = priceRegex.match(priceContainer.get_text(strip=True))
    currency = match.group(1)
    #TODO: CONVERT CURRENCY TO STANDARD CURRENCY PRICE TO STANDARD CURRENCY E.G £
    price = match.group(2)
    price = price.replace(",", '').strip()
    return int(price)
  else:
    return None

def scrapeTier(soup):
  tierRegex = re.compile(r"luxury|premium|economy", re.IGNORECASE)
  tierContainer = soup.find(string=tierRegex)
  if tierContainer:
    return tierRegex.search(tierContainer.get_text(strip=True)).group(1)
  else: 
    return None

def scrapeStars(soup):
  starsRegex = re.compile(r'\b([1-5])\s*(?:-?\s*star|stars?)\b', re.IGNORECASE)
  starContainer = soup.find(string=starsRegex)
  if starContainer:
    return int(starsRegex.search(starContainer.get_text(strip=True)).group(1))
  return None

def scrapeIsShifting(soup):
  nonshifting = bool(re.search(r"\bnon[-\s]?shifting\b", soup.get_text(strip=True), re.IGNORECASE))  
  if nonshifting:
    return False
  else:
    return True

def scrapeIsVisaIncluded(soup):
  isVisaIncludedRegex = isKeywordIncludedRegex("visa")
  isVisaIncluded = bool(isVisaIncludedRegex.search(soup.get_text(strip=True)))
  if isVisaIncluded:
    return True
  else:
    visaRegex = re.compile('visa', re.IGNORECASE)
    visaContainer = soup.find(string=visaRegex)
    if not visaContainer:
      return False
    else:
      #REQUIRES FURTHER ANALYSIS. MAYBE PASS THE PARENT DIV TO LLM
      return None

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

def scrapeHotelName(soup):
  pass

def scrapeHotelImages(soup):
  hotelImgs = set()
  imgs = soup.find_all("img") #I think you can add a regex expression as a another parameter to make sure the image src does not include 'placeholder'
  if not len(imgs) > 3:
    return []
  for img in imgs:
    src = (img.get("data-src") or img.get("data-original") or img.get("data-lazy") or img.get("src"))
    if not src:
      continue
    elif bool(BAD_IMAGE_RE.search(src)):
        continue
    else:
       hotelImgs.add(src)
  
  return hotelImgs

def scrapeHasWifi(soup):
  wifiRegex = isKeywordIncludedRegex("wifi")
  return soup.find(string=wifiRegex) is not None 

def scrapeHasAC(soup):
  acRegex = isKeywordIncludedRegex("ac")
  return soup.find(string=acRegex) is not None

def scrapeDistanceToHaram(soup):
  match = DISTANCE_RE.find(soup.get_text(strip=True))
  if match:
    distance = float(match.group("distance"))
    unit = match.group("unit").lower()
    if TO_METRES.get(unit, False) == False:
      print(f"ERROR: unknown unit {unit}. Acceptable units: {TO_METRES.keys()}")
    
    return distance * TO_METRES[unit]
  else:
    return None
  

def scrapeWalkToHaram(soup):
  pass 

HOTEL_SCRAPERS = {
  'name': scrapeHotelName,
  'total_days': scrapeTotalDays,
  'images': scrapeHotelImages
}

  
