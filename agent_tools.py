from langchain_openrouter import ChatOpenRouter
from langchain_ollama import ChatOllama
from langchain.tools import tool
from langchain.agents import create_agent
from dotenv import load_dotenv
from openrouter.errors.badrequestresponse_error import BadRequestResponseError
from datetime import datetime, timezone
import requests
import time

load_dotenv()


@tool
def callsign_tracker(callsign: str):
    """Track an airplane when the user specifies a callsign."""
    try:
        response = requests.get(
        f"https://api.adsbdb.com/v0/callsign/{callsign}"
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
          if response.status_code == 404: 
               return{"error": f"No flight has been found for the callsign {callsign}. Please try again"}
          return{"error": f"API Error ({response.status_code})"}
    except requests.exceptions.RequestException as e: 
          return{"error": f"Network error while contacting the flight API: {str(e)}"}
    except BadRequestResponseError as e:
          return{"error": f"OpenRouter Bad Request error: {str(e)}"}
   

@tool 
def get_aircraft_type(reg_no: str): 
    """Query for an aircraft by its Mode S transponder code or registration number. Random aircraft endpoint also available."""
    try: 
        response = requests.get(
        f"https://api.adsbdb.com/v0/aircraft/{reg_no}"
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e: 
        if response.status_code == 404: 
            return{"error": f"No flight has been found for registration number {reg_no}. Please try again"}
        return{"error": f"API Error ({response.status_code})"}
    except requests.exceptions.RequestException as e: 
         return{"error": f"Network error while contacting the flight API: {str(e)}"}
    except BadRequestResponseError as e:
         return{"error": f"OpenRouter Bad Request error: {str(e)}"}
    
    

@tool 
def get_aircraft_all_details(reg_no: str, callsign: str): 
    """ Query for both an aircraft & callsign with a single GET request."""
    try: 
        response = requests.get(
        f"https://api.adsbdb.com/v0/aircraft/{reg_no}?callsign={callsign}"
        )
        response.raise_for_status() 
        return response.json() 
    except requests.exceptions.HTTPError as e: 
            if response.status_code == 404: 
                return{"error": f"No flight has been found for registration number {reg_no} / callsign {callsign}. Please try again"}
            return{"error": f"API Error ({response.status_code})"}
    except requests.exceptions.RequestException as e: 
             return{"error": f"Network error while contacting the flight API: {str(e)}"}
    except BadRequestResponseError as e:
             return{"error": f"OpenRouter Bad Request error: {str(e)}"}
    
@tool 
def get_airline(icao: str): 
    """ Query for an Airline based on an Airlines ICAO or IATA short code. 
    If found, this will return an array of one or more Airlines. 
    Random airline endpoint also available, but will always return an array containing only one airline."""
    try: 
        response = requests.get(
        f"https://api.adsbdb.com/v0/airline/{icao}"
        ) 
        response.raise_for_status() 
        return response.json()
    except requests.exceptions.HTTPError as e: 
        if response.status_code == 404: 
            return{"error": f"No airline has been found for ICAO/IATA code {icao}. Please try again"}
        return{"error": f"API Error ({response.status_code})"}
    except requests.exceptions.RequestException as e: 
         return{"error": f"Network error while contacting the flight API: {str(e)}"}
    except BadRequestResponseError as e:
         return{"error": f"OpenRouter Bad Request error: {str(e)}"}



 
OPENSKY_STATES_URL = "https://opensky-network.org/api/states/all"
OPENSKY_TOKEN_URL = (
    "https://auth.opensky-network.org/auth/realms/opensky-network/"
    "protocol/openid-connect/token"
)
 
# State vector field order, per OpenSky docs
STATE_FIELDS = [
    "icao24", "callsign", "origin_country", "time_position", "last_contact",
    "longitude", "latitude", "baro_altitude", "on_ground", "velocity",
    "true_track", "vertical_rate", "sensors", "geo_altitude", "squawk",
    "spi", "position_source", "category",
]

MAX_FLIGHTS_RETURNED = 15  # keep payloads small for the LLM

def _ts(unix_ts):
    """Convert a UNIX timestamp to a human-readable string, or 'N/A'."""
    if unix_ts is None:
        return "N/A"
    return datetime.fromtimestamp(unix_ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

def _format_flights(flights: list, airport: str, direction: str) -> dict:
    """Distill raw OpenSky flight records into an LLM-friendly summary.
    
    - Keeps only the useful fields (callsign, airports, times)
    - Converts UNIX timestamps to readable strings
    - Caps the list at MAX_FLIGHTS_RETURNED
    """
    if not flights:
        return {"message": f"No {direction} recorded at {airport} in the requested time window."}

    total = len(flights)
    trimmed = flights[:MAX_FLIGHTS_RETURNED]

    cleaned = []
    for f in trimmed:
        cleaned.append({
            "callsign": (f.get("callsign") or "").strip() or "Unknown",
            "departure_airport": f.get("estDepartureAirport") or "Unknown",
            "arrival_airport": f.get("estArrivalAirport") or "Unknown",
            "first_seen": _ts(f.get("firstSeen")),
            "last_seen": _ts(f.get("lastSeen")),
        })

    result = {
        "airport": airport,
        "direction": direction,
        "total_count": total,
        "showing": len(cleaned),
        "flights": cleaned,
    }
    if total > MAX_FLIGHTS_RETURNED:
        result["note"] = f"Showing {MAX_FLIGHTS_RETURNED} of {total} flights."
    return result
 
@tool
def get_access_token(client_id: str, client_secret: str) -> str:
    """Exchange OAuth2 client credentials for a bearer token (optional,
    only needed if you want higher rate limits)."""
    try:
        resp = requests.post(
            OPENSKY_TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
            },
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()["access_token"]
    except requests.exceptions.HTTPError as e:
        if resp.status_code == 404:
            return{"error": f"Token endpoint not found. Please check your credentials."}
        return{"error": f"API Error ({resp.status_code})"}
    except requests.exceptions.RequestException as e:
        return{"error": f"Network error while contacting the token API: {str(e)}"}
    except BadRequestResponseError as e:
        return{"error": f"OpenRouter Bad Request error: {str(e)}"}
 
def _fetch_all_states(access_token: str | None = None) -> list[dict]:
    """Internal helper: fetch all current aircraft state vectors from OpenSky."""
    try:
        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
 
        resp = requests.get(OPENSKY_STATES_URL, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
 
        states = data.get("states") or []
        return [dict(zip(STATE_FIELDS, s)) for s in states]
    except requests.exceptions.HTTPError as e:
        if resp.status_code == 404:
            return{"error": f"OpenSky states endpoint not found."}
        return{"error": f"API Error ({resp.status_code})"}
    except requests.exceptions.RequestException as e:
        return{"error": f"Network error while contacting the OpenSky API: {str(e)}"}
    except BadRequestResponseError as e:
        return{"error": f"OpenRouter Bad Request error: {str(e)}"}

@tool
def fetch_all_states(access_token: str | None = None) -> list[dict]:
    """Fetch all current aircraft state vectors from OpenSky."""
    return _fetch_all_states(access_token)
 
@tool
def get_active_flights_by_airline(icao_prefix: str, access_token: str | None = None) -> list[dict]:
    """
    Return all currently airborne/tracked flights whose callsign starts
    with the given airline ICAO code (e.g. 'UAL', 'AAL', 'DLH', 'AIC').
    """
    try:
        icao_prefix = icao_prefix.strip().upper()
        all_states = _fetch_all_states(access_token)
 
        matches = []
        for s in all_states:
            callsign = (s.get("callsign") or "").strip()
            if callsign.upper().startswith(icao_prefix):
                matches.append({
                    "callsign": callsign,
                    "icao24": s["icao24"],
                    "origin_country": s["origin_country"],
                    "longitude": s["longitude"],
                    "latitude": s["latitude"],
                    "altitude_m": s["baro_altitude"],
                    "on_ground": s["on_ground"],
                    "velocity_mps": s["velocity"],
                    "heading": s["true_track"],
                    "last_contact": s["last_contact"],
                })
        return matches
    except requests.exceptions.HTTPError as e:
        return{"error": f"API Error while fetching flights for airline {icao_prefix}"}
    except requests.exceptions.RequestException as e:
        return{"error": f"Network error while contacting the OpenSky API: {str(e)}"}
    except BadRequestResponseError as e:
        return{"error": f"OpenRouter Bad Request error: {str(e)}"}

@tool
def get_airport_departures(icao: str, hours_back: int = 3, access_token: str | None = None) -> dict:
    """Get recent departures for an airport by its ICAO code (default: last 3 hours)."""
    try:
        end = int(time.time())
        begin = end - hours_back * 3600
        headers = {"Authorization": f"Bearer {access_token}"} if access_token else {}

        params = {"airport": icao.upper(), "begin": begin, "end": end}
        resp = requests.get(
            "https://opensky-network.org/api/flights/departure",
            params=params, headers=headers, timeout=30,
        )
        # OpenSky returns 404 with an empty [] when no flights are found —
        # treat that as "no data", not a fatal error.
        if resp.status_code == 404:
            return _format_flights([], icao.upper(), "departures")
        resp.raise_for_status()
        return _format_flights(resp.json(), icao.upper(), "departures")
    except requests.exceptions.HTTPError as e:
        return {"error": f"API Error ({resp.status_code}) while fetching departures for airport {icao}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error while contacting the OpenSky API: {str(e)}"}
    except BadRequestResponseError as e:
        return {"error": f"OpenRouter Bad Request error: {str(e)}"}

@tool
def get_airport_arrivals(icao: str, hours_back: int = 1, access_token: str | None = None) -> dict:
    """Get arrivals for an airport by its ICAO code."""
   
    end = int(time.time())
    begin = end - hours_back * 3600
    headers = {"Authorization": f"Bearer {access_token}"} if access_token else {}

    params = {"airport": icao.upper(), "begin": begin, "end": end}
    resp = requests.get(
            "https://opensky-network.org/api/flights/arrival",
            params=params, headers=headers, timeout=30,
        )
    resp.raise_for_status()
    return {"arrivals": resp.json()}
   

## Creating model ###

model=ChatOllama(
    model="qwen2.5:3b",  

    temperature=0.3
)

## Create Agent to do the task ##   
agent = create_agent(  
    model=model,
    tools=[callsign_tracker,get_aircraft_type,get_aircraft_all_details,get_airline,get_active_flights_by_airline, get_access_token, get_airport_departures, get_airport_arrivals]
)







