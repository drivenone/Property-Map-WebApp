# Import necessary libraries
import os
import json
import time
from functools import cache
from wsgiref import headers
import requests
import numpy as np
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from flask import Flask, render_template

# Initialize Flask app
app = Flask(__name__)

# Load property data from CSV file
df = pd.read_csv('zillow_memphistn.csv')

@app.route('/')
def index():
    # Check if the map HTML file already exists
    if os.path.exists('templates/properties_map.html'):
        return render_template('properties_map.html')
    else:
        # Data preprocessing
        df  = df.dropna(subset=['latitude', 'longitude'])
        
        # Convert columns to numeric type
        df['rentZestimate'] = pd.to_numeric(df['rentZestimate'], errors='coerce')
        df['zestimate'] = pd.to_numeric(df['zestimate'], errors='coerce')
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        
        # Calculate annual rent and gross rental yield
        df['annual_rent'] = df['rentZestimate'] * 12
        df['gross_rental_yield'] = (df['annual_rent'] / df['zestimate']) * 100
        
        # Replace infinite values with NaN
        df['gross_rental_yield'] = df['gross_rental_yield'].replace([np.inf, -np.inf], np.nan)
        
        # Function to determine marker color based on gross yield and market status
        def get_marker_color(gross_yield, off_market):
            if off_market:
                return 'black'
            elif pd.isna(gross_yield):
                return 'gray'
            elif gross_yield < 5:
                return 'red'
            elif gross_yield < 8:
                return 'orange'
            else:
                return 'green'
        
        # Calculate map center
        map_center = [df['latitude'].mean(), df['longitude'].mean()]
        
        # Create the map
        m = folium.Map(location=map_center, zoom_start=13)
        
        # Create a marker cluster
        marker_cluster = MarkerCluster().add_to(m)
        
        # Add markers for each property
        for idx, row in df.iterrows():
            # Extract property details
            price = row['price']
            address = row['address']
            bedrooms = row['bedrooms']
            bathrooms = row['bathrooms']
            living_area = row['livingArea']
            gross_yield = row['gross_rental_yield']
            zestimate = row['zestimate']
            rent_zestimate = row['rentZestimate']
            property_url = row['url']
            zpid = row['zpid']
            
            # Format property details
            if not pd.isna(price):
                price_formatted = f"${price:.2f}"
            else:
                price_formatted = 'N/A'
                
            if not pd.isna(zestimate):
                zestimate_formatted = f"${zestimate:.2f}"
            else:
                zestimate_formatted = 'N/A'
                
            if not pd.isna(rent_zestimate):
                rent_zestimate_formatted = f"${rent_zestimate:.2f}"
            else:
                rent_zestimate_formatted = 'N/A'
                
            if not pd.isna(gross_yield):
                gross_yield_formatted = f"%{gross_yield:.2f}"
            else:
                gross_yield_formatted = 'N/A'
            
            bedrooms = int(bedrooms) if not pd.isna(bedrooms) else 'N/A'
            bathrooms = int(bathrooms) if not pd.isna(bathrooms) else 'N/A'
            living_area = int(living_area) if not pd.isna(living_area) else 'N/A'
            
            # Extract street address from JSON-formatted address
            address_dict = json.loads(address)
            street_address = address_dict['streetAddress']
            
            # Create popup content
            popup_text = f"""
            <b>Address:</b> {street_address}<br>
            <b>Price:</b> {price_formatted}<br>
            <b>Bedrooms:</b> {bedrooms}<br>
            <b>Bathrooms:</b> {bathrooms}<br>
            <b>Living Area:</b> {living_area}<br>
            <b>Gross Rental Yield:</b> {gross_yield_formatted}<br>
            <b>Zestimate:</b> {zestimate_formatted}<br>
            <b>Rental Zestimate:</b> {rent_zestimate_formatted}<br>
            <a href="{property_url}" target="_blank">View Property</a><br>
            <button id="button-{idx}" onclick="showLoadingandRedirect({idx}, '{zpid}')">Show Price History</button>
            <div id="loading-{idx}" style="display: none;">
                <img src="https://upload.wikimedia.org/wikipedia/commons/3/3a/Gray_circles_rotate.gif" alt="Loading..." width="50" height="50">
            </div>
            
            <script>
                function showLoadingandRedirect(idx, zpid) {{
                    document.getElementById('button-' + {idx}).style.display = "none";
                    document.getElementById('loading-' + {idx}).style.display = "block";
                    window.location.href = 'http://localhost:5000/price_history/' + zpid;
                }}
            </script>
            """
            
            # Determine marker color
            color = get_marker_color(row['gross_rental_yield'], row['isoff_market'])
            
            # Create and add marker to the cluster
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=folium.Popup(folium.IFrame(popup_text, width=400, height=300)),
                icon=folium.Icon(color=color, icon='home', prefix='fa')
            ).add_to(marker_cluster)
            
        # Save the map as an HTML file
        m.save('templates/properties_map.html')
        
        return render_template('properties_map.html')

@app.route('/price_history/<int:zpid>')
@cache
def price_history(zpid):
    # Get property URL from DataFrame
    url = df[df.zpid == zpid]['url'].values[0]
    api_url = "https://api.brightdata.com/datasets/v3/trigger?dataset_id=gd_lxu1cz9r88uiqsosl"
    
    # Read API token from file
    TOKEN = open('TOKEN', 'r').read()
    
    # Set up headers for API request
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": 'application/json'
    }
    
    # Prepare data for API request
    data = [{'url': url}]
    
    # Send POST request to trigger data collection
    response = requests.post(api_url, headers=headers, json=data)
    snapshot_id = response.json()['snapshot_id']
    
    # Wait for 5 seconds
    time.sleep(5)
    
    # Prepare URL for getting the snapshot data
    api_url = f"https://api.brightdata.com/datasets/v3/snapshots/{snapshot_id}?format=csv"
    
    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }
    
    # Send GET request to retrieve snapshot data
    response = requests.get(api_url, headers=headers)
    
    # Check if snapshot is empty
    if 'Snapshot is empty' in response.text:
        return 'No historic data available'
    
    # Wait for snapshot to be ready
    while 'Snapshot is not ready yet, try again in 10s' in response.text:
        time.sleep(10)
        response = requests.get(api_url, headers=headers)
        if 'Snapshot is empty' in response.text:
            return 'No historic data available'
        
    # Save snapshot data to a temporary CSV file
    with open('temp.csv', 'wb') as f:
        f.write(response.content)
        
    # Process price history data
    price_history_df = pd.read_csv('temp.csv')
    price_history_df = price_history_df[['date', 'price']]
    price_history_df['date'] = pd.to_datetime(price_history_df['date'])
    price_history_df = price_history_df['date'].dt.strftime('%Y-%m-%d')
    
    # Render price history template
    return render_template('price_history.html', price_history_df=price_history_df)

# Run the Flask app in debug mode
if __name__ == '__main__':
    app.run(debug=True)