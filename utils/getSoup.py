from .helpers import makeRequest
import re
from bs4 import BeautifulSoup

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

# def removeFooterHeaderNav(soup):
#     for tag in soup.select("header, footer, nav"):
#         tag.decompose()

#     keywords = ["footer", "navbar", "nav-bar", "site-header", "page-header"]
#     patterns = [
#         re.compile(rf'(?:^|[\s_-]){re.escape(kw)}(?:[\s_-]|$)', re.IGNORECASE)
#         for kw in keywords
#     ]

#     for tag in list(soup.find_all(True)):
#         if not tag.attrs:
#             continue
#         tag_classes = tag.get("class", [])
#         tag_id = tag.get("id", "")
#         if isinstance(tag_classes, str):
#             tag_classes = [tag_classes]
#         if isinstance(tag_id, list):
#             tag_id = " ".join(tag_id)
#         all_values = " ".join(tag_classes) + " " + tag_id

#         if any(p.search(all_values) for p in patterns):
#             tag.decompose()

#     return soup

def getSoup(url, parser="lxml"):
  resp, err = makeRequest(url)
  if err is not None or resp is None:
    return None

  return createSoup(resp.text, parser)


def createSoup(text, parser="lxml"):
  soup = BeautifulSoup(text, features=parser)
  soup = removeFooterHeaderNav(soup)

  mains = soup.find_all("main")
  if mains:
    combined = BeautifulSoup('<div></div>', 'html.parser')
    container = combined.div
    for main in mains:
      container.append(main.extract())
    soup = combined

  return soup