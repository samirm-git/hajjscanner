import re
from helpers import makeRequest, getSoup, removeFooterHeaderNav, loadHajjPackageSchema
from hotelScraper import scrapeHotelInformation, HEADING_TAGS 

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
      return match.group(1)
  return None

def scrapePPP(soup): 
  priceRegex = re.compile(r"([£$€])\s?(\d+(?:,\d{3})*(?:\.\d{2})?)", re.IGNORECASE)
  priceText = soup.find(string=priceRegex)
  if priceText:
    match = priceRegex.match(str(priceText))
    currency = match.group(1)
    #TODO: CONVERT CURRENCY TO STANDARD CURRENCY PRICE TO STANDARD CURRENCY E.G £
    price = match.group(2)
    return price
  else:
    return None

def scrapeTier(soup):
  return None

def scrapeStars(soup):
  return None

def scrapeIsShifting(soup):
  return None

def scrapeIsVisaIncluded(soup):
  return None

def findOverviewBlock(soup):
  ##MANY PACKAGE WEBPAGE'S HAVE AN OVERVIEW BLOCK NEAR THE TOP OF THE BODY
  overviewRegex = re.compile(r"(?:overview|highlights?|inclusions?|summary)", re.IGNORECASE)
  overviews = soup.find_all(HEADING_TAGS, string=overviewRegex)
  print(f"type(overviews): {type(overviews)}")
  if not overviews:
    return None
  overviewContainers = []
  for o in overviews:
    o = o.find_parent("div") or o 
    if o not in overviewContainers:
      overviewContainers.append(o)
  
  return overviewContainers
    

  
url = "https://alamanahtravel.co.uk/14-days-5-star-non-shifting-hajj-package/"
url2 = "https://www.safamarwahtravel.co.uk/deals/5-star-17-days-non-shifting-hajj-package/"
url3 = "https://www.alhaqtravel.co.uk/book/24-days-shifting-hajj-packages/"
url4 = "https://duatravels.co.uk/package/shifting-luxury-hajj-package/"

packageSchema = loadHajjPackageSchema()
packageInfoResolvers = {
  'ppp': scrapePPP,
  'total_days': scrapeTotalDays,
  'tier': scrapeTier,
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

text = soup.get_text(" ", strip=True)


overviewContainers = findOverviewBlock(soup)

for container in overviewContainers:
  print(f"packageInfo: {packageInfo}")
  for key in packageInfoResolvers.keys():
    if packageInfo.get(key, False):
      continue

    if key == 'makkahHotel':
      packageInfo[key] = packageInfoResolvers[key](container, 'makkah')
    elif key == 'madinahHotel':
      packageInfo[key] = packageInfoResolvers[key](container, 'madinah')
    else:
      packageInfo[key] = packageInfoResolvers[key](container) 
    
print(f"packageInfo end: {packageInfo}")




#==========================================
# tempScraper(visible_text)
#==========================================


# print(soup.prettify())
# package_div = soup.find("div", class_="detail_package")
# price = package_div.find("strong").getText()
