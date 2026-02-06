import re 
import json
from dotenv import load_dotenv
from pathlib import Path
import os
from google import genai
from google.genai.types import GenerateContentConfig

load_dotenv()

PROJECT_ROOT = Path(__file__).parent
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
CONTAINER_TAGS = ["div", "section", "article", "td", "tr"]
HEADING_TAGS = ["h1", "h2", "h3", "h4", "h5", "h6", "small", "strong"]
CITY_PATTERNS = {
    "makkah": re.compile(r"\b(makkah|mecca|meccah|makah)\b", re.IGNORECASE),
    "madinah": re.compile(r"\b(madinah|medina)\b", re.IGNORECASE),
}
BAD_IMAGE = re.compile(r"(icon|place[-_]?holder)", re.IGNORECASE)
  

def jsonUperCaseTypes(obj):
  unsupported = ["$schema", "$id", "title", "uniqueItems", "minLength", "maxLength"]
  if isinstance(obj, dict):
    result = {}
    for key, value in obj.items():
      if key in unsupported:
        continue
      elif key == "type" and isinstance(value, str):
        result[key] = value.upper()
      elif key in ["$schema", "$id", "title"]:
        # Skip JSON Schema metadata
        continue
      else:
        result[key] = jsonUperCaseTypes(value)
    return result
    
  elif isinstance(obj, list):
    return [jsonUperCaseTypes(item) for item in obj]
  else:
    return obj

def LLMPrompter(container, hotelSchema):
  text = container.get_text(" ", strip=True)
  with genai.Client(api_key=GEMINI_KEY) as client:
    response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"""You are extracting hotel information from the following website text.
Text:
  {text}
""",
    config=GenerateContentConfig(response_mime_type="application/json", response_schema=hotelSchema)
      )

  with open('gemini_output.txt','a') as f:
    f.write('\n')
    f.writelines(response.text)


  return response.text
    

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
    hotelSchema = jsonUperCaseTypes(loadHotelSchema())

    makkah_info = {'images':set()}
    madinah_info = {'images':set()}
    other_info = {'images':set()}

    seen = set()

    for container in soup.find_all(CONTAINER_TAGS):
        
        if id(container) in seen:
          continue
       
        headingText = " ".join(h.get_text(" ", strip=True) for h in container.find_all(HEADING_TAGS))            
        fullText = container.get_text(" ", strip=True) # Use fullText as a fall back e.g. call AI model with fullText

        makkahFound = bool(CITY_PATTERNS["makkah"].search(headingText))
        madinahFound = bool(CITY_PATTERNS["madinah"].search(headingText))
        if makkahFound and madinahFound:
            continue
        
        if makkahFound:
          for descendant in container.find_all(CONTAINER_TAGS):
            seen.add(id(descendant))
          temp = LLMPrompter(container, hotelSchema)
          if temp:
            makkah_info.update(json.loads(temp))
          
          makkah_info['images'].update(extractHotelImages(container))

        elif madinahFound:
          for descendant in container.find_all(CONTAINER_TAGS):
            seen.add(id(descendant))
          temp = LLMPrompter(container, hotelSchema)
          if temp:
            madinah_info.update(json.loads(temp))
          
          madinah_info['images'].update(extractHotelImages(container))

        else:
          other_info["images"].update(extractHotelImages(container))


    return {
       "makkah" : makkah_info,
       "madinah" : madinah_info,
       "other" : other_info
    }


def loadHotelSchema():
  hotelSchemaPath = PROJECT_ROOT / "schema" / "hotel.json"
  with open(hotelSchemaPath, 'r') as f:
    hotelSchema = json.load(f)
  return hotelSchema
