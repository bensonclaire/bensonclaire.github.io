import streamlit as st
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from pyproj import Transformer
from pyproj import CRS 
import geopandas as gpd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(layout="wide")

shapefile_path = "2022_Voting_Precincts.shp"
gdf1 = gpd.read_file(shapefile_path)

# Define the original CRS
original_crs = CRS("EPSG:3078")

# Define the target CRS (latitude and longitude)
target_crs = CRS("EPSG:4326")  # WGS84, which uses latitude and longitude

transformer = Transformer.from_crs(original_crs, target_crs, always_xy=True)

# Apply the transformation to each geometry
from shapely.ops import transform as shapely_transform

# Define a function to transform each coordinate pair
def transform_coordinates(x, y):
    lon, lat = transformer.transform(x, y)
    return lon, lat

# Apply the transformation to each geometry
gdf1['geometry'] = gdf1['geometry'].apply(lambda geom: shapely_transform(transform_coordinates, geom))

shapefile_path = "91b9440a853443918ad4c8dfdf52e495.shp"
gdf = gpd.read_file(shapefile_path)

gdf['DISTRICTNO'] = gdf['DISTRICTNO'].apply(lambda x: f"State House District {x}")

# Filter out warnings (optional)
st.set_option('deprecation.showPyplotGlobalUse', False)

fig1 = px.choropleth_mapbox(gdf1, 
                            geojson=gdf1.geometry.__geo_interface__,
                            locations=gdf1.index,
                            mapbox_style="carto-positron",
                            zoom=5,
                            hover_name="Precinct_L", 
                            hover_data=["PRECINCTID"],
                            center={"lat": gdf1.centroid.y.mean(), "lon": gdf1.centroid.x.mean()},
                            opacity=0.5,
                           )

# Extracting data from fig1
choropleth_data1 = list(fig1.data)  # Convert tuple to list

# Your second choropleth map code
fig2 = px.choropleth_mapbox(gdf, 
                            geojson=gdf.geometry.__geo_interface__,
                            locations=gdf.index,
                            mapbox_style="carto-positron",
                            zoom=5,
                            hover_name="DISTRICTNO", 
                            center={"lat": gdf.centroid.y.mean(), "lon": gdf.centroid.x.mean()},
                            opacity=0.5,
                           )

# Extracting data from fig2
choropleth_data2 = list(fig2.data)  # Convert tuple to list

# Define your Mapbox access token
mapbox_access_token = 'pk.eyJ1IjoiY2JlbnNvMTgyMiIsImEiOiJjbHdoenNleTcwMXljMmpwa25xb29mM2FvIn0.oUFcXxBLN4G4FIM2TG8mtg'

# Scattermapbox data
scattermapbox_data = [
    go.Scattermapbox(
    ),
    go.Scattermapbox(
    )
]

# Layout
layout = go.Layout(
    autosize=True,
    hovermode='closest',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        domain={'x': [0, 0.4], 'y': [0, 1]},
        bearing=0,
        center=dict(
            lat=gdf1.centroid.y.mean(),  # Center on first choropleth map's centroid
            lon=gdf1.centroid.x.mean()   # Center on first choropleth map's centroid
        ),
        pitch=0,
        zoom=5
    ),
    mapbox2=dict(
        accesstoken=mapbox_access_token,
        domain={'x': [0.6, 1.0], 'y': [0, 1]},
        bearing=0,
        center=dict(
            lat=gdf.centroid.y.mean(),  # Center on second choropleth map's centroid
            lon=gdf.centroid.x.mean()   # Center on second choropleth map's centroid
        ),
        pitch=0,
        zoom=5
    ),
)

# Create the figure
fig = go.Figure(data=scattermapbox_data + choropleth_data2 , layout=layout)

fig.update_layout(
    clickmode='event+select',
    mapbox={
        "layers": [
            {
                "source": gdf1["geometry"].__geo_interface__,  # Corrected source to gdf
                "type": "line",
                "color": "black"
            }
        ]
    },
)

fig.update_layout(
    clickmode='event+select',
    mapbox2={
        "layers": [
            {
                "source": gdf["geometry"].__geo_interface__,  # Corrected source to gdf
                "type": "line",
                "color": "black"
            }
        ]
    },
)

for trace in choropleth_data1:
    trace['subplot'] = 'mapbox2'
    fig.add_trace(trace)

click_script = """
selected_points = fig.data[0].selectedpoints;
new_color1 = ['#636efa'] * len(fig.data[0].z); // Default color for all districts on mapbox subplot
new_color2 = ['#636efa'] * len(fig.data[1].z); // Default color for all districts on mapbox2 subplot

if (selected_points.length > 0) {
    selected_points.forEach(function(point) {
        new_color1[point] = '#ef553b'; // Change color upon click for mapbox subplot
        new_color2[point] = '#ef553b'; // Change color upon click for mapbox2 subplot
    });

    // Synchronize selected points between subplots
    fig.data[1].selectedpoints = selected_points;
}

fig.data[0].marker.color = new_color1;
fig.data[1].marker.color = new_color2;
"""

fig.update_layout(clickmode='event+select')

# Display the plot using Streamlit
st.plotly_chart(fig, use_container_width=True,height=2000)

