import logging
import asyncio 
import os     
from google.maps import routing_v2
from google.protobuf import field_mask_pb2
from google.api_core.client_options import ClientOptions # If explicit API key for client is needed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleMapsTool:
    def __init__(self):
        try:
            # Alternatively, to be explicit if the env var isn't picked up as expected:
            api_key = os.getenv("GOOGLE_MAPS_API_KEY") 
            if api_key:
                client_options = ClientOptions(api_key = api_key)
                self.client = routing_v2.RoutesClient(client_options = client_options)
            else:
                 # Fallback to default (ADC or other auto-discovery)
                self.client = routing_v2.RoutesClient()
                logger.info("Routes API client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Routes API client: {str(e)}")
            raise

    async def get_directions(self, origin: str, destination: str) -> dict:
        try:
            logger.info(f"Fetching directions from '{origin}' to '{destination}' using Routes API.")
            request = routing_v2.types.ComputeRoutesRequest(
                origin=routing_v2.types.Waypoint(address=origin),
                destination=routing_v2.types.Waypoint(address=destination),
                travel_mode=routing_v2.types.RouteTravelMode.DRIVE,
                # I can add other parameters here, for example:
                # routing_preference=routing_v2.types.RoutingPreference.TRAFFIC_AWARE,
                # compute_alternative_routes=False,
                # language_code="en-US",
                # units=routing_v2.types.Units.METRIC, # Or IMPERIAL
            )

            field_mask_paths = [
                "routes.legs.steps", # For turn-by-turn (if needed, can be verbose)
                "routes.legs.polyline", # Polyline for each leg
                "routes.legs.distance_meters",
                "routes.legs.duration",
                "routes.distance_meters", # Overall route distance
                "routes.duration",        # Overall route duration
                "routes.polyline.encoded_polyline", # Overall route polyline
                # "routes.travel_advisory.toll_info" # If you need toll information (might require billing SKU upgrade)
            ]
            field_mask_str = ",".join(field_mask_paths)

            # The compute_routes method is synchronous.
            # We run it in a separate thread to avoid blocking the asyncio event loop.
            response = await asyncio.to_thread(
                self.client.compute_routes,
                request=request,
                metadata=[
                    ('x-goog-fieldmask', field_mask_str)
                    # The API key should be handled by the client (ADC or GOOGLE_API_KEY env var).
                    # If you still face auth issues, you might need to add it here explicitly:
                    # ('x-goog-api-key', os.getenv("GOOGLE_MAPS_API_KEY"))
                ]
            )

            if not response.routes:
                logger.warning(f"No routes found from '{origin}' to '{destination}'.")
                raise ValueError("No routes found")

            logger.info(f"Successfully fetched directions. Found {len(response.routes)} route(s).")
            # Assuming we take the first route, similar to your original code
            route = response.routes[0]

            distance_meters = route.distance_meters
            duration_seconds_str = route.duration # Format is "123s" (e.g., "3600s")

            # For compatibility and clarity:
            # The old structure: directions[0]["legs"][0]["distance"]["text"]
            # The new structure gives overall route.distance_meters and route.duration
            # and also route.legs[i].distance_meters and route.legs[i].duration

            # Create a more structured leg representation
            parsed_legs = []
            if route.legs:
                for leg in route.legs:
                    parsed_leg = {
                        "distance_meters": leg.distance_meters,
                        "distance_text": f"{leg.distance_meters / 1000:.1f} km", # Example formatting
                        "duration_str": leg.duration, # e.g., "300s"
                        "duration_text": leg.duration, # You might want to parse "300s" to "5 mins"
                        "polyline": leg.polyline.encoded_polyline if leg.polyline else None,
                        "steps": [] # You can populate steps here if needed from leg.steps
                    }
                    # For example, to add simplified step instructions:
                    # for step in leg.steps:
                    #    parsed_leg["steps"].append({
                    #        "instruction": step.navigation_instruction.instructions if step.navigation_instruction else "N/A",
                    #        "distance_meters": step.distance_meters,
                    #        "duration": step.duration,
                    #    })
                    parsed_legs.append(parsed_leg)


            return {
                "overall_distance_meters": distance_meters,
                "overall_distance_text": f"{distance_meters / 1000:.1f} km", # Example formatting
                "overall_duration_str": duration_seconds_str, # e.g., "3600s"
                "overall_duration_text": duration_seconds_str, # You might want to parse this for "1 hour" etc.
                "overall_polyline": route.polyline.encoded_polyline if route.polyline else None,
                "legs_data": parsed_legs, # Detailed data for each leg
                "raw_route_object": route # For access to all underlying protobuf data if needed
            }

        except Exception as e:
            logger.error(f"Error fetching directions using Routes API: {str(e)}", exc_info=True)
            # Consider re-raising a custom error or handling it based on your application's needs
            raise