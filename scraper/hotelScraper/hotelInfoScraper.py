import json
import re
from scraper.helpers import getProjectRoot
from scraper.regexHelpers import regexSearch, hasKeywordPattern
from scraper.regexConsts import TOTAL_DAYS_REGEX, HOTEL_KEYWORDS, DISTANCE_RE, TO_METRES, WALK_TIME_RE, WORD_TO_NUM, BAD_IMAGE_RE 
from scraper.helpers import cleanText
from rapidfuzz import process, fuzz, utils
from scraper.hotelScraper.scrapeHotelNames import HOTELS
from urllib.parse import urljoin, urlparse

class HotelInfoScraper:
  SCHEMA_PATH = getProjectRoot() / "schema" / "hotel.json" 

  @classmethod
  def _load_bounds(cls):
    with open(cls.SCHEMA_PATH) as f:
      schema = json.load(f)
      properties = schema["properties"]
    
    cls.TOTALDAYS_MINMAX = [properties["total_days"]["minimum"], properties["total_days"]["maximum"]]
    cls.DISTANCETOHARAM_MINMAX = [properties["distanceToHaram"]["minimum"], properties["distanceToHaram"]["maximum"]]
    cls.WALKTOHARAM_MINMAX = [properties["walkToHaram"]["minimum"], properties["walkToHaram"]["maximum"]]
    cls.NUMBEROFBEDS_MINMAX = [properties["numberOfBeds"]["minimum"], properties["numberOfBeds"]["maximum"]]
  
  @classmethod 
  def get_scrapers(cls):
    return {'total_days': cls.scrapeTotalDaysHotel, 'name': cls.scrapeHotelName, 'images': cls.scrapeHotelImages,
            'stars': cls.scrapeStars, 'hasWifi': cls.scrapeHasWifi, 'hasAC': cls.scrapeHasAC,
            'distanceToHaram': cls.scrapeDistanceToHaram, 'walkToHaram': cls.scrapeWalkToHaram, 'numberOfBeds': cls.scrapeNumberOfBeds }    
  
  @classmethod
  def run(cls, soup, city, url):
    scrapedInfo = {}
    for field, fn in cls.get_scrapers().items():
      if field == 'name':
        scrapedInfo['name'] = fn(soup, city)
      elif field == 'images':
        scrapedInfo['images'] = fn(soup, url)
      else: 
        scrapedInfo[field] = fn(soup)
    
    return scrapedInfo

  @classmethod
  def scrapeTotalDaysHotel(cls, soup):
    totalDays = -1
    match = regexSearch(TOTAL_DAYS_REGEX, soup)
    if not match:
      return None
    else:
      totalDays = int(match.group(1))
      if totalDays >= cls.TOTALDAYS_MINMAX[0] and totalDays <= cls.TOTALDAYS_MINMAX[1]:
        return totalDays
      else:
        return None
  
  @staticmethod
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

  @staticmethod
  def scrapeHotelImages(soup, url):
    def is_valid_image_url(fullUrl):  
      VALID_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp')

      path = urlparse(fullUrl).path
      return path.lower().endswith(VALID_IMAGE_EXTENSIONS)
    

    hotelImgs = set()
    imgs = soup.find_all("img") #I think you can add a regex expression as a another parameter to make sure the image src does not include 'placeholder'

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
  
  @staticmethod
  def scrapeStars(soup):
    starsRegex = re.compile(r'\b([1-5])\s*(?:-?\s*star|stars?)\b', re.IGNORECASE)
    match = regexSearch(starsRegex, soup)
    if match:
      return int(match.group(1))
    else:
      return None

  @staticmethod
  def scrapeHasWifi(soup):
    wifiPattern =  r"\bwi[-\s]*fi\b"
    return hasKeywordPattern(wifiPattern, soup)
    # return soup.find(string=wifiRegex) is not None 

  @staticmethod
  def scrapeHasAC(soup):
    acPattern = r"\bac\b"
    airconditionPattern = r"\bair[-\s]*condition\w*\b"
    if hasKeywordPattern(acPattern, soup) or hasKeywordPattern(airconditionPattern, soup):
      return True
    else:
      return False
    # return soup.find(string=acRegex) is not None

  @classmethod
  def scrapeDistanceToHaram(cls, soup):
    match = regexSearch(DISTANCE_RE, soup)
    distanceMetres = -1
    if match:
      distance = float(match.group("distance"))
      unit = match.group("unit").lower()
      if unit not in TO_METRES:
        print(f"ERROR: unknown unit {unit}. Acceptable units: {TO_METRES.keys()}")
      else: 
        distanceMetres = int(distance * TO_METRES[unit])

    if distanceMetres >= cls.DISTANCETOHARAM_MINMAX[0] and distanceMetres <= cls.DISTANCETOHARAM_MINMAX[1]:
      return distanceMetres
    else:
      return None
    
  @classmethod
  def scrapeWalkToHaram(cls, soup):

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

    if minutes >= cls.WALKTOHARAM_MINMAX[0] and minutes <= cls.WALKTOHARAM_MINMAX[1]:
      return minutes
    else: 
      return None

  def scrapeNumberOfBeds(soup):
    #complete later
    return None

HotelInfoScraper._load_bounds()