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


def refreshProviderUrls(hajjOrUmrah):
  assert hajjOrUmrah in {'hajj', 'umrah'}, f"{hajjOrUmrah} should be either 'hajj' or 'umrah'"

  regex = HAJJREGEX if hajjOrUmrah == 'hajj' else UMRAHREGEX

  providers = getAllProviders()
  providersPackageUrls = {}
  for companyName, homepage_url in tqdm(providers.items()):
    tqdm.write(f"Now scraping {companyName} URLS...")
    providersPackageUrls[companyName] = scrapePackageUrls(companyName, homepage_url, regex, hajjOrUmrah)

  return providersPackageUrls


def main(hajjOrUmrah, useCache=False, scrapeNewOnly=False, uploadToS3=False):
  start = time.time()
  assert hajjOrUmrah in {'hajj', 'umrah'}, f"{hajjOrUmrah} should be either 'hajj' or 'umrah'"

  if useCache == False:
    tqdm.write(f"Scrapping {hajjOrUmrah} package urls for all providers...")
    providerPackageUrls = refreshProviderUrls()
    tqdm.write("=================================")

  else:
    providerPackageUrls = getAllUrls(hajjOrUmrah, scrapeNewOnly)


  tqdm.write(f"Scrapping {hajjOrUmrah} package info from all urls")
  for companyName, urls in tqdm(providerPackageUrls.items()):
    tqdm.write(f"Now scrapping {companyName}...")
    for url in tqdm(urls):
      packageInfo = scrapePackageInfo(hajjOrUmrah, url, companyName)
      if packageInfo and uploadToS3:
        uploadPackageDataToS3(hajjOrUmrah, packageInfo, companyName)
     
  
  print(f"time taken: {time.time() - start}")
  
  return None  

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="scraper pipeline script")
  parser.add_argument("hajjOrUmrah", choices=['hajj', 'umrah'], help='choose whether to scan for hajj packages or umrah pacakges')
  parser.add_argument("--overridelinkscache", action='store_true')
  parser.add_argument("--uploadtoS3", action="store_true")
  parser.add_argument("--scrapenewonly", action="store_true")
  args = parser.parse_args()

  
  main(useCache= not args.overridelinkscache, scrapeNewOnly=args.scrapenewonly, uploadToS3=args.uploadtoS3)