from .baseScraper import scrapes, BaseScraper
from scraperModels.utils import regexConsts, consts, iterMatches, hasKeywordPattern
from utils import removeHotelSignifier
from cityEnum import City
from schema import models
from db import hotelQueries
from rapidfuzz import process, fuzz
from urllib.parse import urljoin, urlparse

class HotelScraper(BaseScraper):
  MODEL = models.Hotel

  TOKEN_MATCH_THRESHOLD = 84   # fuzz.ratio floor for a candidate/line token pair to count as matched (Step 1)
  DICE_THRESHOLD = 70          # min best dice score (0-100) for a candidate to be considered a match (Step 3.2)
  AMBIGUITY_MARGIN = 8         # min percentage-point gap over runner-up to accept the top candidate (Step 3.3)


  def __init__(self, soup, url, city: City):
    super().__init__(soup)
    self.url = url
    self.hotelsDict = hotelQueries.getCityHotelNames(city.value)
  
  @scrapes("total_days")
  def scrapeTotalDays(self):
    #CURRENTLY THE SAME AS BasePackageScraper implementation. MAYBE MOVE THIS INTO BaseScraper
    for match in iterMatches(regexConsts.TOTAL_DAYS_REGEX, self.headingsList):
      totalDays = int(match.group(1))        
      if self.isFieldValid("total_days", totalDays):
        return totalDays



  @scrapes("name")
  def scrapeHotelName(self):
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
        if bestIdx is not None and bestScore >= self.TOKEN_MATCH_THRESHOLD:
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

    hotels = { extraCleanedName: fullName for _,fullName, extraCleanedName in self.hotelsDict}
    if not hotels:
      return None

    candidateTokens = {key: key.split() for key in hotels}
    best = {key: (0.0, None) for key in hotels}   # key -> (bestDice, bestLineCleaned)

    for line in self.textList:
      cleaned = removeHotelSignifier(line)
      lineTokens = cleaned.split()
      if not lineTokens:
        continue
      for key, cTokens in candidateTokens.items():
        score = diceScore(cTokens, lineTokens)
        if score > best[key][0]:
          best[key] = (score, cleaned)

    ranked = sorted(best.items(), key=lambda kv: kv[1][0], reverse=True)
    topKey, (topScore, topLine) = ranked[0]
    if len(ranked) > 1:
      runnerUpKey, (runnerUpScore, runnerUpLine) = ranked[1]
    else:
      runnerUpKey, runnerUpScore, runnerUpLine = None, 0.0, None

    if topScore < self.DICE_THRESHOLD:
      result = None
    elif runnerUpKey is not None and runnerUpScore >= self.DICE_THRESHOLD and (topScore - runnerUpScore) < self.AMBIGUITY_MARGIN:
      result = None
    else:
      result = hotels[topKey]

    return result

  @scrapes("images")
  def scrapeHotelImages(self):
    def is_valid_image_url(fullUrl):  
      VALID_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp')

      path = urlparse(fullUrl).path
      return path.lower().endswith(VALID_IMAGE_EXTENSIONS)
    

    hotelImgs = set()
    imgs = self.soup.find_all("img") #I think you can add a regex expression as a another parameter to make sure the image src does not include 'placeholder'

    for img in imgs:
      src = (img.get("data-src") or img.get("data-original") or img.get("data-lazy") or img.get("src"))
      if not src or not isinstance(src, str):
        continue
      elif regexConsts.BAD_IMAGE_RE.search(src):
        continue
      else:
        fullUrl = urljoin(self.url, src)
        if is_valid_image_url(fullUrl):
          hotelImgs.add(fullUrl)

    if len(hotelImgs) > 0: 
      return hotelImgs
    else:
      return None
  
  @scrapes("stars")
  def scrapeStars(self):
    #CURRENTLY THE SAME AS BasePackageScraper implementation. MAYBE MOVE THIS INTO BaseScraper
    for match in iterMatches(regexConsts.STARS_REGEX, self.textList):
      stars = int(match.group(1))
      if self.isFieldValid("stars", stars):
        return stars

    return None
   

  @scrapes("has_wifi")
  def scrapeHasWifi(self):
    wifiPattern =  r"\bwi[-\s]*fi\b"
    result = hasKeywordPattern(wifiPattern, self.textList)
    return False if result is None else result

  @scrapes("has_ac")
  def scrapeHasAC(self):
    acPattern = r"\bac\b"
    airconditionPattern = r"\bair[-\s]*condition\w*\b"
    if hasKeywordPattern(acPattern, self.textList) or hasKeywordPattern(airconditionPattern, self.textList):
      return True
    else:
      return False
    # return soup.find(string=acRegex) is not None

  @scrapes("distance_to_haram")
  def scrapeDistanceToHaram(self):
    for match in iterMatches(regexConsts.DISTANCE_RE, self.textList):
      distance = float(match.group("distance"))
      unit = match.group("unit").lower()
      if unit not in consts.TO_METRES:
        raise ValueError
        print(f"ERROR: unknown unit {unit}. Acceptable units: {TO_METRES.keys()}")
      else: 
        distanceMetres = int(distance * consts.TO_METRES[unit])

      if self.isFieldValid("distance_to_haram", distanceMetres):
        return distanceMetres

    return None
    
  @scrapes("walk_to_haram")
  def scrapeWalkToHaram(self):

    def parse_time(value):
      value = value.lower()
      if value.isdigit():
        return int(value)
      else:
        return consts.WORD_TO_NUM.get(value)

    for match in iterMatches(regexConsts.WALK_TIME_RE, self.textList):
      t1 = match.group("time1") or match.group("time1b")
      t2 = match.group("time2") or match.group("time2b")
      
      t1 = parse_time(t1) if t1 else None
      t2 = parse_time(t2) if t2 else None

      if t2 is not None:
          minutes = t2
      elif t1 is not None:
          minutes = t1
      else:
          continue

      if self.isFieldValid("walk_to_haram", minutes):
        return minutes

    return None


  @scrapes("number_of_beds")
  def scrapeNumberOfBeds(self):
    #TODO COMPELTE LATER
    return None

  @scrapes("other_amenities")
  def scrapeOtherAmenities(self):
    #TODO COMPELTE LATER
    return None


if __name__ == "__main__":
  pass