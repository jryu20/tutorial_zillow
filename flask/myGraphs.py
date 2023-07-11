import pandas as pd
import plotly
from plotly import express as px
import sqlite3
import os
import json
import numpy as np
from scipy import stats
import plotly.express.colors
from dataCleaning import *

def mapbox(name, **kwargs):
    """
    Creates a mapbox of all the data points scraped for the name (city name) parameter
    
    Args: name -- a city to be used for the geographic visualization,str
          **kwargs -- other parameters to filter the data to update the visualization
          
    Returns: A json with the mapbox figure
    """

    df = pd.read_csv(f"Datasets/{name}.csv") #Reads the data 
    center = {'lat': np.mean(df['latitude']), 'lon': np.mean(df['longitude'][0])} #Finds the center of the map

    for key, value in kwargs.items():
        if(key == "feature"):
            feature = value
        if(key == "number"):
            num = value
            if num != '':
                num = int(num)
                df = df[df[feature] == num] #Filters the data for specific features having a set value. Ex Bathrooms = 2 or Bedrooms = 3
        if(key == "feature_type"):
            feature_type = value
            if feature_type != []:
                df = df[df["homeType"].isin(feature_type)] #Filters the data to only include specific home types
        if(key == "feature_min_max"):
            feature_min_max = value
        if(key == "min"):
            minimum = value
            if minimum != '':
                minimum = int(minimum)
                df = df[df[feature_min_max] >= minimum] #Filters the data for specific features having a set minimum value. Ex Min Price = 100k or Min Sqft = 2000
        if(key == "max"):
            maximum = value
            print(maximum, feature_min_max)
            if maximum != '':
                maximum = int(maximum)
                df = df[df[feature_min_max] <= maximum]  #Filters the data for specific features having a set max value. Ex Max Price = 250k or Max Year Built = 2010
    #Creates plotly scatter mapbox using data with/without added filters
    fig = px.scatter_mapbox(df,
                            center = center, 
                            hover_data = ["address/city","price", 'bathrooms', 'bedrooms',
                                          'homeType'],
                            lat = "latitude",
                            lon = "longitude", 
                            zoom = 8,
                            height = 600,
                            mapbox_style=kwargs.pop("style", "open-street-map"))
    fig.update_layout(margin={"r":30,"t":10,"l":30,"b":0}) #sets the margin
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder) #returns the json

def density_mapbox(name, **kwargs):
    """
    Creates a heat mapbox of all the data points scraped for the name (city name) parameter
    Args: name -- a city to be used for the geographic visualization,str
          **kwargs -- other parameters to filter the data to update the visualization
          
    Returns: A json with the heat mapbox figure
    """

    df = pd.read_csv(f"Datasets/{name}.csv")  #Reads the data 
    sample_size = df.shape[0] #Gets number of observations
    center = {'lat': np.mean(df['latitude']), 'lon': np.mean(df['longitude'][0])} #Finds the center of the map


    for key, value in kwargs.items():
        if(key == "feature"):
            feature = value
        if(key == "number"):
            num = value
            if num != '':
                num = int(num)
                df = df[df[feature] == num]  #Filters the data for specific features having a set value. Ex Bathrooms = 2 or Bedrooms = 3
        if(key == "feature_type"):
            feature_type = value
            if feature_type != []:
                df = df[df["homeType"].isin(feature_type)] #Filters the data to only include specific home types
        if(key == "feature_min_max"):
            feature_min_max = value
        if(key == "min"):
            minimum = value
            if minimum != '':
                minimum = int(minimum)
                df = df[df[feature_min_max] >= minimum] #Filters the data for specific features having a set minimum value. Ex Min Price = 100k or Min Sqft = 2000
        if(key == "max"):
            maximum = value
            print(maximum, feature_min_max)
            if maximum != '':
                maximum = int(maximum)
                df = df[df[feature_min_max] <= maximum]#Filters the data for specific features having a set max value. Ex Max Price = 250k or Max Year Built = 2010
 

    
    if df.shape[0] != 0:
        radius = 5 * int(np.log2((sample_size + df.shape[0]) / df.shape[0])) # Adjusts the radius parameter of the heatmap as the number of points ploted changes with added filters
        if radius < 1:
            radius = 1
    else:
        radius = 1
    #Creates plotly scatter heat mapbox using data with/without added filters
    fig = px.density_mapbox(df, 
                            center = center,
                            hover_data = ["address/city","price", 'bathrooms', 'bedrooms'],
                            lat = "latitude",
                            lon = "longitude", 
                            zoom = 8,
                            radius = radius,
                            height = 600,
                            mapbox_style=kwargs.pop("style", "open-street-map"))

    fig.update_layout(margin={"r":30,"t":10,"l":30,"b":0})
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder) #returns the json

def histogram_count(name, feature, user_info, color):
    """
    Creates the count histograms vs a feature and returns a json
    Args: name -- a city to be used for the geographic visualization, str
          feature -- a column of the dataframe to be visualized, str
          user_info -- a variable of the user entered information 
          color -- a color for the visualization, str
          
    Returns: A json of the visualization
    """
    df = cleaning(name) #Cleans the dataframe
    highest_value = 450 # marker height for the user entered data 
    fig = px.histogram(df, x=feature, width = 500, color_discrete_sequence=color) #Creates the histogram using the feature and color 
    fig.add_shape(type="line",x0=user_info, y0=0, x1=user_info, y1=highest_value,line=dict(color="red", width=3, dash="dash")) #Adds a dotted line marker 
    fig.add_annotation(x=user_info, y=highest_value, ax=0, ay=-40,text="Your Data",arrowhead=1, arrowwidth=3, showarrow=True) #Adds a comment "your data" above the marker
    fig.update_traces(marker_line_color="black", marker_line_width=1, opacity=0.7) #Adjusts the figure and marker appearence 
    if feature == "livingArea":
        fig.update_layout(title={"text": "Square Footage ", "x": 0.5}, yaxis_title="Count") #Renames the axis 
    else: 
        fig.update_layout(title={"text": "Number of " + feature, "x": 0.5}, yaxis_title="Count") #Renames the axis 
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder) #returns the json



def histogram_price(name, feature, user_info, color):
    """
    Creates the histograms for median price vs a feature and returns a json
    Args: name -- a city to be used for the geographic visualization, str
          feature -- a column of the dataframe to be visualized, str
          user_info -- a variable of the user entered information 
          color -- a color for the visualization, str
          
    Returns: A json of the visualization
    """
    df = cleaning(name) #Cleans the dataframe 
    median_price = df[[feature,"price"]].groupby(feature).median().round(0) #Gets the median price into grouped bins for the selected feature and saves it into a dataframe
    highest_value = int(median_price.max()) #Sets the marker height 
    fig = px.histogram(median_price, width =500, x=median_price.index, y="price", nbins =30, color_discrete_sequence=color) #Creates the histogram using the median price dataframe 
    fig.add_shape(type="line", x0=user_info, y0=0, x1=user_info, y1=highest_value, line=dict(color="red", width=3, dash="dash"))#Adds a marker for the user data
    fig.add_annotation(x=user_info, y=highest_value, ax=0, ay=-40,text="Your Data",arrowhead=1, arrowwidth=3, showarrow=True)# #Adds a comment "Your Data" above the marker
    fig.update_traces(marker_line_color="black", marker_line_width=1, opacity=0.7)  #Adjusts the figure and marker appearence
    if feature == "livingArea":
        fig.update_layout(title={"text": "Median Price of Homes vs Square Footage" , "x": 0.5}, yaxis_title="Price") #Changes plot title 
    else:
        fig.update_layout(title={"text": "Median Price of Homes vs " + feature, "x": 0.5}, yaxis_title="Price") #Changes plot title
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder) #Returns json 


def scatterplot_count(name, feature1, feature2, user_info):
    """
    Creates count scatterplot with a pair of features and user info
    Args: name -- a city to be used for the geographic visualization, str
          feature -- a column of the dataframe to be visualized, str
          user_info -- a variable of the user entered information 
          color -- a color for the visualization, str
          
    Returns: A json of the visualization
    """
    df = cleaning(name) #Cleans the dataframe 
    offset = 1 #Adds an offset for the circle marker 
    scatter_1 = df.groupby([feature1, feature2]).size().reset_index().rename(columns={0:'count'}) #Gets the number of each pair of features present in the dataframe
    fig = px.scatter(scatter_1, x = feature1, y = feature2, color = "count", color_continuous_scale=px.colors.sequential.Plotly3_r, range_color = [1,100], width = 500) #Creates the scatterplot with the features
    if feature2 == "livingArea":
        offset = 550 #Changes the offset if living room is a feature used 
        fig.update_layout(title={"text": "Amount of " + feature1 + " vs Square Footage", "x": 0.5}) #Changes title 
        fig.add_shape(type="circle",x0=int(user_info[0])-1, x1=int(user_info[0])+1, y0 = int(user_info[1])-offset, y1 = int(user_info[1])+offset) #adds circle marker
    else: 
        fig.add_shape(type="circle",x0=int(user_info[0])-1, x1=int(user_info[0])+1, y0 = int(user_info[1])-offset, y1 = int(user_info[1])+offset) #adds circle marker
        fig.update_layout(title={"text": "Amount of " + feature1 + " vs Amount of " + feature2, "x": 0.5}) #Changes title
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder) #returns json