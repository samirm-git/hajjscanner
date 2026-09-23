from hajjUmrahEnum import HajjOrUmrahEnum
from urllib.parse import urljoin
from db import packageUrlQueries

def isCataloguePage(url, soup, companyName, save=True):
  HAJJREGEX = HajjOrUmrahEnum.HAJJ.regex
  UMRAHREGEX = HajjOrUmrahEnum.UMRAH.regex

  hajjPackageLinks, umrahPackageLinks = set(), set()

  for link in soup.find_all("a", href=True):
    href = link.get("href")
    if HAJJREGEX.search(href):
      hajjPackageLinks.add(urljoin(url, href))

    elif UMRAHREGEX.search(href):
      umrahPackageLinks.add(urljoin(url,href))
  
  if save:
    packageUrlQueries.saveUrls(provider=companyName, urls=hajjPackageLinks, type='hajj')
    packageUrlQueries.saveUrls(provider=companyName, urls=umrahPackageLinks, type='umrah')

  if len(hajjPackageLinks) + len(umrahPackageLinks) <= 5:
    return False
  else:
    packageUrlQueries.flagUrlIsCatalogue(url)
    return True