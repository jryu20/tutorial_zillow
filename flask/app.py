from flask import Flask, render_template, g, request
import pandas as pd
import plotly
from plotly import express as px
import sqlite3
import os
import json
import numpy as np
from scipy import stats
from flask import Flask, session
import plotly.express.colors
import pickle
from myGraphs import *
from dataCleaning import * 

app = Flask(__name__)
app.secret_key = "super secret key"

@app.route('/')
def main():
    #Renders the base template 
    return render_template('base.html')  

@app.route('/data_collection', methods=['POST', 'GET'])
def data_collection():
    '''
    Renders template for data collection
    Uses model to predict house price from user input
    
    Args: None 
    Returns: Rendered_template
    '''

    if request.method == 'GET': #checks if the method is GET
        city = request.args.get('city') #gets selected city 
        return render_template('data_collection.html', city=city,
                               prediction = False)
    else: #checks if the method is POST
        city = request.args.get('city') #gets city
        bed=request.form["bed"] #gets bed 
        session['bed_info'] = bed #saves bed
        bath=request.form["bath"] #gets bath 
        session['bath_info'] = bath #saves bath
        sqft=request.form["sqft"] #gets sqft
        session['sqft_info'] = sqft #saves sqft
        year_made=request.form["year_made"] 
        home_type = request.form['home_type']
        zipcode = str(request.form["zipcode"])
        
        with open('Model/model1.pkl', 'rb') as f:
            model = pickle.load(f) #Loads the model for prediction
        
        price = model.predict(pd.DataFrame({ #Predicted the house price using zipcode, bed count, and bath count
            'address/zipcode': [zipcode],
            'bathrooms': [bed],
            'bedrooms': [bath]
        }))

        return render_template('data_collection.html', city = city, #renders the template with the predicted price
                               prediction = True,
                               price = int(price[0]),
                               bed=bed, bath=bath, sqft=sqft,
                               year_made=year_made,
                               home_type=home_type,
                               zipcode=zipcode)


@app.route('/morevisualization')
def morevisualization():
    '''
    renders template for data visualization page which includes creating all 9 graphics 
    
    Args: none 
    Returns: A rendered template using all 9 graphics
    '''
    # set default values if user didn't submit anything
    city = session.get('city_info') #gets city 
    default = getStats(city) #Calls getStats to get the default values
    bed = session.get('bed_info') if session.get('bed_info') else default['bed']
    bath = session.get('bath_info') if session.get('bath_info') else default['bath']
    sqft = session.get('sqft_info') if session.get('sqft_info') else default['sqft']
    
    # create histograms using user info
    graph1 = histogram_count(name =session.get('city_info'), feature = "bedrooms", user_info = bed, color = ['indianred'])
    graph2 = histogram_count(name =session.get('city_info'), feature = "bathrooms", user_info =  bath, color = ["#4083f7"])
    graph3 = histogram_count(name =session.get('city_info'), feature = "livingArea", user_info =  sqft, color = ['#42c947'])
    graph4 = histogram_price(name =session.get('city_info'), feature = "bedrooms", user_info =  bed, color = ["indianred"])
    graph5 = histogram_price(name =session.get('city_info'), feature = "bathrooms", user_info =  bath, color = ["#4083f7"])
    graph6 = histogram_price(name =session.get('city_info'), feature = "livingArea", user_info =  sqft, color = ['#42c947'])
    
    # create scatterplots using user info
    graph7 = scatterplot_count(name=session.get('city_info'), feature1 = "bedrooms", feature2 = "bathrooms", user_info = [bed, bath])
    graph8 = scatterplot_count(name=session.get('city_info'), feature1 = "bedrooms", feature2 = "livingArea", user_info = [bed, sqft])
    graph9 = scatterplot_count(name=session.get('city_info'), feature1 = "bathrooms", feature2 = "livingArea", user_info = [bath, sqft])
    #Returns rendered template with the graphs
    return render_template('morevisualization.html', city = session.get('city_info'), graph1 = graph1, graph2 = graph2, graph3 = graph3, graph4=graph4, graph5=graph5, graph6=graph6, graph7=graph7, graph8=graph8, graph9=graph9)

@app.route('/visualization', methods=['GET', 'POST'])
def visualization():
    '''
    renders template for geographic visualization page with the scatter mapbox and heat mapbox while also using user filter 
    
    Args: none 
    Returns: A rendered template using both graphics
    '''
    city = request.args.get('city')
    session['city_info'] = city
    if request.method == 'POST':
        min = request.form.get("minimum") #Gets user entered filter for minimum 
        max = request.form.get('maximum') #Gets user entered filter for maximum
        feature_min_max = request.form.get("features_min_max") #Gets user tentered filter feature
        style = request.form.get("style") #Gets user mapbox theme
        print(style)
        feature_type = []
        #Adds user entered filter housing type to a list for dataframe subsettiong
        if request.form.get("apartment"):
            feature_type.append(request.form.get("apartment"))
        if request.form.get("condo"):
            feature_type.append(request.form.get("condo"))
        if request.form.get("lot"):
            feature_type.append(request.form.get("lot"))
        if request.form.get("multi_family"):
            feature_type.append(request.form.get("multi_family"))
        if request.form.get("townhouse"):
            feature_type.append(request.form.get("townhouse"))
        feature = request.form.get("features") #Gets the features
        number = request.form.get("number") 
        city = request.args.get('city') #Gets the city 
        #Creates the scatter mapbox with the filters/features the user entered by passing the info to mapbox()
        graph1 = mapbox(city, feature=feature, number=number,
                        feature_type=feature_type,
                        feature_min_max=feature_min_max,
                        min=min, max=max, style=style)
        #Creates the heat mapbox with the filters/features the user entered by passing the info to density_mapbox()
        graph2 = density_mapbox(city, feature=feature, number=number,
                        feature_type=feature_type,
                        feature_min_max=feature_min_max,
                        min=min, max=max, style=style)
        #Renders the template
        return render_template('visualization.html', city=city, graph1 = graph1,
                               graph2=graph2)
    else:
        #If the method is "GET", all data before filters will be loaded for the graphics
        city = request.args.get('city')
        graph1 = mapbox(city)
        graph2 = density_mapbox(city)
        return render_template('visualization.html', city=city, graph1 = graph1,
                               graph2=graph2)

@app.route('/view_data', methods=['GET','POST'])
def view_data():
    '''
    This function will display the dataset of a selected city
    Args: None 
    Returns: an html-rendered table that contains all data of a particular city
    '''
    city = session.get('city_info') #Gets the city name 
    if request.method == 'POST':
        city = request.form["name"]
        data = pd.read_csv(f"Datasets/{city}.csv") #Reads the data 
        clean_data = clean(data) #Cleans the data
        pd.set_option('display.max_colwidth', 10)
        return render_template('view_data.html', tables=[clean_data.to_html()], titles=[''], city=city) #Renders the template 
    else: 
        data = pd.read_csv(f"Datasets/{city}.csv") # reads the data
        clean_data = clean(data) #cleans the data 
        return render_template('view_data.html', tables=[clean_data.to_html()], titles=[''], city=city) #Renderss the template 
