from scraper.scrapePackageInfo import scrapePackageInfo
from scraper.scrapePackageUrls import scrapePackageUrls
from scraper.db import getAllUrls, getAllProviders
from upload import uploadPackageDataToS3
from scraper.helpers import getProjectRoot
from scraper.regexConsts import HAJJREGEX, UMRAHREGEX
from tqdm import tqdm
import time
import argparse
from dotenv import load_dotenv

root = getProjectRoot()
load_dotenv(dotenv_path= root/'.env.')


def refreshProviderUrls(regex):

  providers = getAllProviders()
  providersPackageUrls = {}
  for companyName, homepage_url in tqdm(providers.items()):
    tqdm.write(f"Now scraping {companyName} URLS...")
    providersPackageUrls[companyName] = scrapePackageUrls(companyName, homepage_url, regex, hajjOrUmrah='hajj')
  return providersPackageUrls


def main(useCache=False, scrapeNewOnly=False, uploadToS3=False):
  start = time.time()
  
  if useCache == False:
    tqdm.write("Scrapping package urls for all providers...")
    providerPackageUrls = refreshProviderUrls(HAJJREGEX)
    tqdm.write("=================================")

  else:
    providerPackageUrls = getAllUrls('hajj', scrapeNewOnly)


  tqdm.write("Scrapping package info for all providers...")
  for companyName, urls in tqdm(providerPackageUrls.items()):
    tqdm.write(f"Now scrapping {companyName}...")
    for url in tqdm(urls):
      packageInfo = scrapePackageInfo(url, companyName)
      if packageInfo and uploadToS3:
        uploadPackageDataToS3(packageInfo, companyName)
     
  
  print(f"time taken: {time.time() - start}")
  
  return None  

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="scraper pipeline script")
  parser.add_argument("--overridelinkscache", action='store_true')
  parser.add_argument("--uploadtoS3", action="store_true")
  parser.add_argument("--scrapenewonly", action="store_true")
  args = parser.parse_args()

  
  main(useCache= not args.overridelinkscache, scrapeNewOnly=args.scrapenewonly, uploadToS3=args.uploadtoS3)