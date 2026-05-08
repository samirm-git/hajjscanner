import sys, json, os
from dotenv import load_dotenv
from scraper.helpers import makeRequest, getSoup, removeFooterHeaderNav, getProjectRoot
from scraper.validator import validateData
from scraper.regexConsts import HAJJREGEX, UMRAHREGEX
from scraper.scrapers import runScrapers, updateScrapedInfo
from scraper.hotelScraper.hotelInfoScraper import scrapeHotelInfo 
from scraper.db import saveUrls, flagUrlIsCatalogue, setScrapped
from tqdm import tqdm
from upload import uploadPackageDataToS3
from urllib.parse import urljoin

root = getProjectRoot()
load_dotenv(dotenv_path= root/'.env.')

def tempSave(packageInfo):
  url = packageInfo['url']
  fname = url[8:-1].replace("/","").replace("\\","")
  print(f"Temp save: {fname}")
  path = getProjectRoot() / 'scraperOutputs' / f"{fname}.txt"
  with open(path,'a') as f:
    f.write("=====================================")
    json.dump(packageInfo, f, indent=4)
    f.write('\n')

def logInvalidJson(error, url):
  path = getProjectRoot() / 'invalidJsonLog.txt'
  with open(path, 'a') as f:
    f.write("\n")    
    f.write(url)
    f.write(" : ")
    f.write(error)

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


def scrapePackageInfo(url, companyName, tempSaveFlag = False):
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

  newScrapedInfo = runScrapers(soup, 'package info')
  # print(f"NEW scraped PackageInfo: {newScrapedInfo} ")
  packageInfo = updateScrapedInfo(oldScrapedInfo=packageInfo, newScrapedInfo=newScrapedInfo)
  # print("")
  # print(f"updated package info: {packageInfo}")

  packageInfo['makkahHotel'] = scrapeHotelInfo(soup, 'makkah', url)
  packageInfo['madinahHotel'] = scrapeHotelInfo(soup, 'madinah', url)    
  if tempSaveFlag:
    tempSave(packageInfo)

  error = validateData(packageInfo)
  if error:
    logInvalidJson(error, url)
    tqdm.write("JSON validation error. See logs.")
    return None
  else:   
    setScrapped(url)
    return packageInfo

if __name__ == "__main__":
  temp = "https://www.safamarwahtravel.co.uk/deals/3-star-21-days-shifting-hajj-package-from-glasgow/"
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
  

  urls = [temp2, url, url2, url3, url4, url5, url6, alhaqnew, eliteumrah, hajjUmrahHub]
  if len(sys.argv) >= 2:
    userChosenUrl = int(sys.argv[1])
  else:
    userChosenUrl = 2


  print(urls[userChosenUrl]) 
  packageInfo = scrapePackageInfo(urls[userChosenUrl], 'safamarwahtravel', tempSaveFlag=True) 
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
