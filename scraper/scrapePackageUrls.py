import re, sys
from scraper.helpers import makeRequest, getSoup
from tqdm import tqdm
from scraper.db import getAllProviders, saveUrls
from urllib.parse import urljoin

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
      # soup = removeFooterHeaderNav(soup)
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


def scrapeLinksHomePage(baseurl, regex):
  resp, err = makeRequest(baseurl)
  if err:
    tqdm.write(f"requested {baseurl}: {err}")
    return

  soup = getSoup(resp.text, parser='lxml')
  out = {a["href"] for a in  soup.find_all("a", href=regex)}

  return list(out)
  

def scrapePackageUrls(companyName, baseUrl, regex, hajjOrUmrah):
  sitemapSoups = getSitemapSoup(baseUrl)
  urls = scrapeLinksSitemap(sitemapSoups, regex)
  homepageUrls = scrapeLinksHomePage(baseUrl, regex)
  urls.extend(homepageUrls)
  urls = {urljoin(baseUrl, url) for url in urls} 
  saveUrls(provider=companyName, urls=urls, type=hajjOrUmrah)
  return urls
  

if __name__ == "__main__":
  HAJJREGEX = re.compile(r"hajj[-_]?package", re.IGNORECASE) 
  UMRAHREGEX = re.compile(r"umrah?[-_]?package", re.IGNORECASE)
  if len(sys.argv) >= 2:
    userChosenUrl = int(sys.argv[1])
  else:
    userChosenUrl = 2

  providers = getAllProviders() 
  
  for providerName, homepage_url in providers.items():
    hajjUrls = scrapePackageUrls(providerName, homepage_url, HAJJREGEX, 'hajj')
    # print(f"hajjUrls: {hajjUrls}")
    # print(f"NUM hajjUrls: {len(hajjUrls)}")
    # print("")


    umrahUrls = scrapePackageUrls(providerName, homepage_url, UMRAHREGEX, 'umrah')
    # print(f"umrahUrls: {umrahUrls}")
    # print(f"NUM umrahUrls: {len(umrahUrls)}")


