from .baseScraper import scrapes
from .basePackageCoreScraper import BasePackageCoreScraper
from schema import models
from .utils import regexConsts, hasKeywordPattern, regexSearch
 
class HajjPackageCoreScraper(BasePackageCoreScraper):
  MODEL = models.HajjPackageCore

  @scrapes("is_shifting")
  def scrapeIsShifting(self):
    shiftingPattern = r"\bshifting\b"
    result = hasKeywordPattern(shiftingPattern, self.textList)
    if result is not None:
      return result
    else:
      return regexSearch(regexConsts.AZIZIYAH_RE, self.textList) is not None

    # nonshiftingRegex = re.compile(r"\bnon[-\s]?shifting\b", re.IGNORECASE)
    # match = regexSearch(nonshiftingRegex, pageText.textList)  
    # print(f"isShifting match: {match}")
    # if match:
    #   return False
    # else:
    #   return True
  