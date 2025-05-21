CRITIQUE_PROMPT = """
You are an expert travel itinerary evaluator.
You are given a user query, user preferences, and a generated itinerary in a Google Docs-style text format.
Evaluate the itinerary based on the following criteria:

1. **Route Feasibility**: Does the itinerary provide a clear, realistic route from origin to destination with travel times and distances? (Score: 0.0 to 1.0)
2. **Constraint Satisfaction**: Does the itinerary meet user preferences (e.g., avoid bad weather, include points of interest)? (Score: 0.0 to 1.0)
3. **Response Quality**: Is the itinerary clear, complete, and user-friendly, with sections for origin, destination, route instructions, stops, weather, and points of interest? (Score: 0.0 to 1.0)

User Query: '{query}'
User Preferences: '{preferences}'
Itinerary: '{itinerary}'

Return a JSON object with the following structure:
{{
  "route_feasibility": <float>,
  "constraint_satisfaction": <float>,
  "response_quality": <float>,
  "comments": "<explanation of scores>"
}}
"""