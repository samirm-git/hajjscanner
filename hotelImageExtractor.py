import re 

CONTAINER_TAGS = ["div", "section", "article", "td", "tr"]
HEADING_TAGS = ["h1", "h2", "h3", "h4", "h5", "h6", "small", "strong"]
CITY_PATTERNS = {
    "makkah": re.compile(r"\b(makkah|mecca|meccah|makah)\b", re.IGNORECASE),
    "madinah": re.compile(r"\b(madinah|medina)\b", re.IGNORECASE),
}
BAD_IMAGE = re.compile(r"(icon|place[-_]?holder)", re.IGNORECASE)

def extractHotelImages(container_soup):
  hotelImgs = set()
  imgs = container_soup.find_all("img") #I think you can add a regex expression as a another parameter to make sure the image src does not include 'placeholder'
  if not len(imgs) > 3:
    return set() 
  for img in imgs:
    src = (img.get("data-src") or img.get("data-original") or img.get("data-lazy") or img.get("src"))
    if not src:
      continue
    elif bool(BAD_IMAGE.search(src)):
        continue
    else:
       hotelImgs.add(src)
  
  return hotelImgs

def extractHotelInformation(soup):
    ## TODO: SEND TEXT OF CONTAINER THAT CONTAINS MAKKAH OR MADINAH TO AI TO EXTRACT INFORMATION
    makkah_images = set()
    madinah_images = set()
    other_images = set()

    makkah_info = {}
    madinah_info = {}
    other_info = {}

    for container in soup.find_all(CONTAINER_TAGS):
       
        headingText = " ".join(h.get_text(" ", strip=True) for h in container.find_all(HEADING_TAGS))            
        fullText = container.get_text(" ", strip=True) # Use fullText as a fall back e.g. call AI model with fullText

        makkahFound = bool(CITY_PATTERNS["makkah"].search(headingText))
        madinahFound = bool(CITY_PATTERNS["madinah"].search(headingText))
        if makkahFound and madinahFound:
            continue
        elif makkahFound:
          # makkah_info.add(...)          
          makkah_images.update(extractHotelImages(container))
        elif madinahFound:
          #  madinah_info.add(...)
           madinah_images.update(extractHotelImages(container))
        else:
          #  other_info.add(...)
           other_images.update(extractHotelImages(container))


    return {
       "makkah" : {"information": {}, "images": makkah_images},
       "madinah" : {"information": {}, "images": madinah_images},
       "other" : {"other": {}, "images": other_images}
    }

