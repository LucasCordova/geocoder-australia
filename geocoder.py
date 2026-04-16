"""Google Maps Geocoding helpers (Australia-focused)."""

from __future__ import annotations

from typing import Optional, Tuple

import googlemaps

GOOGLE_MAPS_API_KEY = "AIzaSyA8HVGRG5_GYkxTr3kntNDIE_l1k6BGqfk"


def _parse_lat_lng(coordinates: str) -> Tuple[float, float]:
    """
    Accepts "lat,lng" (optionally with spaces) and returns floats.
    """
    if not coordinates or "," not in coordinates:
        raise ValueError('coordinates must be in the form "lat,lng"')
    lat_s, lng_s = (p.strip() for p in coordinates.split(",", 1))
    return float(lat_s), float(lng_s)


def _pick_component(components: list[dict], preferred_types: list[str]) -> Optional[str]:
    for t in preferred_types:
        for c in components:
            if t in c.get("types", []):
                return c.get("long_name") or c.get("short_name")
    return None


def reverse_geocoder(coordinates: str) -> Tuple[str, str]:
    """
    Reverse-geocode a "lat,lng" string and return (suburb, postal_code).
    """
    if not GOOGLE_MAPS_API_KEY:
        raise RuntimeError("Missing Google Maps API key. Set GOOGLE_MAPS_API_KEY in geocoder.py.")

    lat, lng = _parse_lat_lng(coordinates)
    client = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

    suburb = ""
    postal_code = ""

    def absorb(results: list[dict]) -> None:
        nonlocal suburb, postal_code
        for r in results or []:
            comps = r.get("address_components", []) or []

            if not suburb:
                # In Australia, suburb is commonly "locality" or a "sublocality".
                suburb = _pick_component(
                    comps,
                    preferred_types=[
                        "locality",
                        "postal_town",
                        "sublocality",
                        "sublocality_level_1",
                        "administrative_area_level_3",
                        "administrative_area_level_2",
                    ],
                ) or suburb

            if not postal_code:
                postal_code = _pick_component(comps, preferred_types=["postal_code"]) or postal_code

            if suburb and postal_code:
                return

    # 1) First try to get a clean postal_code result.
    absorb(client.reverse_geocode((lat, lng), result_type=["postal_code"], language="en"))

    # 2) Then try to get a clean locality/sublocality result for suburb.
    absorb(
        client.reverse_geocode(
            (lat, lng),
            result_type=["locality", "postal_town", "sublocality", "sublocality_level_1"],
            language="en",
        )
    )

    # 3) Fallback: general reverse geocode.
    if not (suburb and postal_code):
        absorb(client.reverse_geocode((lat, lng), language="en"))

    return suburb or "", postal_code or ""


def reverse_geocode(coordinates: str) -> Tuple[str, str]:
    """
    Alias for reverse_geocoder(); returns (suburb, postal_code).
    """
    return reverse_geocoder(coordinates=coordinates)

