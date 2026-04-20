import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from pathlib import Path
import json
import re
import unicodedata
from scraper.regexConsts import COMMON_HOTEL_WORDS_RE


def makeRequest(url, timeout=10, retries=3):
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
  retry_strategy = Retry(
        total=retries,
        backoff_factor=1,
        status_forcelist=[429, 502, 503, 504],
        allowed_methods=["GET"],
    )

  adapter = HTTPAdapter(max_retries=retry_strategy)
  session = requests.Session()
  session.mount("https://", adapter)
  session.mount("http://", adapter)

  try:
      resp = session.get(url, headers=headers, timeout=timeout)
      resp.raise_for_status()
      return resp, None

  except requests.exceptions.ConnectionError as e:
      if "NameResolutionError" in str(e) or "getaddrinfo failed" in str(e):
          return None, RuntimeError(f"DNS resolution failed for URL: {url}")
      return None, RuntimeError(f"Connection error for URL: {url}")

  except requests.exceptions.Timeout:
      return None, RuntimeError(f"Request timed out after {timeout}s for URL: {url}")

  except requests.exceptions.HTTPError as e:
      status_code = getattr(e.response, "status_code", None)
      if status_code == 404:
          return None, None
      return None, RuntimeError(f"HTTP error {status_code} for URL: {url}")

  except requests.exceptions.RetryError as e:
      return None, RuntimeError(f"Max retries exceeded for URL: {url}")
  
  except requests.exceptions.MissingSchema as e:
     return None, RuntimeError(f"missing schema excpetion for:  {url}")
  
  except requests.exceptions.InvalidSchema as e:
     return None, RuntimeError(f"invalid schema exception for: {url}")
  # resp = requests.get(url, headers=headers)
  # return resp

def getSoup(respText, parser="html.parser"):
  soup = BeautifulSoup(respText, parser)
  return soup

def removeFooterHeaderNav(soup):
    # Remove semantic tags
    for tag in soup.select("header, footer, nav"):
        tag.decompose()

    # Much more precise keywords — only exact structural identifiers
    keywords = ["footer", "navbar", "nav-bar", "site-header", "page-header"]
    
    for tag in list(soup.find_all(True)):
        if not tag.attrs:
            continue

        tag_classes = tag.get("class", [])
        tag_id = tag.get("id", "")

        if isinstance(tag_classes, str):
            tag_classes = [tag_classes]
        if isinstance(tag_id, list):
            tag_id = " ".join(tag_id)

        # Use whole-word matching instead of substring matching
        all_values = " ".join(tag_classes) + " " + tag_id
        if any(
            f"-{keyword}" in all_values
            or f"{keyword}-" in all_values
            or all_values.strip() == keyword
            for keyword in keywords
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

def getProjectRoot(marker: str = ".gitignore") -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / marker).exists():
            return parent
    raise RuntimeError(f"{marker} not found")

def cleanText(text):
    def remove_arabic(text):
      return re.sub(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+', '', text)

    def normalize_text(text):
      text = text.lower()
      text = unicodedata.normalize('NFKC', text)

      text = text.encode('ascii', 'ignore').decode('ascii')

      text = COMMON_HOTEL_WORDS_RE.sub("", text)
      text = re.sub(r"\d+", "", text)         
      text = re.sub(r"[^\w\s]", "", text)
      text = re.sub(r"\s+", " ", text).strip()

      return text 

    if not text:
      return ""

    text = remove_arabic(text)
    text = normalize_text(text)
    return text
