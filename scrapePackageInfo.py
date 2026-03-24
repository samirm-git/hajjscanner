import sys, json
from dotenv import load_dotenv
from helpers import makeRequest, getSoup, removeFooterHeaderNav
from hotelScraper import scrapeHotelInfo 
from validator import validateData
from upload import uploadPackageDataToS3
from scrapers import scrapeCompanyFromUrl, runScrapers, updateScrapedInfo

load_dotenv()  

def scrapePackageInfo(url):

  packageInfo = {'url':url}


  resp = makeRequest(url)
  soup = getSoup(resp.text, parser="lxml")
  soup = removeFooterHeaderNav(soup)
  if soup.find("main"):
    soup = soup.find("main")

  nLinks = len(soup.find_all("a", href=True))
  print(nLinks)
  0/0
  if nLinks > 10:
    print(f"{nLinks} links. This is a ossible catalogue page!")
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

  fname = url[8:-1].replace("/","").replace("\\","")
  with open(f'scraperOutputs/{fname}.txt','a') as f:
    f.write("=====================================")
    json.dump(packageInfo, f, indent=4)
    f.write('\n')

  # validateData(packageInfo)
  return packageInfo

if __name__ == "__main__":
  url = "https://alamanahtravel.co.uk/14-days-5-star-non-shifting-hajj-package/"
  url2 = "https://www.safamarwahtravel.co.uk/deals/5-star-17-days-non-shifting-hajj-package/"
  url3 = "https://www.alhaqtravel.co.uk/book/24-days-shifting-hajj-packages/"
  url4 = "https://duatravels.co.uk/package/shifting-luxury-hajj-package/"

  urls = [url, url2, url3, url4]
  if len(sys.argv) >= 2:
    userChosenUrl = int(sys.argv[1])
  else:
    userChosenUrl = 2


  print(urls[userChosenUrl]) 
  # temp2 = json.dumps(temp, indent=4)
  # uploadPackageDataToS3(temp2, 'alhaqtravel') 
  packageInfo = scrapePackageInfo(urls[userChosenUrl]) 
  if packageInfo["company"]:
    uploadPackageDataToS3(packageInfo, packageInfo["company"])
  else:
    print("company name not found. Likely a package page")



  #==========================================
  # tempScraper(visible_text)
  #==========================================


  # print(soup.prettify())
  # package_div = soup.find("div", class_="detail_package")
  # price = package_div.find("strong").getText()
