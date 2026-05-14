import asyncio
import sys
import types
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[1] / "custom_components" / "cityparking"
custom_components_pkg = sys.modules.setdefault(
    "custom_components", types.ModuleType("custom_components")
)
custom_components_pkg.__path__ = [str(PACKAGE_ROOT.parent)]
cityparking_pkg = types.ModuleType("custom_components.cityparking")
cityparking_pkg.__path__ = [str(PACKAGE_ROOT)]
sys.modules["custom_components.cityparking"] = cityparking_pkg

from custom_components.cityparking.const import API_MODE_LEGACY, API_MODE_OFFICIAL
from custom_components.cityparking.seetyApi import EmptyResponseError, SeetyApi
from custom_components.cityparking.seetyApi.models import (
    Coords,
    SeetyLocationResponse,
    SeetyUser,
)


def _api(api_mode=API_MODE_OFFICIAL):
    api = SeetyApi.__new__(SeetyApi)
    api.api_mode = api_mode
    api.api_key = "test-api-key"
    api.geoapify_api_key = ""
    api._official_rules_cache = {}
    return api


def _coords(lat=50.8503, lon=4.3517):
    return Coords(lat=lat, lon=lon, bounds={})


def _location_response():
    return SeetyLocationResponse(
        status="OK",
        results=[
            {
                "formatted_address": "Rue Test 1",
                "countryCode": "BE",
                "geometry": {"location": {"lat": 50.8503, "lng": 4.3517}},
                "types": ["street_address"],
            }
        ],
    )


def test_official_rules_are_cached_for_same_coordinates():
    api = _api()
    api.json_get_with_retry_client = AsyncMock(
        return_value={
            "status": "OK",
            "rules": {
                "days": [1, 2, 3, 4, 5],
                "hours": ["09:00,18:00"],
                "type": "green",
                "prices": {"15": 0.5},
            },
            "mapURL": "https://map.seety.co/Rue%20Test/16",
        }
    )

    first = asyncio.run(api.getOfficialRulesForCoordinate(_coords()))
    second = asyncio.run(api.getOfficialRulesForCoordinate(_coords()))

    assert api.json_get_with_retry_client.await_count == 1
    assert second is first
    assert first.status == "OK"
    assert first.rules.type == "green"


def test_official_rules_cache_uses_rounded_coordinates():
    api = _api()
    api.json_get_with_retry_client = AsyncMock(
        return_value={
            "status": "OK",
            "rules": {"type": "green"},
        }
    )

    asyncio.run(api.getOfficialRulesForCoordinate(_coords(50.8503001, 4.3517001)))
    asyncio.run(api.getOfficialRulesForCoordinate(_coords(50.8503002, 4.3517002)))

    assert api.json_get_with_retry_client.await_count == 1


def test_official_rules_failures_are_not_cached():
    api = _api()
    api.json_get_with_retry_client = AsyncMock(
        side_effect=[
            {"status": "ZERO_RESULTS", "rules": None},
            {"status": "OK", "rules": {"type": "green"}},
        ]
    )

    with pytest.raises(EmptyResponseError):
        asyncio.run(api.getOfficialRulesForCoordinate(_coords()))

    result = asyncio.run(api.getOfficialRulesForCoordinate(_coords()))

    assert api.json_get_with_retry_client.await_count == 2
    assert result.status == "OK"


def test_official_address_info_wraps_external_rules():
    api = _api()
    api.json_get_with_retry_client = AsyncMock(
        return_value={
            "status": "OK",
            "rules": {"type": "green"},
            "mapURL": "https://map.seety.co/Rue%20Test/16",
        }
    )

    result = asyncio.run(api.getOfficialAddressSeetyInfo(_coords()))

    assert result.api_mode == API_MODE_OFFICIAL
    assert result.externalRules.status == "OK"
    assert result.externalRules.rules.type == "green"


def test_legacy_address_info_calls_legacy_seety_endpoints():
    api = _api(API_MODE_LEGACY)
    api.getSeetyToken = AsyncMock(return_value=SeetyUser(access_token="token"))
    api.getAddressForCoordinate = AsyncMock(return_value=_location_response())
    api.json_get_with_retry_client = AsyncMock(
        side_effect=[
            {
                "status": "OK",
                "rules": {
                    "days": [1, 2, 3, 4, 5],
                    "hours": ["09:00,18:00"],
                    "type": "paid",
                    "prices": {"15": 0.5},
                },
                "properties": {"closest": [50.8503, 4.3517], "type": "green"},
            },
            {"status": "OK", "rules": {}},
        ]
    )

    result = asyncio.run(api.getAddressSeetyInfo(_coords()))
    requested_urls = [
        str(call.args[0]) for call in api.json_get_with_retry_client.await_args_list
    ]

    assert result.api_mode == API_MODE_LEGACY
    assert result.user.access_token == "token"
    assert result.location.results[0].formatted_address == "Rue Test 1"
    assert api.getSeetyToken.await_count == 1
    assert api.getAddressForCoordinate.await_count == 1
    assert api.json_get_with_retry_client.await_count == 2
    assert requested_urls[0].startswith("https://api.cparkapp.com/street/rules/")
    assert requested_urls[1].startswith("https://api.cparkapp.com/street/complete/")
