OPTIMIZER_PROMPT = """
You are an expert travel optimizer.
Given the initial plan:
'{initial_plan}',
route data: 
'{route_data}',
origin weather data:
'{weather_origin}',
destination weather data:
'{weather_destination}',
and user preferences:
'{preferences}', 
refine the itinerary. 

Ensure the route is feasible, weather-safe, and includes relevant points of interest.
Return a JSON with optimized_route, travel_time, weather_conditions, and points_of_interest.
"""