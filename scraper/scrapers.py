import re
from scraper.consts import HEADING_TAGS 
from scraper.hotelScraper.hotelNamesScraper import HOTELS
from scraper.regexHelpers import hasKeywordPattern, regexSearch
from scraper.helpers import cleanText
from scraper.regexConsts import HOTEL_KEYWORDS, DISTANCE_RE, TO_METRES, WALK_TIME_RE, WORD_TO_NUM, BAD_IMAGE_RE 
from urllib.parse import urljoin, urlparse
from rapidfuzz import process, fuzz, utils

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
      if key == 'images':
        print("images key found in updateScrapedInfo.")
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

        elif type(oldScrapedInfo[key]) is not type(oldScrapedInfo[key]):
          print(f"type mismatch: old value: {oldScrapedInfo[key]} is type: {type(oldScrapedInfo[key])}, while new value: {newScrapedInfo[key]} is type: {type(newScrapedInfo[key])}")

        
        elif oldScrapedInfo[key] is True or newScrapedInfo[key] is True:
          oldScrapedInfo[key] = True 
        
        elif isinstance(oldScrapedInfo[key], str):
          oldScrapedInfo[key] = newScrapedInfo[key]
        
        elif isinstance(oldScrapedInfo[key], list):
          oldScrapedInfo[key].extend(newScrapedInfo[key])  

        elif key == "ppp":
          oldScrapedInfo[key] = max(oldScrapedInfo[key], newScrapedInfo[key])
        else:
          oldScrapedInfo[key] = min(oldScrapedInfo[key], newScrapedInfo[key])

          
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

# def scrapeCompanyFromUrl(url):
#   match = re.search(r'(?:www\.)?([^.]+)\.', url.split('//')[-1])
#   return match.group(1) if match else ''

def scrapePPP(soup): 
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
    if gbp >= 2000 and gbp <= 25_000:
      return gbp
    else:
      return None

def scrapeYear(soup):
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
  match = regexSearch(starsRegex, soup)
  if match:
    return int(match.group(1))
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
    'year': scrapeYear,
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
  # daysRegex = re.compile(r"(\d+)[-\s]?(?:night|day)s?", re.IGNORECASE)
  daysRegex = re.compile(r"\b([1-9]|1[0-9]|20)[-\s]?(?:day|night)s?\b", re.IGNORECASE)
  match = regexSearch(daysRegex, soup)
  if match:
    return int(match.group(1))
  else:
    return None

def scrapeHotelName(soup, city):
  def extract_hotel_candidates(soup) -> set[str]:
    candidates = set()

    for text in soup.stripped_strings:
      words = text.split()
      match_idx = next((i for i, w in enumerate(words) if HOTEL_KEYWORDS.search(w)), None)
      if match_idx is not None:
        if len(words) <= 5:
            candidate = " ".join(words)
        else:
            start = max(0, match_idx - 2)
            end = start + 5
            if end > len(words):
                end = len(words)
                start = end - 5
            candidate = " ".join(words[start:end])
        
        candidates.add(candidate) 

    return candidates


  def match_hotel(candidates: list[str], hotels: list[str]):
      threshold = 75
      best_match = None
      best_score = 0

      for candidate in candidates:
          cleanedText = cleanText(candidate)
          cleanedText = candidate if cleanedText == "" else cleanedText
          # print(f"cleanedText: {cleanedText}")
          result = process.extractOne(
              cleanedText,
              hotels,
              scorer=fuzz.token_set_ratio,  # handles word reordering.
                                              #162 null hotel names when using token_set_ratio
                                              #220 null hotel names when using token_sort_ratio
              processor=utils.default_process
          )
          if result and result[1] >= threshold and result[1] > best_score:
              best_score = result[1]
              best_match = {"matched_name": result[0], "score": result[1], "from_cleanedtext": cleanedText}

      return best_match

  candidates = extract_hotel_candidates(soup)
  # print(f"candidates: {candidates}")
  hotelsDict = HOTELS[city]
  shortNames = list(hotelsDict.keys())
  best_match = match_hotel(candidates, shortNames)
  # print(f"best_match: {best_match}")
  # print("")
  if best_match is not None:
    return hotelsDict[best_match["matched_name"]]
  else:
   return None

def scrapeHotelImages(soup, url):
  def is_valid_image_url(fullUrl):  
    VALID_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp')

    path = urlparse(fullUrl).path
    return path.lower().endswith(VALID_IMAGE_EXTENSIONS)
  

  hotelImgs = set()
  imgs = soup.find_all("img") #I think you can add a regex expression as a another parameter to make sure the image src does not include 'placeholder'
  if not len(imgs) > 3:
    return None
  for img in imgs:
    src = (img.get("data-src") or img.get("data-original") or img.get("data-lazy") or img.get("src"))
    if not src or not isinstance(src, str):
      continue
    elif BAD_IMAGE_RE.search(src):
      continue
    else:
      fullUrl = urljoin(url, src)
      if is_valid_image_url(fullUrl):
        hotelImgs.add(fullUrl)

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
    else: 
      distanceMetres = int(distance * TO_METRES[unit])

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
  # 'images': scrapeHotelImages,
  'stars': scrapeStars,
  'hasWifi': scrapeHasWifi,
  'hasAC': scrapeHasAC,
  'distanceToHaram': scrapeDistanceToHaram,
  'walkToHaram': scrapeWalkToHaram,
  'numberOfBeds': scrapeNumberOfBeds
}