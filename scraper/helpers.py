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
    )
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
    # Remove semantic tags
    for tag in soup.select("header, footer, nav"):
        tag.decompose()

    # Remove elements whose class or id contains 'footer' or 'background'
    keywords = ["footer", "background"]
    for tag in list(soup.find_all(True)):
        if tag.attrs is None:
            continue

        tag_classes = tag.get("class", [])
        tag_id = tag.get("id", "")

        # Normalise both to lists of strings
        if isinstance(tag_classes, str):
            tag_classes = [tag_classes]
        if isinstance(tag_id, list):
            tag_id = " ".join(tag_id)

        if any(
            keyword in value
            for keyword in keywords
            for value in tag_classes + [tag_id]
        ):
            tag.decompose()

    return soup

def loadHotelSchema():
  hotelSchemaPath = getProjectRoot() / "schema" / "hotel.json"
  with open(hotelSchemaPath, 'r') as f:
    hotelSchema = json.load(f)
  return hotelSchema

def loadHajjPackageSchema():
  path = getProjectRoot() / "schema" / "hajjPackage.json"
  with open(path, 'r') as f:
    hajjPackageSchema = json.load(f)
  return hajjPackageSchema

# def isKeywordIncludedRegex(keyword):
#   word = re.escape(keyword)
#   pattern = rf"""
# \b
# (
#     {word}s?\b              # key or keys
#     (?:[^.!?\n]*?)  
#     (?:is\s+|are\s+)?              # optional "is"
#     (?:included|covered|provided|arranged|taken\s+care\s+of)
#   |
#     (?:includes?|including|has)\s+
#     (?:[^.!?\n]*?)  
#     {word}s?\b
# )
# \b
# """
#   return re.compile(pattern, re.IGNORECASE | re.VERBOSE)



def getProjectRoot(marker: str = ".gitignore") -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / marker).exists():
            return parent
    raise RuntimeError(f"{marker} not found")
