import streamlit as st
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd

# Load your data (assuming gdf1 and gdf are loaded DataFrames)
# Replace this with your actual data loading code
# gdf1 = pd.read_csv("path_to_your_data_file1.csv")
# gdf = pd.read_csv("path_to_your_data_file2.csv")

# Filter out warnings (optional)
st.set_option('deprecation.showPyplotGlobalUse', False)

# Your first choropleth map code
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

# Create the figure
fig = go.Figure()

# Add traces to the figure
for data in fig1.data:
    fig.add_trace(data)

for data in fig2.data:
    data['subplot'] = 'mapbox2'
    fig.add_trace(data)

# Define layout for the plot
layout = go.Layout(
    autosize=True,
    hovermode='closest',
    mapbox=dict(
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

# Update the layout
fig.update_layout(layout)

# Display the plot using Streamlit
st.plotly_chart(fig)
