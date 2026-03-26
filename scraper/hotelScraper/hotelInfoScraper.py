import json 
import re
import os
from google import genai
from google.genai.types import GenerateContentConfig
from scraper.helpers import loadHotelSchema, getProjectRoot
from scraper.gemini_helpers import *
from scraper.consts import CITY_PATTERNS, CONTAINER_TAGS, HEADING_TAGS
from scraper.scrapers import runScrapers, updateScrapedInfo, scrapeHotelName



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

  path = getProjectRoot() / 'gemini_output.txt'
  with open(path,'a') as f:
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
  if re.search(CITY_PATTERNS[city], text, re.IGNORECASE):
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
  #NOTE FOR GEMINI SCHEMA WE CANNOT ALLOW MORE THAN 1 TYPE + NULL. 
  #IF USING GEMINI AGAIN, MUST REMOVE array FROM TYPE FIELD
  # hotelSchema = jsonUperCaseTypes(loadHotelSchema())
  # remove_property(hotelSchema, 'images')


  hotelInfo = {}
  seen = set()

  with genai.Client(api_key=GEMINI_KEY) as client:
    for container in soup.find_all(True):
      if id(container) in seen:
        continue

      fullText = container.get_text(separator=" ", strip=True)

      if not checkCityinText(fullText, city):
        # print(f"Did not find desired city: {city}")
        seen.update(getChildContainerIDs(container))
      
      elif checkCityinText(fullText, otherCity):
        pass
        # print(f"Found other city: {otherCity}")
        
      else:
        # print(f"found container with desired city: {city}, and no other city: {otherCity} in heading text")
        seen.update(getChildContainerIDs(container)) 

        # fullTextLLM = container.get_text("\n", strip=True) # Use fullText as a fall back e.g. call AI model with fullText
        
        # llmOutput = LLMPrompter(client, fullTextLLM, hotelSchema)
        hotelInfo['name'] = scrapeHotelName(container, city)
        newScrapedInfo = runScrapers(container, 'hotel info')
        hotelInfo = updateScrapedInfo(oldScrapedInfo=hotelInfo, newScrapedInfo=newScrapedInfo)

        # if llmOutput:
          # hotelInfo.update(llmOutput)

  for key in hotelInfo.keys():
    if isinstance(hotelInfo[key], set):
      hotelInfo[key] = list(hotelInfo[key])

  return hotelInfo
