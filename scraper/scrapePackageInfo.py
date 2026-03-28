import sys, json, os
from dotenv import load_dotenv
from scraper.helpers import makeRequest, getSoup, removeFooterHeaderNav, getProjectRoot
from validator import validateData
from upload import uploadPackageDataToS3
from scraper.scrapers import scrapeCompanyFromUrl, runScrapers, updateScrapedInfo
from scraper.hotelScraper.hotelInfoScraper import scrapeHotelInfo 
from tqdm import tqdm

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

def logInvalidJson(error):
  path = getProjectRoot() / 'invalidJsonLog.txt'
  with open(path, 'a') as f:
    f.write("\n")    
    f.write(error)



def scrapePackageInfo(url, tempSave = False):
  packageInfo = {'url':url}

  resp = makeRequest(url)
  soup = getSoup(resp.text, parser="lxml")
  soup = removeFooterHeaderNav(soup)
  if soup.find("main"):
    soup = soup.find("main")

  nLinks = len(soup.find_all("a", href=True))
  if nLinks > 10:
    tqdm.write(f"{nLinks} links. {url} is a possible catalogue page")
    #IF MORE THAN 10 LINKS IT IS LIKELY TO BE A CATALOGUE PAGE NOT A PACKAGE DETAILS PAGE
    #TODO: HANDLE CATALOGUE PAGE TO FIND PACKAGE DETAILS PAGES
    return 

  packageInfo['company'] = scrapeCompanyFromUrl(url)
  newScrapedInfo = runScrapers(soup, 'package info')
  # print(f"NEW scraped PackageInfo: {newScrapedInfo} ")
  packageInfo = updateScrapedInfo(oldScrapedInfo=packageInfo, newScrapedInfo=newScrapedInfo)
  # print("")
  # print(f"updated package info: {packageInfo}")

  packageInfo['makkahHotel'] = scrapeHotelInfo(soup, 'makkah')
  packageInfo['madinahHotel'] = scrapeHotelInfo(soup, 'madinah')    
  if tempSave:
    tempSave(packageInfo)

  error = validateData(packageInfo)
  if error:
    logInvalidJson(error)
    return None
     
  return packageInfo

if __name__ == "__main__":

  
  url = "https://alamanahtravel.co.uk/14-days-5-star-non-shifting-hajj-package/"
  url2 = "https://www.safamarwahtravel.co.uk/deals/5-star-17-days-non-shifting-hajj-package/"
  url3 = "https://www.alhaqtravel.co.uk/book/24-days-shifting-hajj-packages/"
  url4 = "https://duatravels.co.uk/package/shifting-luxury-hajj-package/"
  alhaqnew = "https://www.alhaqtravel.co.uk/book/19-days-economy-hajj-packages/"

  urls = [url, url2, url3, url4, alhaqnew]
  if len(sys.argv) >= 2:
    userChosenUrl = int(sys.argv[1])
  else:
    userChosenUrl = 2


  print(urls[userChosenUrl]) 
  packageInfo = scrapePackageInfo(urls[userChosenUrl], tempSave=True) 
  if packageInfo:
    # uploadPackageDataToS3(packageInfo, packageInfo["url"])
    pass
  else:
    print("company name not found. Likely a package page")



  #==========================================
  # tempScraper(visible_text)
  #==========================================


  # print(soup.prettify())
  # package_div = soup.find("div", class_="detail_package")
  # price = package_div.find("strong").getText()
