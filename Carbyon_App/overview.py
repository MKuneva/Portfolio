import panel as pn
import pandas as pd
from map import ClimateMap
from filters import Filters
from performance import performance_filter
from color_map import Color_map
from nav_tabs import NavTabs

### STYLING ###

# Padding for the whole content
padding_style = {
    'padding': '20px',  
}

# Define individual styles for ID and Date
id_style = {
    'padding': '0',
    'margin': '0 !important',
    'line-height': '0',
    'height': '1vh',
    'position':'relative',
    'left':'0',
    'top':'0',
}

title = {
    'font-size': '1.5em',
    'margin': 'auto'
}
margin = {
    'margin-top': '2vh'
}
location_details={
    'height':'4vh',
    'font-size':'1.2em',
    'font-weight':'bold'
}


class Overview(pn.viewable.Viewer):
    def __init__(self,nav_tabs):
        super().__init__()

        # Initiate elements and variables
        self.nav_tabs=nav_tabs
        self._map=ClimateMap('files/2026-2050_A1FI_GIS/2026-2050-A1FI.shp')
        self._filters = Filters(map=self._map.map, map_pane=self._map.map_pane)
        self.color_map=Color_map()
        self._searchBtn = self._filters.Search(self._map.add_marker, self.update_display_input)
        self.displayInput=pn.pane.Markdown() 
        self.slider=pn.widgets.RangeSlider(name='Costs (€/ton)', format='0.0a', start=270, end=600)
        self.slider.styles = margin
        self.details_button = None 
        self.latest_coordinates = None

        # Read the CSV
        df = pd.read_csv('files/csv/alpha1.csv')

        # Adds values for date and id from the csv
        date = df['Date'][1]
        id_value = df['ID'][1]

        # performance dropdown options
        self.performance_dropdown=pn.widgets.Select(
            name='Performance',
            options=['Choose performance',
                'Best CO₂ Capture: Cost €277-€453/ton',
                'Good CO₂ Capture: Cost €281-€496/ton',
                'Moderate CO₂ Capture: Cost €327-€501/ton',
                'Worst CO₂ Capture: Cost €357-€568/ton'
                ],
            value='Choose performance'
            )
        
        # Update map on dropdown selection with callback
        self.performance_dropdown.param.watch(self.update_map, 'value')
        
        # Look for changes in overview_dropdown
        self._filters.overview_dropdown.param.watch(self.switch_dropdown_options, 'value')
        
        # Layout for the area right from the map
        self.details=pn.Column(
                    self.performance_dropdown,
                    self.slider,
                    pn.pane.Markdown("**Location Details:** ", styles=location_details),
                    self.displayInput
                    )

        ## SETTING THE PAGE LAYOUT ###

        # Creating a layout with the content with the padding around the whole content
        self._layout = pn.Column(

            # TITLE
            pn.Row(
                pn.pane.Markdown("# Location and Weather Sensitivity", styles=title),
                sizing_mode='stretch_width',  
                align='center',
                styles={'text-align': 'center'}  
            ),

            # ID and DATE
            pn.Column(
                pn.pane.Markdown(f"**ID:** {id_value}", styles=id_style),
                pn.pane.Markdown(f"**Date:** {date}", styles=id_style),
                styles={'width': 'fit-content', 'height': '1vh', 'margin-bottom':'50px',}
            ),

            # FILTERS row
            pn.Row(
                self._filters,
            ),

            # grid row with MAP (left) and DETAILS (right) 
            pn.Row( 
                self._map,
                self.details,
                styles={'display':'grid', 'grid-template-columns':'75% 25%','padding': '20px' },

        )
        )

    ### CALLBACK FUNCTIONS FOR ACTIONS ###    
    def update_map(self, event):
    
        # Callback function to update the map based on the selected performance filter.
        
        selected_performance = event.new  # Get the selected performance from dropdown
        if selected_performance == 'Choose performance':
            # If the default option is selected color map = original color
            self._map.reset_to_full_color_map()
        else:
            # Filter the color map based on performance
            updated_color_map = performance_filter(self.color_map, selected_performance)
            
            # Update the map colors dynamically
            self._map.update_map_colors(updated_color_map)  # Call existing method in ClimateMap
    
    def update_display_input(self, location_details):
        
        # Update function the display with location details or a not found message.
        
        if "message" in location_details:
            self.displayInput.object = f"<span style='color: red;'>{location_details['message']}</span>"
            self.remove_details_button()  # Remove the button if no location details
        else:
            # print the location data of coordinates from the csv
            details = "\n".join(f"**{key}:** {value}" for key, value in location_details.items())
            self.displayInput.object = f"\n\n{details}"
            self.latest_coordinates = location_details.get('coordinates') 
            self.add_details_button()


    def add_details_button(self):   
        # Adds button for more details tab
        if not self.details_button:
            self.details_button = pn.widgets.Button(name="More Details", button_type="primary", width=200)
            self.details_button.on_click(self.handle_details_button_click)
            # Add the button below the location details
            self.details.append(self.details_button)

    def remove_details_button(self):
        # Removes button for more details tab
        if self.details_button:
            self.details.remove(self.details_button)
            self.details_button = None  # Set to None after removing

    def handle_details_button_click(self, event):
        # Creates a new tab for more detailed overview
        content = pn.pane.Markdown("**Details:**")
        new_tab = ("Details", content)
        self.nav_tabs.append_new_tab(new_tab)  # Add the new tab
        print("Appended new 'Details' tab")
    
    def switch_dropdown_options(self, event):
        # Switch dropdown options based on overview dropdown selection
        if event.new == '€ / ton CO₂':
            self.performance_dropdown.options = [
                'Choose performance',
                'Best CO₂ Capture: Cost €277-€453/ton',
                'Good CO₂ Capture: Cost €281-€496/ton',
                'Moderate CO₂ Capture: Cost €327-€501/ton',
                'Worst CO₂ Capture: Cost €357-€568/ton'
            ]
        elif event.new == 'kWh / ton':
            self.performance_dropdown.options = [
                'Choose performance',
                'Best Energy Efficiency: 500-700 kWh/ton',
                'Good Energy Efficiency: 700-900 kWh/ton',
                'Moderate Energy Efficiency: 900-1100 kWh/ton',
                'Worst Energy Efficiency: 1100-1300 kWh/ton'
            ]

    def update_slider(self, event):
        # Update slider range and label based on overview dropdown selection
        if event.new == '€ / ton CO₂':
            self.slider.name = 'Costs (€/ton)'
            self.slider.start = 270
            self.slider.end = 600
            self.slider.value = (270, 600)
            self.slider.format = '0.0a'
        elif event.new == 'kWh / ton':
            self.slider.name = 'Energy (kWh/ton)'
            self.slider.start = 500
            self.slider.end = 1300
            self.slider.value = (500, 1300)
            self.slider.format = '0[.]0'

    def update_map_with_slider(self, event):
        # Callback to update the map based on slider selection.
        selected_range = event.new  # Get the selected range from slider
        filter_column = 'CostsToCapture' if self.slider.name == 'Costs (€/ton)' else 'EnergyRequirements'
        self._map.apply_slider_filter(selected_range, filter_column)

    # Expose the layout for rendering
    def __panel__(self):
        return self._layout
