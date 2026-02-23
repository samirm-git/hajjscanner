import boto3
import uuid
from botocore.exceptions import ClientError
s3 = boto3.client('s3')

def getID():
  id = str(uuid.uuid4())
  return id


def uploadPackageDataToS3(jsonData, company):
  try:
    response = s3.put_object(Bucket='hajjpackagedata', Key=f'raw/{company}/{getID()}', Body=jsonData, ContentType='application/json')
  except ClientError as e:
    print(e)

