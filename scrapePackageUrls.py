import re
from helpers import makeRequest, getSoup, removeFooterHeaderNav
from pprint import pprint


def scrapeFromSitemap(soup):
  hajjPackages = []
  umrahPackages = []
  for urlTag in soup.find_all("url"):
    url = urlTag.find("loc").get_text(strip=True)
    #TODO: MAKE THIS MORE ROBUST AS AN RE SEARCH OVER 'hajjpackage' , 'hajj_package', ...
    if re.search(r"hajj[-_]?package", url, re.IGNORECASE):
      lastModified = urlTag.find("lastmod").get_text(strip=True)
      hajjPackages.append({'url':url, 'last-modified': lastModified})
    elif re.search(r"umrah?[-_]?package", url, re.IGNORECASE):
      lastModified = urlTag.find("lastmod").get_text(strip=True)
      umrahPackages.append({'url': url, 'last-modified': lastModified})
  
  return (hajjPackages, umrahPackages)
    
def scrapeFromHomePage(soup):
  print("hi")

  return None, None

def filterPackages(packageList):
  for package in packageList:
    resp = makeRequest(package['url'])
    soup = getSoup(resp.text, 'lxml')
    soup = removeFooterHeaderNav(soup)
    numberOfLinks = len(soup.find_all("a", href=True))
    if numberOfLinks > 10:
      print(f"CATALOGUE PAGE: {package['url']} :  {numberOfLinks}")
    else:
      print(f"PACKAGE PAGE: {package['url']} :  {numberOfLinks}")

with open('providers.txt','r') as f:
  providerList = f.read().splitlines()

alHaqSitemap = providerList[2] + "sitemap.xml"
print(alHaqSitemap)
resp = makeRequest(alHaqSitemap)

match resp.status_code:
  case 200 | 304:
    soup = getSoup(resp.text, parser="xml")
    hajjPackages, umrahPackages = scrapeFromSitemap(soup)
  case 301:
    soup = getSoup(resp.text, parser="lxml")
    hajjPackagesj, umrahPackages = scrapeFromHomePage(soup)

print("")
print("")
hajjPackages = filterPackages(hajjPackages)
# umrahPackages = filterPackages(umrahPackages)

print(hajjPackages)

## if there is multiple links on the page then we know this is not for a specific package.
## is there a more sophisticated way to differentiate between a catalogue page and a specific package details page