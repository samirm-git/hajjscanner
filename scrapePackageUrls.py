import re
from helpers import makeRequest, getSoup, removeFooterHeaderNav
from pprint import pprint


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
  packageUrls, caltalougeUrls = [], []
  for package in packageList:
    resp = makeRequest(package['url'])
    soup = getSoup(resp.text, 'lxml')
    soup = removeFooterHeaderNav(soup)
    numberOfLinks = len(soup.find_all("a", href=True))
    if numberOfLinks > 10:
      caltalougeUrls.append(package['url'])
      print(f"CATALOGUE PAGE: {package['url']} :  {numberOfLinks}")
    else:
      packageUrls.append(package['url'])
      print(f"PACKAGE PAGE: {package['url']} :  {numberOfLinks}")
  
  return packageUrls, caltalougeUrls


def scrapePackages(packageUrls):
  for package in packageUrls:
    continue
  ##TODO: CALL THE SCRAPER.PY ON ALL THE PACKAGES 
  return 0


with open('providers.txt','r') as f:
  providerList = f.read().splitlines()

sitemapurl = providerList[2] + "sitemap.xml"

print(sitemapurl)
resp = makeRequest(sitemapurl)

match resp.status_code:
  case 200 | 304:
    soup = getSoup(resp.text, parser="xml")
    hajjPackageUrls, umrahPackageUrls = scrapeLinksSitemap(soup)
  case 301:
    soup = getSoup(resp.text, parser="lxml")
    hajjPackageUrls, umrahPackageUrls = scrapeLinksHomePage(soup)

print("")
print("")
hajjPackageUrls, hajjCatalogueUrls = filterPackages(hajjPackageUrls)
umrahPackageUrls, umrahCatalogueUrls = filterPackages(umrahPackageUrls)


if hajjPackageUrls:
  out = scrapePackages(hajjPackageUrls)
  if len(out) < 6:
    scrapeLinksHomePage(hajjCatalogueUrls)

if umrahPackageUrls:
  out = scrapePackages(umrahPackageUrls)
  if len(out) < 6:
    scrapeLinksHomePage(umrahCatalogueUrls)
# umrahPackageUrls = filterPackages(umrahPackageUrls)

