
from agent_tools import get_airport_arrivals

result = get_airport_arrivals.invoke({"icao": "KJFK", "hours_back": 12})
print(result)