import pandas as pd
import psycopg
import csv
import logging
from datetime import timedelta

logging.basicConfig(level=logging.INFO)

def filter(dataframe,null_values,duplicate_values,data_type_change,format_data,to_lowercase,to_uppercase):
    gender_mapping = {
    "M": "Male",
    "Male": "Male",
    "male": "Male",
    "F": "Female",
    "Female": "Female",
    "female": "Female"
}   
    logging.info('Enter the transformation pipeline')
    if(null_values):
        dataframe=dataframe.dropna()
    if(duplicate_values):
        dataframe=dataframe.drop_duplicates()
    if(data_type_change):
        dataframe['Date of Admission']=pd.to_datetime(dataframe['Date of Admission'],format='%Y-%m-%d')
        dataframe['Discharge Date']=pd.to_datetime(dataframe['Discharge Date'],format='%Y-%m-%d')
    if(format_data):
        dataframe["Gender"] = dataframe["Gender"].map(gender_mapping)
    if(to_lowercase and not to_uppercase):
        string_cols=dataframe.select_dtypes(include='object').columns
        dataframe[string_cols] = dataframe[string_cols].apply(
        lambda col: col.str.lower()
            )
       
    if(to_uppercase and not to_lowercase):
        string_cols=dataframe.select_dtypes(include='object').columns
        dataframe[string_cols] = dataframe[string_cols].apply(
        lambda col: col.str.upper()
            )
    else:
        pass
    string_cols = dataframe.select_dtypes(include="object").columns
    dataframe[string_cols] = dataframe[string_cols].astype("string")
   
    logging.info('Done with the Transformation of uploaded file!')
    return dataframe