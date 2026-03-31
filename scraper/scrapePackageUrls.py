import re, sys
from scraper.helpers import makeRequest, getSoup, removeFooterHeaderNav
from tqdm import tqdm

def scrapeLinksHomePage(baseUrl, regex):
  return []

def scrapeLinksCatalogue(cataloguePages: list, regex):
  out = set()
  for url in cataloguePages:
    resp = makeRequest(url)
    soup = getSoup(resp.text, parser="lxml")
    links = {a["href"] for a in  soup.find_all("a", href=regex)}
    out.update(links)

  return list(out)

def getSitemapSoup(baseUrl):
  sitemapUrls = [baseUrl + "sitemap.xml", baseUrl + "page-sitemap.xml", baseUrl + "package-sitemap.xml"]
  out = []
  while sitemapUrls:
    url = sitemapUrls.pop()
    resp, err = makeRequest(url)
    if err:
      tqdm.write(f"Skipping {url}: {err}")
      continue
    if resp is None:  # 404
      continue

    elif resp.status_code == 200 or resp.status_code == 304:
      soup = getSoup(resp.text, parser='xml')
      soup = removeFooterHeaderNav(soup)
      out.append(soup)
  
  return out


def scrapeLinksSitemap(sitemapSoups, regex):
  out = set()
  for soup in sitemapSoups:
    for urlTag in soup.find_all("url"):
      link = urlTag.find("loc", string=regex)
      if link:
          out.add(link.get_text(strip=True))
      #TODO: IF last-modified IS VERY OLD DON'T USE IT
      lastmodTag = urlTag.find("lastmod")
      lastModified = lastmodTag.get_text(strip=True) if lastmodTag else None
    
  return list(out)


def scrapeLinksFromHomePage(soup, regex):
  return 
  

def scrapePackageUrls(baseUrl, regex):
  sitemapSoups = getSitemapSoup(baseUrl)
  urls = scrapeLinksSitemap(sitemapSoups, regex)
  homepageUrls = scrapeLinksHomePage(baseUrl, regex)
  #TODO: Complete scrapeLinksHomePage()
  urls.extend(homepageUrls)
  return urls
  

if __name__ == "__main__":
  HAJJREGEX = re.compile(r"hajj[-_]?package", re.IGNORECASE) 
  UMRAHREGEX = re.compile(r"umrah?[-_]?package", re.IGNORECASE)
  if len(sys.argv) >= 2:
    userChosenUrl = int(sys.argv[1])
  else:
    userChosenUrl = 2

  with open('providers.txt','r') as f:
    providerList = f.read().splitlines()
  print(providerList[userChosenUrl])
  print("")

  hajjUrls = scrapePackageUrls(providerList[userChosenUrl], HAJJREGEX)
  print(f"hajjUrls: {hajjUrls}")
  print(f"NUM hajjUrls: {len(hajjUrls)}")
  print("")

  umrahUrls = scrapePackageUrls(providerList[userChosenUrl], UMRAHREGEX)
  print(f"umrahUrls: {umrahUrls}")
  print(f"NUM umrahUrls: {len(umrahUrls)}")


