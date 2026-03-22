"""
soil_api.py — NRCS Soil Data Access API and Census Geocoder wrappers.

Data sources:
    Census Geocoder: geocoding.geo.census.gov
    NRCS Soil Data Access: SDMDataAccess.nrcs.usda.gov
"""

import json
import urllib.request
import urllib.parse


def geocode_address(address: str) -> tuple[float, float, str]:
    """
    Convert address string to (lat, lon, matched_address) via Census Geocoder.
    Raises ValueError if no match found.
    """
    base = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
    params = {
        "address":   address,
        "benchmark": "2020",
        "format":    "json",
    }
    url = base + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "NYCannabis-SoilTool/1.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode())

    matches = data.get("result", {}).get("addressMatches", [])
    if not matches:
        raise ValueError(
            f"No geocoding results for: '{address}'\n"
            "Tips: Include city, state, and ZIP code; check spelling."
        )
    coords = matches[0]["coordinates"]
    lat = float(coords["y"])
    lon = float(coords["x"])
    matched = matches[0].get("matchedAddress", address)
    return lat, lon, matched


def query_component(lat: float, lon: float) -> dict | None:
    """
    Query NRCS SDA for the dominant soil component at a lat/lon point.
    Returns dict or None if no SSURGO data at this location.
    """
    url = "https://SDMDataAccess.nrcs.usda.gov/Tabular/SDMTabularService/post.rest"
    query = f"""
    SELECT TOP 1
        mu.muname,
        co.compname,
        co.comppct_r,
        co.drainagecl,
        co.hydgrp,
        co.slope_r,
        co.taxsubgrp
    FROM mapunit mu
    INNER JOIN component co ON mu.mukey = co.mukey
    WHERE mu.mukey IN (
        SELECT mukey FROM SDA_Get_Mukey_from_intersection_with_WktWgs84('POINT ({lon} {lat})')
    )
    AND co.majcompflag = 'Yes'
    ORDER BY co.comppct_r DESC
    """
    payload = f"query={urllib.parse.quote(query.strip())}&format=json%2Bcolumnname"
    req = urllib.request.Request(
        url,
        data=payload.encode(),
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept":       "application/json",
            "User-Agent":   "NYCannabis-SoilTool/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())

    rows = data.get("Table", [])
    if len(rows) < 2:
        return None

    row = rows[1]  # row 0 = column headers; row 1 = first data row
    return {
        "map_unit":  row[0],
        "series":    row[1],
        "pct":       row[2],
        "drainage":  row[3],
        "hydro_grp": row[4],
        "slope":     row[5],
        "taxonomy":  row[6],
    }


def query_horizon(lat: float, lon: float) -> dict | None:
    """
    Query NRCS SDA for surface horizon (0 cm top) properties.
    Returns dict with texture, pH, CEC, OM or None if not found.
    """
    url = "https://SDMDataAccess.nrcs.usda.gov/Tabular/SDMTabularService/post.rest"
    query = f"""
    SELECT TOP 1
        h.hzname,
        h.sandtotal_r,
        h.silttotal_r,
        h.claytotal_r,
        h.ph1to1h2o_r,
        h.cec7_r,
        h.om_r,
        h.hzdept_r,
        h.hzdepb_r
    FROM mapunit mu
    INNER JOIN component co ON mu.mukey = co.mukey
    INNER JOIN chorizon h ON co.cokey = h.cokey
    WHERE mu.mukey IN (
        SELECT mukey FROM SDA_Get_Mukey_from_intersection_with_WktWgs84('POINT ({lon} {lat})')
    )
    AND co.majcompflag = 'Yes'
    AND h.hzdept_r = 0
    ORDER BY co.comppct_r DESC
    """
    payload = f"query={urllib.parse.quote(query.strip())}&format=json%2Bcolumnname"
    req = urllib.request.Request(
        url,
        data=payload.encode(),
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept":       "application/json",
            "User-Agent":   "NYCannabis-SoilTool/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())

    rows = data.get("Table", [])
    if len(rows) < 2:
        return None

    row = rows[1]
    sand  = float(row[1]) if row[1] is not None else None
    silt  = float(row[2]) if row[2] is not None else None
    clay  = float(row[3]) if row[3] is not None else None

    return {
        "horizon":   row[0],
        "texture":   _texture_class(sand, silt, clay),
        "ph":        row[4],
        "cec":       row[5],
        "om":        row[6],
        "depth_top": row[7],
        "depth_bot": row[8],
    }


def _texture_class(sand, silt, clay) -> str:
    """Derive USDA texture class name from sand/silt/clay percentages."""
    if sand is None or silt is None or clay is None:
        return "Unknown"
    if clay >= 60:
        return "Heavy clay"
    if clay >= 40:
        return "Clay"
    if clay >= 35 and sand <= 45:
        return "Clay"
    if clay >= 27 and sand <= 20:
        return "Silty clay"
    if clay >= 27 and silt >= 20:
        return "Clay loam"
    if clay >= 20 and sand >= 45:
        return "Sandy clay loam"
    if silt >= 80 and clay < 12:
        return "Silt"
    if silt >= 50:
        return "Silt loam"
    if sand >= 85:
        return "Sand"
    if sand >= 70:
        return "Loamy sand"
    if sand >= 52 and clay < 20:
        return "Sandy loam"
    return "Loam"


def get_soil_data(address: str) -> dict:
    """
    Convenience wrapper: geocode address, then fetch component + horizon data.
    Returns a single dict with all available data.
    Raises on geocoding failure; gracefully returns partial data on API failure.
    """
    lat, lon, matched = geocode_address(address)

    result = {
        "lat": lat,
        "lon": lon,
        "matched_address": matched,
        "comp": None,
        "horizon": None,
        "error_comp": None,
        "error_horizon": None,
    }

    try:
        result["comp"] = query_component(lat, lon)
    except Exception as e:
        result["error_comp"] = str(e)

    try:
        result["horizon"] = query_horizon(lat, lon)
    except Exception as e:
        result["error_horizon"] = str(e)

    return result
