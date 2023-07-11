import pandas as pd
import plotly
from plotly import express as px
import sqlite3
import os
import json
import numpy as np
from scipy import stats
import plotly.express.colors

def clean(df):
    '''
    This function will clean each city's dataset
    Args: df the dataset of a city
    Returns: cleaned dataset that no longer contains columns that are not needed (such as photos)
    '''
    re_str = 'photos/' # use this string to drop all 'photos' columns
    clean_df = df.drop(df.columns[df.columns.str.contains(re_str)], axis=1)
    clean_df = clean_df.drop(df.columns[df.columns.str.contains("address/community")], axis=1) # drop empty column
    return clean_df

def cleaning(name):
    """
    Cleans the dataframe specifically for the visualizations -- this includes removing outliers, rounding data, and adjusting the sqft for better graphics
    Args: name -- a city to be used for the geographic visualization, str
          
    Returns: A new dataframe
    """
    df = pd.read_csv(f"Datasets/{name}.csv") #Reads the data
    df = df[(np.abs(stats.zscore(df["price"])) <3)] #removes outliers
    df["bathrooms"] = df["bathrooms"].round() #rounds bathrooms for some badly entered data
    #Removes a few datapoints that greatly skew the data
    df = df[df["bathrooms"] < 30] 
    df = df[df["bedrooms"] < 30]
    df = df[df["livingArea"] < 25000]
    df["livingArea"] = round(df["livingArea"] / 500.0) *500 #Rounds sqft
    return df #returns the dataframe

def getStats(name):
    '''
    Returns dictionary of statistics for a city to use as default values for the visualization page
    
    Args: name -- the name of the city of interests, str
    returns: A dictonary 
    '''

    # get data frame for given city
    df = pd.read_csv(f"Datasets/{name}.csv")

    # get mode values
    modes = df[['address/zipcode', 'homeType', 'bathrooms', 'bedrooms', 'yearBuilt', 'livingArea']].mode()
    mode_zipcode = modes.iloc[0]['address/zipcode']
    mode_home_type = modes.iloc[0]['homeType']
    mode_bath = modes.iloc[0]['bathrooms']
    mode_bed = modes.iloc[0]['bedrooms']
    mode_year = modes.iloc[0]['yearBuilt']
    mode_area = modes.iloc[0]['livingArea']

    # return dictionary
    return {
        "zipcode": int(mode_zipcode),
        "home_type": mode_home_type,
        "bath": int(mode_bath),
        "bed": int(mode_bed),
        "year_made": int(mode_year),
        "sqft": int(mode_area)  
    }