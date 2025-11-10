import panel as pn
import pandas as pd
from geopy.distance import geodesic


class Filters(pn.viewable.Viewer):
    def __init__(self, map, map_pane, **params):
        super().__init__(**params)
        
        # Pass the map and map_pane
        self.map = map
        self.map_pane = map_pane
 
        # Dropdowns
        self.overview_dropdown=pn.widgets.Select(
            name='Change overview',
            options=['€ / ton CO₂', 'kWh / ton'],
            value='€ / ton CO₂',
            styles={
                'width':'18%'
            }
            )
        
        self.machine_dropdown=pn.widgets.Select(
            name='Choose machine',
            options=['alpha1', 'alpha2'],
            value='alpha1',
            styles={
                'width':'18%'
            }
            )
        
        # Searchbar
        self.coordinates=pn.widgets.TextInput(
            name='Coordinates',
            placeholder="Latitude, Longitude",
            styles={
                'width':'21%'
            }
            )
        
        # Search button
        self.search_btn=pn.widgets.Button(
            name='SHOW ON MAP', icon='search',
            styles={
                'width':'10%',
            }
        )

        # Layout of the Row above the map with the filtering options and searchbar
        self._layout = pn.FlexBox(
            self.machine_dropdown,
            self.overview_dropdown,
            self.coordinates,
            self.search_btn,
            align_items="flex-end"

        )

        # Load the CSV file
        self.data = pd.read_csv('files/csv/alpha1.csv')

    def Search(self, add_marker_callback, update_display_callback):
        def handle_click(event):
            # gets coordiannates from the searchbar
            coordinates = self.coordinates.value.strip()
            print(f"Coordinates entered: '{coordinates}'")  

            # Checks if coordinates are empty
            if not coordinates:
                print("No coordinates provided. Please enter valid coordinates.")
                update_display_callback({"message": "No coordinates provided. Please enter valid coordinates."})
                return

            # Ensure the coordinates are in valid format (latitude, longitude)
            if ',' not in coordinates:
                print("Invalid format. Coordinates should be in 'latitude, longitude' format.")
                update_display_callback({"message": "Invalid format. Coordinates should be in 'latitude, longitude' format."})
                return

            
            pn.state.curdoc.add_next_tick_callback(lambda: self.process_coordinates(coordinates, add_marker_callback, update_display_callback))

        # Connect the button click event to the handler function
        self.search_btn.on_click(handle_click)

    def process_coordinates(self, coordinates, add_marker_callback, update_display_callback):
        try:
            # Parse the coordinates
            lat, lon = map(float, coordinates.split(','))
            print(f"Searching for: {lat}, {lon}")

            # Check if the coordinates are in the CSV
            match = self.data[(self.data['Lat'] == lat) & (self.data['Long'] == lon)]

            if not match.empty:
                location_details = match.iloc[0].to_dict()
                update_display_callback(location_details)
                add_marker_callback((lat, lon))
            else:
                # Finds the closest coordinates in the dataset
                searched_coords = (lat, lon)
                self.data['Distance'] = self.data.apply(
                    lambda row: geodesic(searched_coords, (row['Lat'], row['Long'])).kilometers, axis=1
                )
                closest_match = self.data.nsmallest(1, 'Distance').iloc[0]

                closest_coords = (closest_match['Lat'], closest_match['Long'])
                distance = closest_match['Distance']

                # Update display with the closest coordinates
                details = closest_match.to_dict()
                details['message'] = f"Coordinates not found in the dataset. \n\n Closest coordinates at {closest_coords[0]}, {closest_coords[1]} with distance {distance:.2f} km."
                
                update_display_callback(details)
                add_marker_callback((lat, lon))

        except ValueError:
            # Invalid coordinate format
            print("Invalid coordinates format. Ensure the format is 'latitude, longitude'.")
            update_display_callback({"message": "Invalid coordinates format. Ensure the format is 'latitude, longitude'."})


       

    # Expose the layout for rendering
    def __panel__(self):
        return self._layout