import requests
from bs4 import BeautifulSoup
from pathlib import Path
import json
import re

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

def loadHotelSchema():
  hotelSchemaPath = Path(__file__).parent / "schema" / "hotel.json"
  with open(hotelSchemaPath, 'r') as f:
    hotelSchema = json.load(f)
  return hotelSchema

def loadHajjPackageSchema():
  path = Path(__file__).parent / "schema" / "hajjPackage.json"
  with open(path, 'r') as f:
    hajjPackageSchema = json.load(f)
  return hajjPackageSchema

def isKeywordIncludedRegex(keyword):
  word = re.escape(keyword)
  pattern = rf"""
\b
(
    {word}?\s+                # key or keys
    (?:is\s+)?               # optional "is"
    (?:included|covered|provided|arranged|taken\s+care\s+of)
  |
    (?:includes?|including|has)\s+
    {word}?
)
\b
"""
  return re.compile(pattern, re.IGNORECASE | re.VERBOSE)
