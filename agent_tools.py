from langchain_openrouter import ChatOpenRouter
from langchain_ollama import ChatOllama
from langchain.tools import tool
from langchain.agents import create_agent
from dotenv import load_dotenv
from openrouter.errors.badrequestresponse_error import BadRequestResponseError
import requests

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




## Creating model ###

model=ChatOllama(
    model="qwen2.5:3b",  

    temperature=0.3
)

## Create Agent to do the task ##   
agent = create_agent(  
    model=model,
    tools=[callsign_tracker,get_aircraft_type,get_aircraft_all_details,get_airline,get_active_flights_by_airline, get_access_token]
)







