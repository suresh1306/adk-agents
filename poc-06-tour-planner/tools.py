"""
Custom Tools for Tour Planner Agent System with ADK State Management

This module provides specialized tools for travel and tour planning.
All tools use ToolContext for proper ADK session and state management.
"""

import math
from typing import Dict, List, Union, Optional
from datetime import datetime, timedelta
from ddgs import DDGS
from google.adk.tools import ToolContext


def search_destination(
    destination: str,
    query_type: str = "attractions",
    tool_context: ToolContext = None
) -> Dict:
    """
    Search for information about a travel destination.

    Args:
        destination: The destination city or location
        query_type: Type of search (attractions, restaurants, hotels, culture)
        tool_context: ADK context for state access (automatically injected)

    Returns:
        Search results about the destination
    """
    try:
        # Read from state if available
        if tool_context:
            # Track search history
            search_count = tool_context.state.get("temp:search_count", 0)
            tool_context.state["temp:search_count"] = search_count + 1
            tool_context.state["temp:last_search_destination"] = destination

            # Save destination for context
            if not tool_context.state.get("temp:destination"):
                tool_context.state["temp:destination"] = destination

        query = f"{destination} {query_type} travel guide"
        ddgs = DDGS()
        results = ddgs.text(query, max_results=5)

        formatted_results = []
        for result in results:
            formatted_results.append({
                "title": result.get("title", ""),
                "url": result.get("href", ""),
                "description": result.get("body", "")
            })

        return {
            "destination": destination,
            "query_type": query_type,
            "results": formatted_results,
            "success": True
        }

    except Exception as e:
        return {
            "destination": destination,
            "error": f"Search failed: {str(e)}",
            "success": False
        }


def calculate_budget(
    destination: str,
    num_days: int,
    num_people: int,
    accommodation_type: str = "mid-range",
    tool_context: ToolContext = None
) -> Dict:
    """
    Calculate estimated budget for a trip.

    Args:
        destination: The destination location
        num_days: Number of days for the trip
        num_people: Number of travelers
        accommodation_type: Type of accommodation (budget, mid-range, luxury)
        tool_context: ADK context for state access (automatically injected)

    Returns:
        Detailed budget breakdown
    """
    try:
        # Save trip parameters to state
        if tool_context:
            tool_context.state["temp:destination"] = destination
            tool_context.state["temp:num_days"] = num_days
            tool_context.state["temp:num_people"] = num_people
            tool_context.state["user:accommodation_preference"] = accommodation_type

        # Rough estimates (simplified for demo)
        accommodation_rates = {
            "budget": 50,
            "mid-range": 120,
            "luxury": 300
        }

        daily_food_per_person = 50
        daily_activities_per_person = 40
        transportation_base = 100

        accommodation_cost = accommodation_rates.get(accommodation_type, 120) * num_days
        food_cost = daily_food_per_person * num_days * num_people
        activities_cost = daily_activities_per_person * num_days * num_people
        transport_cost = transportation_base * num_people

        total_cost = accommodation_cost + food_cost + activities_cost + transport_cost

        # Save budget to state for later reference
        if tool_context:
            tool_context.state["temp:total_budget"] = total_cost
            tool_context.state["temp:budget_breakdown"] = {
                "accommodation": accommodation_cost,
                "food": food_cost,
                "activities": activities_cost,
                "transportation": transport_cost
            }

        return {
            "destination": destination,
            "num_days": num_days,
            "num_people": num_people,
            "breakdown": {
                "accommodation": accommodation_cost,
                "food": food_cost,
                "activities": activities_cost,
                "transportation": transport_cost
            },
            "total_estimated_cost": total_cost,
            "per_person_cost": total_cost / num_people,
            "accommodation_type": accommodation_type,
            "success": True
        }

    except Exception as e:
        return {
            "error": f"Budget calculation failed: {str(e)}",
            "success": False
        }


def create_itinerary(
    destination: str,
    num_days: int,
    interests: Optional[List[str]] = None,
    tool_context: ToolContext = None
) -> Dict:
    """
    Create a day-by-day itinerary template.

    Args:
        destination: The destination location
        num_days: Number of days
        interests: List of interests (culture, food, adventure, relaxation, etc.)
        tool_context: ADK context for state access (automatically injected)

    Returns:
        A structured itinerary template
    """
    try:
        # Read from state if context available
        if tool_context:
            # Use saved interests if not provided
            if not interests:
                interests = tool_context.state.get("user:travel_interests", ["sightseeing", "culture", "food"])
            else:
                # Save interests for future trips
                tool_context.state["user:travel_interests"] = interests

            # Save current trip details
            tool_context.state["temp:destination"] = destination
            tool_context.state["temp:num_days"] = num_days
            tool_context.state["temp:interests"] = interests

        if interests is None:
            interests = ["sightseeing", "culture", "food"]

        itinerary = []
        for day in range(1, num_days + 1):
            day_plan = {
                "day": day,
                "morning": f"Morning activity focusing on {interests[0] if interests else 'exploration'}",
                "afternoon": f"Afternoon {interests[1] if len(interests) > 1 else 'activities'}",
                "evening": f"Evening {interests[2] if len(interests) > 2 else 'dining and leisure'}",
            }
            itinerary.append(day_plan)

        # Save itinerary to state
        if tool_context:
            tool_context.state["temp:itinerary"] = itinerary

        return {
            "destination": destination,
            "num_days": num_days,
            "interests": interests,
            "itinerary": itinerary,
            "success": True
        }

    except Exception as e:
        return {
            "error": f"Itinerary creation failed: {str(e)}",
            "success": False
        }


def get_weather_info(
    destination: str,
    month: Optional[str] = None,
    tool_context: ToolContext = None
) -> Dict:
    """
    Get weather information for a destination.

    Args:
        destination: The destination location
        month: Optional month (e.g., "January", "July")
        tool_context: ADK context for state access (automatically injected)

    Returns:
        Weather information and recommendations
    """
    try:
        # Read from state if context available
        if tool_context:
            # Use saved destination if not provided
            if not destination or destination == "":
                destination = tool_context.state.get("temp:destination", "unknown")

        # Simplified weather info (in production, would use a real API)
        current_month = month or datetime.now().strftime("%B")

        # Generic seasonal info
        seasonal_tips = {
            "December": "Winter season - pack warm clothing",
            "January": "Winter season - pack warm clothing",
            "February": "Winter season - pack warm clothing",
            "March": "Spring season - light jacket recommended",
            "April": "Spring season - pleasant weather",
            "May": "Spring to Summer - comfortable temperatures",
            "June": "Summer season - pack light clothing",
            "July": "Summer season - stay hydrated",
            "August": "Summer season - peak travel time",
            "September": "Fall season - pleasant weather",
            "October": "Fall season - light jacket recommended",
            "November": "Fall to Winter - pack layers",
        }

        return {
            "destination": destination,
            "month": current_month,
            "seasonal_tip": seasonal_tips.get(current_month, "Check weather before travel"),
            "recommendation": f"Research current weather conditions for {destination} in {current_month}",
            "success": True
        }

    except Exception as e:
        return {
            "error": f"Weather lookup failed: {str(e)}",
            "success": False
        }


def get_travel_recommendations(
    destination: str,
    category: str = "general",
    tool_context: ToolContext = None
) -> Dict:
    """
    Get travel recommendations and tips.

    Args:
        destination: The destination location
        category: Category of recommendations (food, safety, culture, activities)
        tool_context: ADK context for state access (automatically injected)

    Returns:
        Travel recommendations and tips
    """
    try:
        # Read from state if context available
        if tool_context:
            # Use saved destination if not provided
            if not destination or destination == "":
                destination = tool_context.state.get("temp:destination", "unknown")

            # Personalize based on user interests
            user_interests = tool_context.state.get("user:travel_interests", [])
            if user_interests and "culture" in user_interests:
                category = "culture" if category == "general" else category

        general_tips = [
            "Research local customs and etiquette before traveling",
            "Keep copies of important documents",
            "Learn basic phrases in the local language",
            "Download offline maps for the area",
            "Check visa requirements well in advance"
        ]

        category_tips = {
            "food": [
                "Try local specialties and street food",
                "Research popular local restaurants",
                "Be aware of food safety practices",
                "Consider dietary restrictions"
            ],
            "safety": [
                "Keep valuables secure",
                "Share your itinerary with someone",
                "Know emergency numbers",
                "Purchase travel insurance"
            ],
            "culture": [
                "Respect local traditions",
                "Dress appropriately for sites",
                "Ask before taking photos",
                "Support local businesses"
            ],
            "activities": [
                "Book popular attractions in advance",
                "Mix tourist spots with local experiences",
                "Allow flexibility in your schedule",
                "Consider guided tours for context"
            ]
        }

        tips = category_tips.get(category, general_tips)

        return {
            "destination": destination,
            "category": category,
            "recommendations": tips,
            "success": True
        }

    except Exception as e:
        return {
            "error": f"Recommendations lookup failed: {str(e)}",
            "success": False
        }


def calculate_travel_distance(
    origin: str,
    destination: str,
    mode: str = "flight",
    tool_context: ToolContext = None
) -> Dict:
    """
    Calculate estimated travel distance and time.

    Args:
        origin: Starting location
        destination: Destination location
        mode: Mode of transport (flight, train, car)
        tool_context: ADK context for state access (automatically injected)

    Returns:
        Distance and estimated travel time
    """
    try:
        # Save travel origin to state
        if tool_context:
            tool_context.state["temp:travel_origin"] = origin
            tool_context.state["temp:travel_mode"] = mode

        # Simplified calculation (in production, would use a real API)
        estimated_times = {
            "flight": "4-12 hours (depending on distance)",
            "train": "Varies by route",
            "car": "Depends on distance and conditions"
        }

        return {
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "estimated_time": estimated_times.get(mode, "Unknown"),
            "recommendation": f"Use a travel search engine to find specific {mode} options from {origin} to {destination}",
            "success": True
        }

    except Exception as e:
        return {
            "error": f"Distance calculation failed: {str(e)}",
            "success": False
        }
