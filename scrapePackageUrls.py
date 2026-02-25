import re, sys
from helpers import makeRequest, getSoup, removeFooterHeaderNav
from pprint import pprint
from scraper import scrapePackage
from upload import uploadPackageDataToS3


def scrapeLinksSitemap(soup):
  hajjPackageUrls = []
  umrahPackageUrls = []
  for urlTag in soup.find_all("url"):
    url = urlTag.find("loc").get_text(strip=True)
    #TODO: IF last-modified IS VERY OLD DON'T USE IT
    if re.search(r"hajj[-_]?package", url, re.IGNORECASE):
      lastModified = urlTag.find("lastmod").get_text(strip=True)
      hajjPackageUrls.append({'url':url, 'last-modified': lastModified})
    elif re.search(r"umrah?[-_]?package", url, re.IGNORECASE):
      lastModified = urlTag.find("lastmod").get_text(strip=True)
      umrahPackageUrls.append({'url': url, 'last-modified': lastModified})
  
  return (hajjPackageUrls, umrahPackageUrls)
    
def scrapeLinksHomePage(soup):
  print("hi")

  return None, None

def filterPackages(packageList):
  packageAllUrls = {'package':[], 'catalogue':[]}
  for package in packageList:
    resp = makeRequest(package['url'])
    soup = getSoup(resp.text, 'lxml')
    soup = removeFooterHeaderNav(soup)
    numberOfLinks = len(soup.find_all("a", href=True))
    if numberOfLinks > 10:
      packageAllUrls['catalogue'].append(package['url'])
      print(f"CATALOGUE PAGE: {package['url']} :  {numberOfLinks}")
    else:
      packageAllUrls['package'].append(package['url'])
      print(f"PACKAGE PAGE: {package['url']} :  {numberOfLinks}")
  
  return packageAllUrls


def scrapePackages(packageUrls):
  for url in packageUrls:
    packageInfo = scrapePackage(url)
    uploadPackageDataToS3(packageInfo)
  ##TODO: FIX LLM CALL TO ATLEAST ALWAYS PROVIDE NULL ON THE REQUIRED PROPERTIES
  ##TODO: CALL THE SCRAPER.PY ON ALL THE PACKAGES 
  ##TODO: SET UP BOTO3 (AWS PYTHON SDK) TO SEND OUTPUT JSON FILES TO S3 STORAGE
  ##TODO: FINISH scrapeLinksFromHomePage() function
  ##TODO: HANDLE WEBPAGES THAT HAVE MULTIPLE SITEMAPS E.G. sitemap/offer (see alamanah travel)
  return 0


if __name__ == "__main__":
  if len(sys.argv) > 2:
    userChosenUrl = int(sys.argv[1])
  else:
    userChosenUrl = 2

with open('providers.txt','r') as f:
  providerList = f.read().splitlines()

sitemapurl = providerList[userChosenUrl] + "sitemap.xml"

print(sitemapurl)
resp = makeRequest(sitemapurl)

match resp.status_code:
  case 200 | 304:
    soup = getSoup(resp.text, parser="xml")
    hajjList, umrahList = scrapeLinksSitemap(soup)
  case 301:
    soup = getSoup(resp.text, parser="lxml")
    hajjList, umrahList = scrapeLinksHomePage(soup)

print("")
print("")
hajjPackageAndCatalogue = filterPackages(hajjList)
# umrahPackageUrls, umrahCatalogueUrls = filterPackages(umrahPackageUrls)

print(hajjPackageAndCatalogue)

if len(hajjPackageAndCatalogue['package']) < 10:
  scrapeLinksHomePage(hajjPackageAndCatalogue['catalogue'])

if hajjPackageAndCatalogue['package']:
  scrapePackages(hajjPackageAndCatalogue['package'])
  

