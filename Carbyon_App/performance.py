def performance_filter(gridcode_color_map, performance):
    """
    Change the color map based on the selected performance filter.

    gridcode_color_map (dict): Original GRIDCODE to color and description mapping.
    performance (str): Selected performance filter.
        
    Returns:
        dict: Updated GRIDCODE to color and description mapping.
    """
    performance_colors = {
        "Best CO₂ Capture: Cost €277-€453/ton": '#90be6d',  # Green
        "Good CO₂ Capture: Cost €281-€496/ton": '#e9c46a',  # Yellow 
        "Moderate CO₂ Capture: Cost €327-€501/ton": '#f4a261',  # Orange
        "Worst CO₂ Capture: Cost €357-€568/ton": '#e76f51',  # Red
        "Best Energy Efficiency: 500-700 kWh/ton": '#90be6d',
        "Good Energy Efficiency: 700-900 kWh/ton": '#e9c46a',
        "Moderate Energy Efficiency: 900-1100 kWh/ton": '#f4a261',
        "Worst Energy Efficiency: 1100-1300 kWh/ton": '#e76f51'
    }

    selected_color = performance_colors.get(performance, None)

    if selected_color is None:
        return gridcode_color_map

    filtered_map = {
        gridcode: (selected_color if color[0] == selected_color else '#e0e0e0', color[1])
        for gridcode, color in gridcode_color_map.items()
    }

    return filtered_map
