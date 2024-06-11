import streamlit as st
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from pyproj import Transformer
from pyproj import CRS 
import geopandas as gpd
import matplotlib.pyplot as plt
import openpyxl
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Michigan House Districts and Voting Precincts Maps",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title(':blue[Michigan House Districts and Voting Precincts Maps]')
st.subheader(':blue[Based Upon the Motown Sound FC E1 Michigan State House Districts]')

# shapefile_path = "2022_Voting_Precincts.shp"
# gdf1 = gpd.read_file(shapefile_path)

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

# df = gpd.overlay(gdf1, gdf, how='intersection')

# # Ensure 'geometry' column is retained as 'geometry_left' and 'geometry_right' for precincts and districts respectively
# df['intersection_area'] = df.apply(lambda row: row['geometry'].area, axis=1)

# # For each precinct, keep the row with the largest intersection area
# df_resolved = df.loc[df.groupby('PRECINCTID')['intersection_area'].idxmax()]

# # Sort the DataFrame alphabetically by Precinct_L
# df_sorted = df_resolved.sort_values(by='Precinct_L').reset_index(drop=True)

#shapefile_path = "gdf1.shp"
shapefile_path = "gdf1v2.shp"
gdf1 = gpd.read_file(shapefile_path)

# Filter out warnings (optional)
st.set_option('deprecation.showPyplotGlobalUse', False)

#df_sorted["color"] = "#514585"
gdf1["color"] = "#514585"

import plotly.express as px

# Define initial figures
fig = px.choropleth_mapbox(gdf1, 
                            geojson=gdf1.geometry.__geo_interface__,
                            locations=gdf1.index,
                            mapbox_style="carto-positron",
                            zoom=5,
                            color=gdf1['color'],
                            color_discrete_map={'#514585':'#6F2A3B'},
                            hover_name="Precinct_L", 
                            hover_data=["Precinct_L", "DISTRICTNO", "PRECINCTID"],
                            center={"lat": gdf1.centroid.y.mean(), "lon": gdf1.centroid.x.mean()},
                            opacity=0.5,
                           )


# Update hoverinfo for the combined figure
fig.update_traces(selector=dict(type='choropleth'), hoverinfo='skip')

# Define JavaScript for click event
click_script = """
selected_points = fig.data[0].selectedpoints;
new_color = ['#636efa'] * len(fig.data[0].z); // Default color for all districts
if (selected_points.length > 0) {
    selected_points.forEach(function(point) {
        new_color[point] = '#ef553b'; // Change color upon click
    });
}
fig.data[0].marker.color = new_color;
"""

fig.update_layout(
    clickmode='event+select',
    mapbox={
        "layers": [
            {
                "source": gdf["geometry"].__geo_interface__,
                "type": "line",
                "color": "black"
            }
        ]
    },
)

fig.update_traces(
    hovertemplate="<b>Precinct Name: %{customdata[0]}</b><br>State House District: %{customdata[1]}<br>Precinct ID: %{customdata[2]}<extra></extra>"
)

fig.update_layout(
    autosize=False,
    height=900,
    margin=dict(
        l=50,
        r=50,
        b=50,
        t=50,
        pad=4
    ),    paper_bgcolor="LightSteelBlue",
)

fig.update_layout(showlegend=False)

# Define tabs
tabs = ["Map", "Excel Data"]
active_tab = st.sidebar.radio("Select Tab", tabs)

# Render Plot tab
if active_tab == "Map":
    st.plotly_chart(fig, use_container_width=True, height=1200)
# Render Data tab
elif active_tab == "Excel Data":
    df = pd.read_excel("gdf1.xlsx")
    st.dataframe(df, width=1000, height=800)

