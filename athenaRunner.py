# import time
# import boto3
# from dotenv import load_dotenv

# load_dotenv()
# athena = boto3.client('athena') 
# s3 = boto3.client('s3')
# HAJJ_QUERIES = {'allData':"""SELECT 
#               url,
#               ppp,
#               year,
#               total_days,
#               tier,
#               stars,
#               isShifting,
#               departureCity,
#               isVisaIncluded,
#               company,

#               -- Makkah hotel
#               makkahHotel.name            AS makkah_name,
#               makkahHotel.images          AS makkah_images,
#               makkahHotel.total_days      AS makkah_total_days,
#               makkahHotel.stars           AS makkah_stars,
#               makkahHotel.hasWifi         AS makkah_hasWifi,
#               makkahHotel.hasAC           AS makkah_hasAC,
#               makkahHotel.distanceToHaram AS makkah_distanceToHaram,
#               makkahHotel.walkToHaram     AS makkah_walkToHaram,
#               makkahHotel.numberOfBeds    AS makkah_numberOfBeds,
#               makkahHotel.otherAmenities  AS makkah_otherAmenities,

#               -- Madinah hotel
#               madinahHotel.name            AS madinah_name,
#               madinahHotel.images          AS madinah_images,
#               madinahHotel.total_days      AS madinah_total_days,
#               madinahHotel.stars           AS madinah_stars,
#               madinahHotel.hasWifi         AS madinah_hasWifi,
#               madinahHotel.hasAC           AS madinah_hasAC,
#               madinahHotel.distanceToHaram AS madinah_distanceToHaram,
#               madinahHotel.walkToHaram     AS madinah_walkToHaram,
#               madinahHotel.numberOfBeds    AS madinah_numberOfBeds,
#               madinahHotel.otherAmenities  AS madinah_otherAmenities
          
#            FROM hajjpackagedata.hajj_packages ORDER BY ppp DESC"""}


# def runAthenaQuery(queryName, queryString):
#   try:
#       athenaResultsFolder = f"athena-results/{queryName}"

#       query_id = athena.start_query_execution(
#           QueryString=queryString,
#           QueryExecutionContext={"Database": "hajjpackagedata"},
#           ResultConfiguration={
#               "OutputLocation": f"s3://hajjpackagedata/{athenaResultsFolder}/"
#           },
#       )["QueryExecutionId"]

#       while True:
#           state = athena.get_query_execution(
#               QueryExecutionId=query_id
#           )["QueryExecution"]["Status"]["State"]

#           if state == "SUCCEEDED":
#               break

#           if state in ("FAILED", "CANCELLED"):
#               raise RuntimeError(f"Athena query {state}")

#           time.sleep(2)

#       # Query succeeded — delete previous results, keeping only the new file
#       # existing = s3.list_objects_v2(Bucket="hajjpackagedata", Prefix=athenaResultsFolder)
#       # for obj in existing.get("Contents", []):
#       #     if obj["Key"] != f"{athenaResultsFolder}/{query_id}.csv":
#       #         s3.delete_object(Bucket="hajjpackagedata", Key=obj["Key"])

#       # print(f"queryID: {query_id}")

#   except Exception as e:
#       print(str(e))
#       return None

# if __name__ == "__main__":
#    runAthenaQuery('allData', QUERIES["allData"])