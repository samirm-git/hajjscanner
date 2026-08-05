from .packageScraper import Hajj_FieldScraper, Umrah_FieldScraper
from . import hotelScraper
from .schema.fields import BaseField
from .validator import validateData
from .logger import getCategoryLogger
from tqdm import tqdm
from .uploadS3 import uploadPackageDataToS3
from HajjUmrahEnum import HajjOrUmrahEnum
import argparse 
from urllib.parse import urljoin

inaccessibleLogger = getCategoryLogger("inaccessible_urls")
invalidJsonLogger = getCategoryLogger("invalid_json")

def scrapePage(company, url, soup, hajjOrUmrah: HajjOrUmrahEnum):

  scraper = Hajj_FieldScraper if hajjOrUmrah == HajjOrUmrahEnum.HAJJ else Umrah_FieldScraper

  packageInfo = {
        BaseField.URL: url,
        BaseField.COMPANY: company,
        **scraper.run(soup),
        BaseField.MAKKAH_HOTEL: hotelScraper.scrapeHotelInfo(soup, city='makkah', url=url),
        BaseField.MADINAH_HOTEL: hotelScraper.scrapeHotelInfo(soup, city='madinah', url=url),
    }
 
  error = validateData(packageInfo, hajjOrUmrah)
  if error:
    invalidJsonLogger.error(f"[{company}] {url}: {error}")
    return None  
  else:
    return packageInfo

if __name__ == "__main__":
  from utils import makeRequest, getSoup
  from bs4 import BeautifulSoup
  # url = "https://aqdastravel.co.uk/package/21-days-non-shifting-hajj-package/"
  url = "https://eliteumrah.co.uk/14-days-economy-hajj-package/"
  resp, err = makeRequest(url)
  if err is not None:
    print(err)
  soup = BeautifulSoup(resp.text, features="lxml")

  # print(soup.get_text(separator='\n', strip=True))

  soup2 = getSoup(url)
  print(soup2.get_text(separator='\n', strip=True))
  # scrapePage("aqdastravel", url, soup, HajjOrUmrahEnum.HAJJ)