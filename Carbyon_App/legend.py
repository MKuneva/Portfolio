def climate_map_legend():
     # Create a categorized legend using HTML
    legend_html = '''
    <div style="
        position: fixed; 
        bottom: 10px; left: 10px; width: 200px; height: 200px; 
        background-color: white; 
        border:2px solid grey; 
        z-index:1000; 
        font-size:12px;
        overflow-y: auto;
    ">
        <div style="padding: 10px;">
            <b>Climate Classification Legend</b><br><br>
            <i style="background:#90be6d; width:10px; height:10px; float:left; margin-right:5px; margin-top:5px;"></i><b>Best CO₂ capture:</b><br>
            Cold and dry, these regions maximize CO₂ density and minimize energy requirements for DAC systems.
            <ul>
                <li>Cold Desert/Arid Climate</li>
                <li>Cold Semi-arid/Semi-desert Climate/Steppe</li>
            </ul>
            <br>
            <i style="background:#e9c46a; width:10px; height:10px; float:left; margin-right:5px; margin-top:5px;"></i><b>Good CO₂ capture:</b><br>
            Varying temperatures and moisture levels complicate CO₂ capture efficiency and increase energy requirements.
            <ul>
                <li>Humid Continental Climate</li>
                <li>Mediterranean Climate</li>
                <li>Oceanic/Marine Climate</li>
                <li>Humid Subtropical Climate</li>
            </ul>
            <br>
            <i style="background:#f4a261; width:10px; height:10px; float:left; margin-right:5px; margin-top:5px;"></i><b>Moderate CO₂ capture:</b><br>
            Increased energy requirements due to the region's environment.
            <ul>
                <li>Hot Semi-arid/Semi-desert Climate/Steppe</li>
                <li>Hot Desert/Arid Climate</li>
            </ul>
            <br>
            <i style="background:#e76f51; width:10px; height:10px; float:left; margin-right:5px; margin-top:5px;"></i><b>Worst CO₂ capture:</b><br>
            Warmer and more humid, these regions have higher energy requirements for DAC, making them less effective for CO₂ capture.
            <ul>
                <li>Tropical Savanna Climate</li>
                <li>Tropical Rainforest/Equatorial Climate</li>
                <li>Tropical Monsoon Climate</li>
                <li>Subarctic Climate</li>
                <li>Ice Cap Climate</li>
                <li>Tundra Climate</li>
            </ul>
        </div>
    </div>
    '''
    return legend_html