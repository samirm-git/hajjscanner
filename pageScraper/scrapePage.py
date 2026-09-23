from __future__ import annotations
from scraperModels import HajjPackageCoreScraper, UmrahPackageCoreScraper
from .scrapeHotelInfo import scrapeHotelInfo
from schema import models
from cityEnum import City
from .logger import getCategoryLogger
from tqdm import tqdm
from .uploadS3 import uploadPackageDataToS3
from hajjUmrahEnum import HajjOrUmrahEnum
import argparse 
from urllib.parse import urljoin
from utils import getProjectRoot

inaccessibleLogger = getCategoryLogger("inaccessible_urls")
invalidJsonLogger = getCategoryLogger("invalid_json")

# def _tempSave(hajjOrUmrah, packageInfo):
#   url = packageInfo['url']
#   fname = url[8:-1].replace("/","").replace("\\","")
#   print(f"Temp save: {fname}")

#   path = getProjectRoot() / 'scraperOutputs' / hajjOrUmrah / f"{fname}.txt"
#   path.parent.mkdir(parents=True, exist_ok=True)
#   with open(path,'a') as f:
#     f.write("=====================================\n")
#     json.dump(packageInfo, f, indent=4)
#     f.write('\n')


def scrapePage(company, url, soup, hajjOrUmrah: HajjOrUmrahEnum):

  if hajjOrUmrah == HajjOrUmrahEnum.HAJJ:
    package_model = models.HajjPackage
    package_core_scraper = HajjPackageCoreScraper(soup)
  else:
    package_model = models.UmrahPackage
    package_core_scraper = UmrahPackageCoreScraper(soup)

  package_core = package_core_scraper.run()
  makkah_hotel = scrapeHotelInfo(soup=soup, url=url, city=City.MAKKAH)
  madinah_hotel = scrapeHotelInfo(soup=soup, url=url, city=City.MADINAH)

  result = package_model(url=url, company=company, package_core=package_core, makkah_hotel=makkah_hotel, madinah_hotel=madinah_hotel)  

  return result


if __name__ == "__main__":
  from utils import getSoup
  from bs4 import BeautifulSoup
  url = "https://eliteumrah.co.uk/14-days-economy-hajj-package/"
  url1 = "https://alamanahtravel.co.uk/14-days-5-star-non-shifting-hajj-package/"
  url2 = "https://www.safamarwahtravel.co.uk/deals/5-star-17-days-non-shifting-hajj-package/"
  url3 = "https://www.alhaqtravel.co.uk/book/24-days-shifting-hajj-packages/"
  url4 = "https://duatravels.co.uk/package/shifting-luxury-hajj-package/"
  url5 = "https://traveltoharam.co.uk/package/14-days-5-star-shifting-hajj-package/"
  url6 = "https://www.alkhairtravel.co.uk/offer/21-days-shifting-hajj-package/"
  alhaqnew = "https://www.alhaqtravel.co.uk/book/19-days-economy-hajj-packages/"
  eliteumrah = "https://eliteumrah.co.uk/21-days-economy-hajj-package/"
  hajjUmrahHub = "https://www.hajjumrahhub.co.uk/hajj/2-3-weeks-hajj-package-non-shifting.html"

  umrah1 = "https://www.safamarwahtravel.co.uk/deals/4-star-14-nights-muharram-umrah-package-from-birmingham/"
  umrah2 = "https://www.safamarwahtravel.co.uk/deals/3-star-7-nights-january-umrah-package-from-glasgow/"
  pppoutlier = "https://www.safamarwahtravel.co.uk/deals/5-star-14-nights-february-umrah-package-with-doha-holidays/"
  

  hajjUrls = [url, url1, url2, url3, url4, url5, url6, alhaqnew, eliteumrah, hajjUmrahHub]
  umrahUrls = [umrah1, umrah2, pppoutlier]

  soup2 = getSoup(umrah2)

  output = scrapePage("safamarwahtravel", umrah2, soup2, HajjOrUmrahEnum.UMRAH)
  print("OUTPUT")
  print("==============================")
  print(output.model_dump_json(indent=4))
  # scrapePage("aqdastravel", url, soup, HajjOrUmrahEnum.HAJJ)



  
  # parser = argparse.ArgumentParser(description='scrapePackageInfo script')
  # parser.add_argument("hajjOrUmrah", choices=['hajj', 'umrah'], help='choose whether to scan for hajj packages or umrah pacakges')
  # parser.add_argument("index", type=int, default=0)
  # args = parser.parse_args()

  # l = hajjUrls if args.hajjOrUmrah == 'hajj' else umrahUrls
  # if len(l) -1 < args.index:
  #   print(f"index out of range for {args.hajjOrUmrah} list: {l}")
  # else:

    # print(l[args.index]) 
    # packageInfo = scrapePackageInfo(args.hajjOrUmrah, l[args.index], 'safamarwahtravel', tempSaveFlag=True) 
    # if packageInfo:
    #   pass
    # else:
    #   print("no package info. Possible JSON validation error")



  #==========================================
  # tempScraper(visible_text)
  #==========================================


  # print(soup.prettify())
  # package_div = soup.find("div", class_="detail_package")
  # price = package_div.find("strong").getText()