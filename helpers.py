import requests
from bs4 import BeautifulSoup

def makeRequest(url):
  headers = {
    # "User-Agent": "Chrome/117.0.0.0",
    "User-Agent": (
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
      "AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/144.0.0.0 Safari/537.36"
    ),
    # "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    # "accept-encoding": "gzip, deflate, br, zstd",
    # "accept-language": "en-US,en;q=0.9",
    # "cache-control": "max-age=0",
  }
  resp = requests.get(url, headers=headers)
  return resp

def getSoup(respText, parser="html.parser"):
  soup = BeautifulSoup(respText, parser)
  return soup

def removeFooterHeaderNav(soup):
  for tag in soup.select("header, footer, nav"):
    tag.decompose()

  return soup