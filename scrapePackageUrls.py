import re
from helpers import makeRequest, getSoup
from pprint import pprint


def scrapeFromSitemap(soup):
  print("hello")
  pass

def scrapeFromHomePage(soup):
  print("hi")
  pass

with open('providers.txt','r') as f:
  providerList = f.read().splitlines()

zamzamTravelsSitemap = providerList[-1] + "sitemap.xml"
print(zamzamTravelsSitemap)
resp = makeRequest(zamzamTravelsSitemap)

match resp.status_code:
  case 200 | 304:
    soup = getSoup(resp.text, parser="xml")
    scrapeFromSitemap(soup)
  case 301:
    soup = getSoup(resp.text, parser="lxml")
    scrapeFromHomePage(soup)


print(resp.status_code)
