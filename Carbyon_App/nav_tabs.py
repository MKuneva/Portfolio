import panel as pn


class NavTabs(pn.viewable.Viewer):
    def __init__(self, overview_content):
        super().__init__()

        # Create a Tabs layout, passing the Overview content as one of the tabs
        self.tabs = pn.Tabs(
            ("Location Sensitivity", overview_content),
            tabs_location="left",
            styles={
                'font-size': '12px',                 
                'font-weight': 'bold', 
                'height':'85vh',        
            }
        )
    def append_new_tab(self, new_tab):
        # Method to append new tab to the existing ones
        self.tabs.append(new_tab)
    
    

    # Expose the layout for rendering
    def __panel__(self):
        return self.tabs