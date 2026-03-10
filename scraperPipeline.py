from scrapePackageInfo import scrapePackageInfo
from scrapePackageUrls import scrapePackageUrls
from upload import uploadPackageDataToS3
import re
from tqdm import tqdm
import time


HAJJREGEX = re.compile(r"hajj[-_]?package", re.IGNORECASE) 
UMRAHREGEX = re.compile(r"umrah?[-_]?package", re.IGNORECASE)

##TODO: FIX LLM CALL TO ATLEAST ALWAYS PROVIDE NULL ON THE REQUIRED PROPERTIES
##TODO: HANDLE RELATIVE ULRS RETURNED BY THE scrapeLinksFromCataloguePage()
def main():
  start = time.time()
  with open('providers.txt','r') as f:
    providerList = f.read().splitlines()

  alhaqtravel = providerList[2]
  urls = tqdm(scrapePackageUrls(alhaqtravel, HAJJREGEX))
  for url in tqdm(urls):
    packageInfo = scrapePackageInfo(url)
    uploadPackageDataToS3(packageInfo)
  
  print(f"time taken: {time.time() - start}")

  return None  

if __name__ == "__main__":
  main()