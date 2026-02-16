import re, json
from helpers import makeRequest, getSoup, removeFooterHeaderNav, loadHajjPackageSchema
from hotelScraper import scrapeHotelInformation, HEADING_TAGS 
from validator import validateData

# def findOverviewBlock(soup):
#   ##MANY PACKAGE WEBPAGE'S HAVE AN OVERVIEW BLOCK NEAR THE TOP OF THE BODY
#   overviewRegex = re.compile(r"(?:overview|highlights?|inclusions?|summary)", re.IGNORECASE)
#   overviews = soup.find_all(HEADING_TAGS, string=overviewRegex)
#   if not overviews:
#     return None
#   overviewContainers = []
#   for o in overviews:
#     o = o.find_parent("div") or o 
#     if o not in overviewContainers:
#       overviewContainers.append(o)
  
#   return overviewContainers
    

def tempScraper(text):
    # price = findPrice(text)
    totalNights = scrapeTotalDays(soup)

    nonshifting = bool(re.search(r"\bnon[-\s]?shifting\b", text, re.IGNORECASE))

    makkahHotel = re.search(r"(?:Makkah|Mecca|Meccah|Makah)[\s-]*(?:hotels?|Hotel)", text, re.IGNORECASE)
    makkahHotel = makkahHotel.groups() if makkahHotel else None
    if makkahHotel is None:
      makkahHotel = re.search(r'\b([Hh]otels?\s+in\s+(?:Makkah|Mecca))\b', text, re.IGNORECASE)
      makkahHotel = makkahHotel.groups() if makkahHotel else None

    hotelInfo = scrapeHotelInformation(soup)


    makkahHotel = hotelInfo["makkah"]
    madinahHotel = hotelInfo["madinah"]
    otherHotel = hotelInfo["other"]


    print("")
    # print(price)
    print(f"totalNights: {totalNights}")
    print(nonshifting)

    print("")
    print(f"makkahHotelImages: {makkahHotel['images']}")
    print("")
    print(f"madinahHotelImages: {madinahHotel['images']}")
    print("")
    print(f"otherImages: {otherHotel['images']}")
    print("")
    print(f"makkah hotel info: {makkahHotel}")
    print("")
    print(f"madinah hotel info: {madinahHotel}")

def scrapeTotalDays(soup):
  for tag in soup.find_all(HEADING_TAGS):
    text = tag.get_text(strip = True)
    match = re.search(r"(\d+)[-\s]?(?:night|day)s?", text, re.IGNORECASE)
    if match:
      return int(match.group(1))
  return 

def scrapePPP(soup): 
  priceRegex = re.compile(r"([£$€])\s?(\d+(?:,\d{3})*(?:\.\d{2})?)", re.IGNORECASE)
  #can do re.search(r"...", soup.get_text(strip=True)) for faster searching (not sure how much faster)
  #but then we would not know which container the matching text comes from which may be useful e.g. finding the parent container for more context (although not doing this currently).
  #moreover, with soup.find(...) we can filter the containers we are searching through e.g heading [h1, h2, ..., h6] containers.
  priceContainer = soup.find(string=priceRegex)
  if priceContainer:
    match = priceRegex.match(priceContainer.get_text(strip=True))
    currency = match.group(1)
    #TODO: CONVERT CURRENCY TO STANDARD CURRENCY PRICE TO STANDARD CURRENCY E.G £
    price = int(match.group(2))
    return int(price)
  else:
    return None

def scrapeTier(soup):
  tierRegex = re.compile(r"luxury|premium|economy", re.IGNORECASE)
  tierContainer = soup.find(string=tierRegex)
  if tierContainer:
    return tierRegex.search(tierContainer.get_text(strip=True)).group(1)
  else: 
    return None

def scrapeStars(soup):
  starsRegex = re.compile(r'\b([1-5])\s*(?:-?\s*star|stars?)\b', re.IGNORECASE)
  starContainer = soup.find(string=starsRegex)
  if starContainer:
    return int(starsRegex.search(starContainer.get_text(strip=True)).group(1))
  return None

def scrapeIsShifting(soup):
  nonshifting = bool(re.search(r"\bnon[-\s]?shifting\b", soup.get_text(strip=True), re.IGNORECASE))  
  if nonshifting:
    return False
  else:
    return True

def scrapeIsVisaIncluded(soup):
  isVisaIncludedRegex = re.compile(r'\b(?:visa|visas?)\s+(?:is\s+)?(?:included|covered|provided|arranged|taken\s+care\s+of)\b|\b(?:includes?|with|including)\s+(?:visa|visas?)\b', re.IGNORECASE)
  isVisaIncluded = bool(isVisaIncludedRegex.search(soup.get_text(strip=True)))
  if isVisaIncluded:
    return True
  else:
    visaRegex = re.compile('visa', re.IGNORECASE)
    visaContainer = soup.find(string=visaRegex)
    if not visaContainer:
      return False
    else:
      #REQUIRES FURTHER ANALYSIS. MAYBE PASS THE PARENT DIV TO LLM
      return 
  


url = "https://alamanahtravel.co.uk/14-days-5-star-non-shifting-hajj-package/"
url2 = "https://www.safamarwahtravel.co.uk/deals/5-star-17-days-non-shifting-hajj-package/"
url3 = "https://www.alhaqtravel.co.uk/book/24-days-shifting-hajj-packages/"
url4 = "https://duatravels.co.uk/package/shifting-luxury-hajj-package/"

packageSchema = loadHajjPackageSchema()
packageInfoResolvers = {
  'ppp': scrapePPP,
  'total_days': scrapeTotalDays,
  # 'tier': scrapeTier,
  'stars': scrapeStars,
  'isShifting': scrapeIsShifting,
  'makkahHotel': scrapeHotelInformation,
  'madinahHotel': scrapeHotelInformation,
  'isVisaIncluded': scrapeIsVisaIncluded
}
packageInfo = {}


resp = makeRequest(url3)
soup = getSoup(resp.text, parser="lxml")
soup = removeFooterHeaderNav(soup)
if soup.find("main"):
  soup = soup.find("main")

for key in packageInfoResolvers.keys():
  if packageInfo.get(key, False):
    continue

  if key == 'makkahHotel':
    pass
    packageInfo[key] = packageInfoResolvers[key](soup, 'makkah')
  elif key == 'madinahHotel':
    pass
    packageInfo[key] = packageInfoResolvers[key](soup, 'madinah')
  else:
    value = packageInfoResolvers[key](soup)
    if value:
      packageInfo[key] = value
  

print(f"packageInfo: {packageInfo}")
print("----------------------------")
print(f"packageInfo stars: {packageInfo['stars']}")

with open('scraperoutput.text','a') as f:
  json.dump(packageInfo, f, indent=4)
  f.write('\n')

validateData(packageInfo)



#==========================================
# tempScraper(visible_text)
#==========================================


# print(soup.prettify())
# package_div = soup.find("div", class_="detail_package")
# price = package_div.find("strong").getText()
