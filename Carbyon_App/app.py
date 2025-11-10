import panel as pn
from overview import Overview  
from nav_tabs import NavTabs  


pn.extension(
    sizing_mode="stretch_width",
    css_files=[
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css"
    ],
)

class App(pn.viewable.Viewer):

    def __init__(self):
        super().__init__()
        # Create the Overview instance first and pass None temporarily to nav_tabs
        overview = Overview(nav_tabs=None)  

        # Create the NavTabs instance
        self._tabs = NavTabs(overview)

        # Update the Overview instance with the correct nav_tabs reference
        overview.nav_tabs = self._tabs  

        # Create the layout using the NavTabs instance
        self._layout = pn.template.BootstrapTemplate(
            title="Carbyon",
            header_background="#41abff",
            main=pn.Row(self._tabs)
        )
         
    # Expose the layout for rendering
    def __panel__(self):
        return self._layout
    
# Serve the app
app = App()
app.servable()
