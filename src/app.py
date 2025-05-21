# src/app.py
import streamlit as st
import asyncio
import sys
import os
import logging
import json


# Debug sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.dirname(__file__))
sys.path.append(project_root)
sys.path.append(os.path.dirname(__file__))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"sys.path: {sys.path}")

try:
    from evaluation.evaluation_script import EvaluationScript
except ImportError as e:
    logger.error(f"Import error: {str(e)}")
    raise

st.set_page_config(page_title="Travel Assistant", page_icon="✈️")

async def run_evaluation(query: str, origin: str, destination: str, preferences: dict, refinement: str = None, prior_itinerary: dict = None) -> tuple:
    evaluator = EvaluationScript()
    try:
        if not query:
            logger.error("run_evaluation: Query is empty")
            raise ValueError("Query is required")
        logger.info(f"run_evaluation: Query: {query}, Refinement: {refinement}")
        itinerary, results = await evaluator.run_evaluation(
            query=query,
            origin=origin,
            destination=destination,
            preferences=preferences,
            refinement=refinement,
            prior_itinerary=prior_itinerary
        )
        logger.info(f"Evaluation result - Itinerary: {json.dumps(itinerary, indent=2)}")
        return itinerary, results
    except Exception as e:
        logger.error(f"Evaluation error: {str(e)}")
        st.error(f"Error running evaluation: {str(e)}")
        return None, []

def main():
    st.title("Travel Assistant Chatbot")
    st.write("Plan your trip with AI-powered recommendations!")

    # Initialize session state
    if "conversation" not in st.session_state:
        st.session_state.conversation = {
            "query": "",
            "origin": "",
            "destination": "",
            "preferences": {"avoid_bad_weather": True, "include_pois": True},
            "itinerary": None,
            "results": [],
            "refinements": []
        }

    # User inputs for initial query
    query = st.text_input("Travel Query", value=st.session_state.conversation["query"], placeholder="Plan a scenic trip from San Francisco to Los Angeles")
    origin = st.text_input("Origin", value=st.session_state.conversation["origin"], placeholder="San Francisco, CA, US")
    destination = st.text_input("Destination", value=st.session_state.conversation["destination"], placeholder="Los Angeles, CA, US")
    avoid_bad_weather = st.checkbox("Avoid Bad Weather", value=st.session_state.conversation["preferences"]["avoid_bad_weather"])
    include_pois = st.checkbox("Include Points of Interest", value=st.session_state.conversation["preferences"]["include_pois"])
    preferences = {"avoid_bad_weather": avoid_bad_weather, "include_pois": include_pois}

    if st.button("Plan Trip"):
        if not query or not origin or not destination:
            st.error("Please provide query, origin, and destination.")
            return

        # Update session state
        st.session_state.conversation.update({
            "query": query,
            "origin": origin,
            "destination": destination,
            "preferences": preferences,
            "refinements": []
        })
        logger.info(f"Session state updated: {json.dumps(st.session_state.conversation, indent=2)}")

        with st.spinner("Planning your trip..."):
            # Run initial evaluation
            itinerary, results = asyncio.run(run_evaluation(query, origin, destination, preferences))
            if itinerary and results:
                st.session_state.conversation["itinerary"] = itinerary
                st.session_state.conversation["results"] = results
                logger.info(f"Initial itinerary stored: {json.dumps(itinerary, indent=2)}")

    # Display current itinerary and results
    if st.session_state.conversation["itinerary"]:
        st.subheader("Travel Itinerary")
        st.markdown(st.session_state.conversation["itinerary"]["final_itinerary"])

        st.subheader("Evaluation Metrics")
        for result in st.session_state.conversation["results"]:
            if "error" in result:
                st.warning(f"Prompt '{result['prompt']}': Error - {result['error']}")
            else:
                st.write(f"**Prompt: {result['prompt']}**")
                st.write(f"- Route Feasibility: {result['route_feasibility']:.2f}")
                st.write(f"- Constraint Satisfaction: {result['constraint_satisfaction']:.2f}")
                st.write(f"- Response Quality: {result['response_quality']:.2f}")
                st.write(f"- Total Score: {result['total']:.2f}")
                st.write(f"- Comments: {result['comments']}")
                st.divider()

        # Display average scores and best prompt
        from evaluation.metrics import compute_average_scores, find_best_prompt
        avg_scores = compute_average_scores(st.session_state.conversation["results"])
        best_prompt = find_best_prompt(st.session_state.conversation["results"])

        st.subheader("Summary Metrics")
        st.write(f"**Average Scores Across Prompts ({', '.join(avg_scores['prompts'])})**")
        st.write(f"- Avg Route Feasibility: {avg_scores['avg_route_feasibility']:.2f}")
        st.write(f"- Avg Constraint Satisfaction: {avg_scores['avg_constraint_satisfaction']:.2f}")
        st.write(f"- Avg Response Quality: {avg_scores['avg_response_quality']:.2f}")
        st.write(f"- Avg Total Score: {avg_scores['avg_total']:.2f}")

        st.write(f"**Best Prompt**")
        st.write(f"- Prompt: {best_prompt['best_prompt']}")
        st.write(f"- Total Score: {best_prompt['total_score']:.2f}")
        st.write(f"- Details: {json.dumps(best_prompt['details'], indent=2)}")

        # Refinement input
        st.subheader("Refine Your Trip")
        refinement = st.text_input("Refinement Request", placeholder="e.g., Make it a half-day trip")
        if st.button("Submit Refinement"):
            if not refinement:
                st.error("Please provide a refinement request.")
                return

            # Ensure query is not empty
            if not st.session_state.conversation["query"]:
                st.error("Original query is missing. Please submit a new trip plan.")
                logger.error("Refinement attempted with empty query")
                return

            logger.info(f"Refinement request: {refinement}")
            logger.info(f"Session state before refinement: {json.dumps(st.session_state.conversation, indent=2)}")

            with st.spinner("Refining your trip..."):
                # Run evaluation with refinement
                itinerary, results = asyncio.run(run_evaluation(
                    query=st.session_state.conversation["query"],
                    origin=st.session_state.conversation["origin"],
                    destination=st.session_state.conversation["destination"],
                    preferences=st.session_state.conversation["preferences"],
                    refinement=refinement,
                    prior_itinerary=st.session_state.conversation["itinerary"]
                ))
                if itinerary and results:
                    st.session_state.conversation["itinerary"] = itinerary
                    st.session_state.conversation["results"] = results
                    st.session_state.conversation["refinements"].append(refinement)
                    logger.info(f"Refined itinerary stored: {json.dumps(itinerary, indent=2)}")
                    st.success("Trip refined successfully!")
                    st.rerun()

if __name__ == "__main__":
    main()