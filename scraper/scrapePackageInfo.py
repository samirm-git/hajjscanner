import sys, json, os
from dotenv import load_dotenv
from scraper.helpers import makeRequest, getSoup, removeFooterHeaderNav, getProjectRoot
from scraper.validator import validateData
from scraper.regexConsts import HAJJREGEX, UMRAHREGEX
from scraper.scrapers import runScrapers, updateScrapedInfo
from scraper.dateFieldScrapers import fillMissingDateFields
from scraper.hotelScraper.hotelInfoScraper import scrapeHotelInfo 
from scraper.db import saveUrls, flagUrlIsCatalogue, setScrapped
from tqdm import tqdm
from upload import uploadPackageDataToS3

import argparse 
from urllib.parse import urljoin

root = getProjectRoot()
load_dotenv(dotenv_path= root/'.env.')

def tempSave(hajjOrUmrah, packageInfo):
  url = packageInfo['url']
  fname = url[8:-1].replace("/","").replace("\\","")
  print(f"Temp save: {fname}")

  path = getProjectRoot() / 'scraperOutputs' / hajjOrUmrah / f"{fname}.txt"
  path.parent.mkdir(parents=True, exist_ok=True)
  with open(path,'a') as f:
    f.write("=====================================\n")
    json.dump(packageInfo, f, indent=4)
    f.write('\n')

def logInvalidJson(error, url):
  path = getProjectRoot() / 'invalidJsonLog.txt'
  path.parent.mkdir(parents=True, exist_ok=True)

  with open(path, 'a') as f:
    f.write("\n")    
    f.write(url)
    f.write(" : ")
    f.write(str(error))

def isCataloguePage(url, soup, companyName, save=True):
  hajjPackageLinks, umrahPackageLinks = set(), set()

  for link in soup.find_all("a", href=True):
    href = link.get("href")
    if HAJJREGEX.search(href):
      hajjPackageLinks.add(urljoin(url, href))

    elif UMRAHREGEX.search(href):
      umrahPackageLinks.add(urljoin(url,href))
  
  if save:
    saveUrls(provider=companyName, urls=hajjPackageLinks, type='hajj')
    saveUrls(provider=companyName, urls=umrahPackageLinks, type='umrah')

  if len(hajjPackageLinks) + len(umrahPackageLinks) <= 5:
    return False
  else:
    flagUrlIsCatalogue(url)
    return True

def scrapePackageInfo(hajjOrUmrah, url, companyName, tempSaveFlag = False):
  packageInfo = {'url':url, 'company': companyName}

  resp, err = makeRequest(url)
  if err:
    tqdm.write(f"{url}: {err}")
    return None 
  if resp is None:  # 404
    tqdm.write(f"{url} is not valid")
    return None

  soup = getSoup(resp.text, parser="lxml")

  soup = removeFooterHeaderNav(soup)
  if soup.find("main"):
    soup = soup.find("main")
  
  if isCataloguePage(url, soup, companyName, save=True):
    return None

  scrapedInfo = runScrapers(soup, hajjOrUmrah)
  packageInfo = updateScrapedInfo(oldScrapedInfo=packageInfo, newScrapedInfo=scrapedInfo)

  if hajjOrUmrah == 'umrah':
    inferedDataFields = fillMissingDateFields(year=packageInfo.get('year'), season=packageInfo.get('season'), month=packageInfo.get('month'), islamicMonth=packageInfo.get('islamicMonth'))
    packageInfo = updateScrapedInfo(oldScrapedInfo=packageInfo, newScrapedInfo=inferedDataFields)
  

  packageInfo['makkahHotel'] = scrapeHotelInfo(soup, 'makkah', url)
  packageInfo['madinahHotel'] = scrapeHotelInfo(soup, 'madinah', url)    

  packageInfo = {key: list(value) if isinstance(value, set) else value for key,value in packageInfo.items()}
  if tempSaveFlag:
    tempSave(hajjOrUmrah, packageInfo)

  error = validateData(packageInfo, hajjOrUmrah)
  if error:
    logInvalidJson(error, url)
    tqdm.write("JSON validation error. See logs.")
    return None
  else:   
    setScrapped(url)
    return packageInfo

if __name__ == "__main__":
  temp2 = "https://www.safamarwahtravel.co.uk/deals/3-star-17-days-shifting-hajj-package-from-glasgow/"
  url = "https://alamanahtravel.co.uk/14-days-5-star-non-shifting-hajj-package/"
  url2 = "https://www.safamarwahtravel.co.uk/deals/5-star-17-days-non-shifting-hajj-package/"
  url3 = "https://www.alhaqtravel.co.uk/book/24-days-shifting-hajj-packages/"
  url4 = "https://duatravels.co.uk/package/shifting-luxury-hajj-package/"
  url5 = "https://traveltoharam.co.uk/package/14-days-5-star-shifting-hajj-package/"
  url6 = "https://www.alkhairtravel.co.uk/offer/21-days-shifting-hajj-package/"
  alhaqnew = "https://www.alhaqtravel.co.uk/book/19-days-economy-hajj-packages/"
  eliteumrah = "https://eliteumrah.co.uk/21-days-economy-hajj-package/"
  hajjUmrahHub = "https://www.hajjumrahhub.co.uk/hajj/2-3-weeks-hajj-package-non-shifting.html"

  umrah1 = "https://www.safamarwahtravel.co.uk/deals/4-star-14-nights-muharram-umrah-package-from-birmingham/"
  

  hajjUrls = [temp2, url, url2, url3, url4, url5, url6, alhaqnew, eliteumrah, hajjUmrahHub]
  umrahUrls = [umrah1]
  
  parser = argparse.ArgumentParser(description='scrapePackageInfo script')
  parser.add_argument("hajjOrUmrah", choices=['hajj', 'umrah'], help='choose whether to scan for hajj packages or umrah pacakges')
  parser.add_argument("index", type=int, default=0)
  args = parser.parse_args()

  l = hajjUrls if args.hajjOrUmrah == 'hajj' else umrahUrls
  if len(l) -1 < args.index:
    print(f"index out of range for {args.hajjOrUmrah} list: {l}")
  else:

    print(l[args.index]) 
    packageInfo = scrapePackageInfo(args.hajjOrUmrah, l[args.index], 'safamarwahtravel', tempSaveFlag=True) 
    if packageInfo:
      pass
    else:
      print("no package info. Possible JSON validation error")



  #==========================================
  # tempScraper(visible_text)
  #==========================================


  # print(soup.prettify())
  # package_div = soup.find("div", class_="detail_package")
  # price = package_div.find("strong").getText()
