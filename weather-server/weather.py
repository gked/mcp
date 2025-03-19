from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP


# Initialize the FastMCP server
mcp = FastMCP("weather-server")

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

async def make_nws_request(url:str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json",
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""Event: {props.get("event", "Unknown")}
Area: {props.get("areaDesc", "Unknown")}
Severity: {props.get("severity", "Unknown")}
Description: {props.get("description", "No description available")}
Instructions: {props.get("instruction", "No instruction provided")}"""


@mcp.tool()
async def get_alerts(location: str) -> str:
    """Get the alerts for a US state.
        Args:
            state: Two-letter US state code (e.g. CA, NY)"""
    url = f"{NWS_API_BASE}/alerts/active/area/{location}"
    data = await make_nws_request(url)
    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."
    if not data["features"]:
        return "No active alerts for this state."
    
    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n\n".join(alerts)


@mcp.tool()
async def get_forecast(location: str) -> str:
    """Get the forecast for a given location."""
    url = f"{NWS_API_BASE}/points/{location}/forecast"
    forecast = await make_nws_request(url)
    return forecast
