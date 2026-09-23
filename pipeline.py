import urlScraper
import pageScraper
from db import providerQueries, packageUrlQueries
from hajjUmrahEnum import HajjOrUmrahEnum
from utils import getProjectRoot, getSoup
from tqdm import tqdm
import time
import argparse
from dotenv import load_dotenv

root = getProjectRoot()
load_dotenv(dotenv_path= root/'.env.')


def refreshProviderUrls(hajjOrUmrah: HajjOrUmrahEnum):

  providers = providerQueries.getAllProviders()
  providersPackageUrls = {}
  for companyName, homepage_url in tqdm(providers.items()):
    tqdm.write(f"Now scraping {companyName} URLS...")
    providersPackageUrls[companyName] = urlScraper.scrape(homepage_url, hajjOrUmrah.regex)
    packageUrlQueries.saveUrls(provider=companyName, urls=providersPackageUrls[companyName], type=hajjOrUmrah.value)


  return providersPackageUrls


def main(hajjOrUmrah: HajjOrUmrahEnum, useCache=False, scrapeNewOnly=False, uploadToS3=False):
  start = time.time()

  if useCache == False:
    tqdm.write(f"Scrapping {hajjOrUmrah.label} package urls for all providers...")
    providerPackageUrls = refreshProviderUrls(hajjOrUmrah)
    tqdm.write("=================================")

  else:
    providerPackageUrls = packageUrlQueries.getAllUrls(hajjOrUmrah.value, scrapeNewOnly)

  tqdm.write(f"{sum(len(u) for u in providerPackageUrls.values())} urls")
  tqdm.write(f"Scrapping {hajjOrUmrah.label} package info from all urls")
  for companyName, urls in tqdm(providerPackageUrls.items()):
    tqdm.write(f"Now scrapping {companyName}...")
    for url in tqdm(urls):
      soup = getSoup(url)
      if soup is None:
        tqdm.write(f"None soup for url: {url}")
        continue
      if pageScraper.isCataloguePage(url, soup, companyName=companyName):
        continue

      packageInfo = pageScraper.scrape(company=companyName, url=url, soup=soup, hajjOrUmrah=hajjOrUmrah) 
      # packageInfo = scrapePackageInfo(hajjOrUmrah, url, companyName)
      if packageInfo:
        packageUrlQueries.setScrapped(url)
        if uploadToS3:
          pageScraper.uploadPackageDataToS3(hajjOrUmrah, packageInfo, companyName)
     
  print(f"time taken: {time.time() - start}")
  
  return None  

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="scraper pipeline script")
  parser.add_argument("hajjOrUmrah", choices=['hajj', 'umrah'], help='choose whether to scan for hajj packages or umrah pacakges')
  parser.add_argument("--overridelinkscache", action='store_true')
  parser.add_argument("--uploadtoS3", action="store_true")
  parser.add_argument("--scrapenewonly", action="store_true")
  args = parser.parse_args()

  hajjOrUmrah = HajjOrUmrahEnum.HAJJ if args.hajjOrUmrah == 'hajj' else HajjOrUmrahEnum.UMRAH

  
  main(hajjOrUmrah, useCache= not args.overridelinkscache, scrapeNewOnly=args.scrapenewonly, uploadToS3=args.uploadtoS3)