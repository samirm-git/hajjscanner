import json 
from dotenv import load_dotenv
import os
from google import genai
from google.genai.types import GenerateContentConfig
from helpers import loadHotelSchema
from gemini_helpers import *
from consts import CITY_PATTERNS, CONTAINER_TAGS, HEADING_TAGS
from scrapers import runScrapers, updateScrapedInfo

load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")

def LLMPrompter(client, containerText, hotelSchema):
  response = client.models.generate_content(
  model="gemini-2.5-flash-lite",
  contents=f"""Extract hotel information from the text below. Infer where reasonable (e.g. 'Quad'=4 beds, 'days'='nights', drive time is not walk time). Do any necessary metric conversions e.g. miles to metres. Use null if genuinely unavailable.

Text:
{containerText}
""",
  config=GenerateContentConfig(response_mime_type="application/json", response_schema=hotelSchema)
    )

  with open('gemini_output.txt','a') as f:
    f.write('\n')
    f.writelines(response.text)

  try:
    output = json.loads(response.text)
    return output
  except json.JSONDecodeError as e:
    print(f"llmOutput not valid json: {response.text}")
    print(e)
    return None

def checkCityinText(text, city):
  if CITY_PATTERNS[city].search(text):
    return True
  else:
    return False


def getChildContainerIDs(container):
  out = set()
  for descendant in container.find_all(CONTAINER_TAGS):
    out.add(id(descendant))
  
  return out



#TODO: ADD MANUAL SCRAPPING FOR ALL OTHER FIELDS. ONLY CALL LLM IF FIELDS ARE MISSING OR TO COMPARE ANSWERS
# print(hotelSchema)
def scrapeHotelInfo(soup, city):
  city = city.lower()
  otherCity = 'madinah' if city == 'makkah' else 'makkah'
  hotelSchema = jsonUperCaseTypes(loadHotelSchema())
  remove_property(hotelSchema, 'images')


  hotelInfo = {}
  seen = set()

  with genai.Client(api_key=GEMINI_KEY) as client:
    for container in soup.find_all(CONTAINER_TAGS):
      if id(container) in seen:
        continue

      headingText = " ".join(h.get_text(strip=True) for h in container.find_all(HEADING_TAGS))            
      if not headingText:
        seen.update(getChildContainerIDs(container))

      elif not checkCityinText(headingText, city):
        # print(f"Did not find desired city: {city}")
        seen.update(getChildContainerIDs(container))
      
      elif checkCityinText(headingText, otherCity):
        pass
        # print(f"Found other city: {otherCity}")
        
      else:
        # print(f"found container with desired city: {city}, and no other city: {otherCity} in heading text")
        seen.update(getChildContainerIDs(container)) 

        fullText = container.get_text("\n", strip=True) # Use fullText as a fall back e.g. call AI model with fullText
        
        # llmOutput = LLMPrompter(client, fullText, hotelSchema)
        newScrapedInfo = runScrapers(container, 'hotel info')
        hotelInfo = updateScrapedInfo(oldScrapedInfo=hotelInfo, newScrapedInfo=newScrapedInfo)

        # if llmOutput:
          # hotelInfo.update(llmOutput)


  if hotelInfo == {}:
    return None
  if hotelInfo.get("images", False):
      hotelInfo["images"] = list(hotelInfo["images"])
  else:
      hotelInfo["images"] = None
  return hotelInfo
