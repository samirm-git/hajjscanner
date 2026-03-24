import boto3
import uuid
import json
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()
s3 = boto3.client('s3')

def getID():
  id = str(uuid.uuid4())
  return id


def uploadPackageDataToS3(packageInfo, company=None):
  if company == None:
    company = packageInfo.get("company", "BADDATA")
  
  packageInfo = json.dumps(packageInfo, indent=4)
  try:
    response = s3.put_object(Bucket='hajjpackagedata', Key=f'raw/{company}/{getID()}', Body=packageInfo, ContentType='application/json')
  except ClientError as e:
    print(e)

