import os
import folium
import geopandas as gpd
import pandas as pd
import panel as pn
from legend import climate_map_legend
from color_map import Color_map
from performance import performance_filter
import shapely
from shapely.geometry import Point

def create_map(koppen_giger_data_path: str, color_map):
    # Load the shapefile with geodata for the climate zones into a GeoDataFrame
    koppen_giger_data = gpd.read_file(koppen_giger_data_path)

    # Load the CSV which contains the additional data (CostsToCapture and EnergyRequirements)
    additional_data = pd.read_csv('files/csv/alpha1.csv')
    additional_data['CostsToCapture'] = additional_data['CostsToCapture'].str.extract(r'(\d+(\.\d+)?)')[0].astype(float)
    additional_data['EnergyRequirements'] = additional_data['EnergyRequirements'].str.extract(r'(\d+(\.\d+)?)')[0].astype(float)

    # Create a GeoDataFrame for the additional data with Lat, Long columns
    additional_data['geometry'] = additional_data.apply(
        lambda row: Point(row['Long'], row['Lat']), axis=1
    )
    additional_data_gdf = gpd.GeoDataFrame(additional_data, geometry='geometry', crs="EPSG:4326")

    # Make the shapefile in the same format as the additional one
    koppen_giger_data = koppen_giger_data.to_crs(epsg=4326)

    # Spatial join to combine the two datasets (additional and koppen)
    joined_data = gpd.sjoin(koppen_giger_data, additional_data_gdf, how="left", predicate='intersects')

    # Map GRIDCODES to colors
    joined_data['color'] = joined_data['GRIDCODE'].map(lambda x: color_map.get(x, ('gray', 'Unknown'))[0])
    joined_data['description'] = joined_data['GRIDCODE'].map(lambda x: color_map.get(x, ('gray', 'Unknown'))[1])

    # range data calculationg the ranges for CostsToCapture and EnergyRequirements
    range_data = joined_data.groupby('GRIDCODE').agg({
        'CostsToCapture': lambda x: f"{x.min()} - {x.max()} €/ton",
        'EnergyRequirements': lambda x: f"{x.min()} - {x.max()} kWh/ton"
    }).reset_index()

    # Merge the range_data data back into the joined data
    joined_data = joined_data.merge(range_data, on='GRIDCODE', suffixes=('', '_range'))
    
    # Creates a centered folium map
    m = folium.Map(location=(30, 10), zoom_start=3, tiles="cartodb positron")

    # Creates a feature group for the climate zone which makes removing
    # the layer with the colors possible
    climate_zones_fg = folium.FeatureGroup(name="Climate Zones", show=True)

    # Adds features to the climate zones (pop ups, colors)
    for _, row in joined_data.iterrows():
        geojson_feature = {
            'type': 'Feature',
            'geometry': row['geometry'].__geo_interface__,
            'properties': {
                'description': row['description'],
                'GRIDCODE': row['GRIDCODE'],
                'CostsToCapture_range': row['CostsToCapture_range'],
                'EnergyRequirements_range': row['EnergyRequirements_range']
            }
        }

        fields = ['description', 'CostsToCapture_range', 'EnergyRequirements_range']
        aliases = ['Climate Zone:', 'Costs to Capture (Range):', 'Energy Requirements (Range):']
  
        folium.GeoJson(
            geojson_feature,
            style_function=lambda x, color=row['color']: {
                'fillColor': color,
                'color': 'black',
                'weight': 0.5,
                'fillOpacity': 0.6,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=fields,
                aliases=aliases,
                localize=True,
                sticky=True,
                labels=True,
                style="font-size: 12px; color: black;"
            )
        ).add_to(climate_zones_fg)

    # Adds the feature group with the climate zones colors to the folium map
    climate_zones_fg.add_to(m)

    # Adds the layer control on the top right corner
    folium.LayerControl().add_to(m)

    # Adds the legend to the map
    legend = climate_map_legend()
    m.get_root().html.add_child(folium.Element(legend))

    return m


class ClimateMap(pn.viewable.Viewer):
    def __init__(self, koppen_giger_data_path: str, color_map=None, map=None, map_pane=None, **params):
        super().__init__(**params)
        self.path = os.path.abspath(koppen_giger_data_path)
        self.original_color_map = color_map if color_map else Color_map()
        self.color_map = self.original_color_map  

        # If the map and map_pane variables are not set, create new ones
        if map and map_pane:
            self.map = map
            self.map_pane = map_pane
        else:
            self.map = create_map(self.path, self.color_map)
            self.map_pane = pn.pane.HTML(self.map._repr_html_())

        self._layout = pn.Column(self.map_pane)

        self.koppen_giger_data = gpd.read_file(self.path)

        # Add color and description columns based on GRIDCODE
        self.koppen_giger_data['color'] = self.koppen_giger_data['GRIDCODE'].map(
            lambda x: self.color_map.get(x, ('gray', 'Unknown'))[0]
        )
        self.koppen_giger_data['description'] = self.koppen_giger_data['GRIDCODE'].map(
            lambda x: self.color_map.get(x, ('gray', 'Unknown'))[1]
        )

    ### DEFINING FUNCTIONS FOR ACTIONS ###
    def get_climate_zone_for_coordinates(self, lat, lon):
        # When the lat and long are entered it finds the climate zone corresponding to 
        # these coordinates and adds the name of the zone and GRIDCODE to the koppen dataset

        # Creates a GeoDataFrame for the point
        point_gdf = gpd.GeoDataFrame(
            {'geometry': [Point(lon, lat)]}, 
            crs="EPSG:4326"
        )
        self.koppen_giger_data = self.koppen_giger_data.to_crs("EPSG:4326")

        # Performs a spatial join to find the containing polygon
        result = gpd.sjoin(point_gdf, self.koppen_giger_data, how="left", predicate="within")

        # Checks if a match was found
        if not result.empty:
            return {
                'description': result.iloc[0]['description'],
                'GRIDCODE': result.iloc[0]['GRIDCODE']
            }
        return None
    
    def add_marker(self, coordinates, update_display_callback=None):
        try:
            print(f"Received coordinates: {coordinates}") 
            if isinstance(coordinates, tuple):
                lat, lon = coordinates
            else:
                lat, lon = map(float, coordinates.split(','))

            print(f"Parsed coordinates: {lat}, {lon}")  

            # Finds the climate zone for the coordinates
            climate_info = self.get_climate_zone_for_coordinates(lat, lon)

            if climate_info:
                climate_description = climate_info['description']
                gridcode = climate_info['GRIDCODE']
                print(f"Climate Zone: {climate_description} (GRIDCODE: {gridcode})")
                
                # Adds a marker with climate zone information
                popup_html = f"""
                    <p>Marker at <br> ({lat}, {lon})</p>
                    <p><strong>Climate Zone:</strong> {climate_description} (GRIDCODE: {gridcode})</p>
                    <button onclick="">Delete Dot</button>
                """
                folium.Marker(location=(lat, lon), popup=folium.Popup(popup_html, max_width=300)).add_to(self.map)
            else:
                print("Coordinates are outside the defined climate zones.")
                popup_html = f"""
                    <p>Marker at <br> ({lat}, {lon})</p>
                    <p><strong>Climate Zone:</strong> Not Found</p>
                """
                folium.Marker(location=(lat, lon), popup=folium.Popup(popup_html, max_width=300)).add_to(self.map)
            
            # Refresh map HTML
            self.map_pane.object = self.map._repr_html_()
            self._layout[0] = self.map_pane 

            print("Map HTML updated")  
            if update_display_callback:
                update_display_callback(f"{lat}, {lon}")
        except ValueError:
            print("Invalid coordinates. Ensure the format is 'latitude, longitude'")
    

    def apply_performance_filter(self, selected_performance):
        # Apply the performance filter based on the selected machine performance (best to worst)
        # from the dropdown menu

        if selected_performance == 'Choose performance':
            # default = full coloring
            self.reset_to_full_color_map()
        else:
            filtered_color_map = performance_filter(self.color_map, selected_performance)
            self.update_map_colors(filtered_color_map)

    def update_map_colors(self, color_map):
       # Updates the map with the new coloring
        self.color_map = color_map
        self.map = create_map(self.path, self.color_map)  
        self.map_pane.object = self.map._repr_html_()
        self._layout[0] = self.map_pane 

    def reset_to_full_color_map(self):
       # Resets the map with the fyll coloring
        self.color_map = self.original_color_map  
        self.update_map_colors(self.color_map)  
    


    
    def __panel__(self):
        return self._layout
