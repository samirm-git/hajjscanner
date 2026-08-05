import json
import re
from utils import getProjectRoot
from pageScraper.regexHelpers import regexSearch, hasKeywordPattern
from pageScraper.commonRegex import TOTAL_DAYS_REGEX

from .hotelRegexConsts import HOTEL_KEYWORDS_RE, BAD_IMAGE_RE, DISTANCE_RE, WALK_TIME_RE
from .hotelConsts import TO_METRES, WORD_TO_NUM
from .hotelHelpers import cleanText, liteClean
from db import hotelQueries
from rapidfuzz import process, fuzz, utils
from urllib.parse import urljoin, urlparse
from pageScraper.schema.fields import HotelField

class HotelFieldScraper:
  SCHEMA  = json.loads((getProjectRoot() / "pageScraper" / "schema" / "hotel.json").read_text())
  _properties = SCHEMA['properties']

  TOTALDAYS_MINMAX = [_properties[HotelField.TOTAL_DAYS]["minimum"], _properties[HotelField.TOTAL_DAYS]["maximum"]]
  DISTANCETOHARAM_MINMAX = [_properties[HotelField.DISTANCE_TO_HARAM]["minimum"], _properties[HotelField.DISTANCE_TO_HARAM]["maximum"]]
  WALKTOHARAM_MINMAX = [_properties[HotelField.WALK_TO_HARAM]["minimum"], _properties[HotelField.WALK_TO_HARAM]["maximum"]]
  NUMBEROFBEDS_MINMAX = [_properties[HotelField.NUMBER_OF_BEDS]["minimum"], _properties[HotelField.NUMBER_OF_BEDS]["maximum"]]

  TOKEN_MATCH_THRESHOLD = 84   # fuzz.ratio floor for a candidate/line token pair to count as matched (Step 1)
  DICE_THRESHOLD = 70          # min best dice score (0-100) for a candidate to be considered a match (Step 3.2)
  AMBIGUITY_MARGIN = 8         # min percentage-point gap over runner-up to accept the top candidate (Step 3.3)

  HOTELS = {"makkah": hotelQueries.getCityHotelNames('makkah'), "madinah": hotelQueries.getCityHotelNames("madinah")}
  
  @classmethod 
  def get_scrapers(cls):
    return {HotelField.TOTAL_DAYS: cls.scrapeTotalDaysHotel, HotelField.NAME: cls.scrapeHotelNameNEW, HotelField.IMAGES: cls.scrapeHotelImages,
            HotelField.STARS: cls.scrapeStars, HotelField.HAS_WIFI: cls.scrapeHasWifi, HotelField.HAS_AC: cls.scrapeHasAC,
            HotelField.DISTANCE_TO_HARAM: cls.scrapeDistanceToHaram, HotelField.WALK_TO_HARAM: cls.scrapeWalkToHaram, HotelField.NUMBER_OF_BEDS: cls.scrapeNumberOfBeds }    
  
  @classmethod
  def run(cls, soup, city, url):
    scrapedInfo = {}
    textList = list(soup.stripped_strings)
    for field, fn in cls.get_scrapers().items():
      if field == HotelField.NAME:
        scrapedInfo[field] = fn(textList, city)
      elif field == HotelField.IMAGES:
        scrapedInfo[field] = fn(soup, url)
      else: 
        scrapedInfo[field] = fn(textList)
    
    return scrapedInfo

  @classmethod
  def scrapeTotalDaysHotel(cls, textList):
    totalDays = -1
    match = regexSearch(TOTAL_DAYS_REGEX, textList)
    if not match:
      return None
    else:
      totalDays = int(match.group(1))
      if totalDays >= cls.TOTALDAYS_MINMAX[0] and totalDays <= cls.TOTALDAYS_MINMAX[1]:
        return totalDays
      else:
        return None

  @classmethod
  def scrapeHotelNameNEW(cls, textList, city):
    def greedyMatchedTokenCount(candidateTokens, lineTokens):
      # Greedy one-to-one pairing, not a globally-optimal assignment: for each
      # candidate token (in order) take the best-scoring available line token.
      # Acceptable simplification since hotel names here are short (1-4 tokens).
      available = list(lineTokens)
      matched = 0
      for cToken in candidateTokens:
        bestIdx, bestScore = None, -1
        for i, lToken in enumerate(available):
          score = fuzz.ratio(cToken, lToken)  # never partial_ratio: substring search causes false positives
          if score > bestScore:
            bestScore, bestIdx = score, i
        if bestIdx is not None and bestScore >= cls.TOKEN_MATCH_THRESHOLD:
          matched += 1
          del available[bestIdx]
      return matched

    def diceScore(candidateTokens, lineTokens):
      if not candidateTokens or not lineTokens:
        return 0.0
      matched = greedyMatchedTokenCount(candidateTokens, lineTokens)
      if matched == 0:
        return 0.0
      return 100 * 2 * matched / (len(candidateTokens) + len(lineTokens))

    hotels = { extraCleanedName: fullName for _,fullName, extraCleanedName in cls.HOTELS[city]}
    if not hotels:
      return None

    candidateTokens = {key: key.split() for key in hotels}
    best = {key: (0.0, None) for key in hotels}   # key -> (bestDice, bestLineCleaned)

    for line in textList:
      lineCleaned = cleanText(line)
      lineTokens = lineCleaned.split()
      if not lineTokens:
        continue
      for key, cTokens in candidateTokens.items():
        score = diceScore(cTokens, lineTokens)
        if score > best[key][0]:
          best[key] = (score, lineCleaned)

    ranked = sorted(best.items(), key=lambda kv: kv[1][0], reverse=True)
    topKey, (topScore, topLine) = ranked[0]
    if len(ranked) > 1:
      runnerUpKey, (runnerUpScore, runnerUpLine) = ranked[1]
    else:
      runnerUpKey, runnerUpScore, runnerUpLine = None, 0.0, None

    if topScore < cls.DICE_THRESHOLD:
      result = None
    elif runnerUpKey is not None and runnerUpScore >= cls.DICE_THRESHOLD and (topScore - runnerUpScore) < cls.AMBIGUITY_MARGIN:
      result = None
    else:
      result = hotels[topKey]

    return result



  @staticmethod
  def scrapeHotelImages(soup, baseUrl):
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
        fullUrl = urljoin(baseUrl, src)
        if is_valid_image_url(fullUrl):
          hotelImgs.add(fullUrl)

    if len(hotelImgs) > 0: 
      return hotelImgs
    else:
      return None
  
  @staticmethod
  def scrapeStars(textList):
    starsRegex = re.compile(r'\b([1-5])\s*(?:-?\s*star|stars?)\b', re.IGNORECASE)
    match = regexSearch(starsRegex, textList)
    if match:
      return int(match.group(1))
    else:
      return None

  @staticmethod
  def scrapeHasWifi(textList):
    wifiPattern =  r"\bwi[-\s]*fi\b"
    result = hasKeywordPattern(wifiPattern, textList)
    return False if result is None else result

  @staticmethod
  def scrapeHasAC(textList):
    acPattern = r"\bac\b"
    airconditionPattern = r"\bair[-\s]*condition\w*\b"
    if hasKeywordPattern(acPattern, textList) or hasKeywordPattern(airconditionPattern, textList):
      return True
    else:
      return False
    # return soup.find(string=acRegex) is not None

  @classmethod
  def scrapeDistanceToHaram(cls, textList):
    match = regexSearch(DISTANCE_RE, textList)
    distanceMetres = -1
    if match:
      distance = float(match.group("distance"))
      unit = match.group("unit").lower()
      if unit not in TO_METRES:
        raise ValueError
        print(f"ERROR: unknown unit {unit}. Acceptable units: {TO_METRES.keys()}")
      else: 
        distanceMetres = int(distance * TO_METRES[unit])

    if distanceMetres >= cls.DISTANCETOHARAM_MINMAX[0] and distanceMetres <= cls.DISTANCETOHARAM_MINMAX[1]:
      return distanceMetres
    else:
      return None
    
  @classmethod
  def scrapeWalkToHaram(cls, textList):

    def parse_time(value):
      value = value.lower()
      if value.isdigit():
        return int(value)
      else:
        return WORD_TO_NUM.get(value)

    minutes = -1 
    match = regexSearch(WALK_TIME_RE, textList)
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

  def scrapeNumberOfBeds(textList):
    #complete later
    return None

if __name__ == "__main__":
  HotelFieldScraper.scrapeHotelName(['31 May', 'Transfer to Madinah (Dar al Eiman al Haram)', '03 June', 'Madinah Hotel (half board)'],
                                    "madinah")
  