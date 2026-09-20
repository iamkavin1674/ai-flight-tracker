import requests
import os
from dotenv import load_dotenv
from langchain.tools import tool

load_dotenv()

api = os.getenv("SERPAPI_KEY")

@tool
def flight_prices(departure_id: str, arrival_id: str, outbound_date: str, return_date: str = None) -> dict:
    """Get flight prices from one aiport to another via Google search. departure_id is departure airport, arrival_id is arrival airport. If user does not specify time, list flights from today until 2 days next"""
    try:
        params = {
            "engine": "google_flights",
            "departure_id": departure_id,
            "arrival_id": arrival_id,
            "outbound_date": outbound_date,
            "currency": "USD",
            "type": "2" if return_date is None else "1",
            "api_key": api,
        }
        if return_date:
            params["return_date"] = return_date
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            return {"error": "Token endpoint not found. Please check your credentials."}
        if response.status_code == 401:
            return {"error": "API Issue"}
        return {"error": f"HTTP error: {str(e)}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error while contacting the token API: {str(e)}"}

@tool
def booking_options(departure_id: str, arrival_id: str, outbound_date: str, booking_token: str, return_date: str = None) -> dict:
    """If user wishes to book a flight, use this function to retrieve the booking options for the flight"""
    try:
        params = {
            "engine": "google_flights",
            "departure_id": departure_id,
            "arrival_id": arrival_id,
            "outbound_date": outbound_date,
            "currency": "USD",
            "booking_token":booking_token, 
            "type": "2" if return_date is None else "1",
            "api_key": api,
        }
        if return_date:
            params["return_date"] = return_date
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            return {"error": "Token endpoint not found. Please check your credentials."}
        if response.status_code == 401:
            return {"error": "API Issue"}
        return {"error": f"HTTP error: {str(e)}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error while contacting the token API: {str(e)}"}
