import pandas as pd
import streamlit as st
import awswrangler as wr
from dotenv import load_dotenv
# from athenaRunner import QUERIES

load_dotenv()

@st.cache_data
def loadData(queryName):
  try:
      path = f's3://hajjpackagedata/athena-results/{queryName}/'
      df = wr.s3.read_csv(path)
      return df, None
  except Exception as e:
      return None, e

if __name__ == "__main__":
  df, err = loadData('allData')
  if err is None:
    print(df.shape)
    # print(df.head())
    print(df.columns.values)
  else:
     print(str(e))
