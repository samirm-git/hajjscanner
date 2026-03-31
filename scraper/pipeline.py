from scraper.scrapePackageInfo import scrapePackageInfo
from scraper.scrapePackageUrls import scrapePackageUrls
from upload import uploadPackageDataToS3
from scraper.helpers import getProjectRoot
from scraper.regexConsts import HAJJREGEX, UMRAHREGEX
from tqdm import tqdm
import time
from dotenv import load_dotenv

root = getProjectRoot()
load_dotenv(dotenv_path= root/'.env.')



def createPackageUrlsMasterDict(providerList, regex):
  providersPackageUrls = {}
  for provider in tqdm(providerList):
    tqdm.write(f"{provider}")
    providersPackageUrls[provider] = scrapePackageUrls(provider, regex)
  return providersPackageUrls


##TODO: FIX LLM CALL TO ATLEAST ALWAYS PROVIDE NULL ON THE REQUIRED PROPERTIES
##TODO: HANDLE RELATIVE ULRS RETURNED BY THE scrapeLinksFromCataloguePage()
def main():
  start = time.time()
  path = getProjectRoot() / 'providers.txt'
  with open(path,'r') as f:
    providerList = f.read().splitlines()

  tqdm.write("Scrapping package urls for all providers...")
  providerPackageUrls = createPackageUrlsMasterDict(providerList, HAJJREGEX)

  tqdm.write("=================================")
  tqdm.write("Scrapping package info for all providers...")
  for provider, urls in providerPackageUrls.items():
    tqdm.write(provider)
    for url in tqdm(urls):
      packageInfo = scrapePackageInfo(url)
      if packageInfo:
        uploadPackageDataToS3(packageInfo, packageInfo["url"])

  
  print(f"time taken: {time.time() - start}")

  return None  

if __name__ == "__main__":
  main()