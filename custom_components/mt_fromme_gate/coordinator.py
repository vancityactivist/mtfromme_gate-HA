"""Data update coordinator for the Mt Fromme Gate integration."""
from __future__ import annotations

import asyncio
import calendar
import logging
from datetime import date, datetime, time, timedelta
from typing import Any
from urllib.parse import quote

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    API_URL,
    HEADING_TEXT,
    MONTH_ALIASES,
    PAGE_PATH,
    REQUEST_TIMEOUT,
    UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


def _node_text(node: dict[str, Any]) -> str:
    """Flatten a ProseMirror/TipTap rich-text node into plain text."""
    if "text" in node:
        return node["text"]
    return "".join(_node_text(child) for child in node.get("content", []))


def _month_day_to_date(text: str, year: int) -> date:
    """Parse a "Month D" string into a date, tolerating known data quirks."""
    parts = text.strip().split()
    month_name, day = parts[0], int(parts[1])
    month_name = MONTH_ALIASES.get(month_name.lower(), month_name)
    parsed = datetime.strptime(f"{month_name} {year}", "%B %Y")
    last_day = calendar.monthrange(year, parsed.month)[1]
    day = min(day, last_day)  # clamp invalid days like "Sept 31"
    return parsed.replace(day=day).date()


def _closing_time_str_for_date(closing_times: dict[str, str], target: date) -> str | None:
    """Return the "6pm"-style closing time that applies on the given date."""
    for date_range, time_str in closing_times.items():
        start_text, end_text = date_range.split(" to ")
        start = _month_day_to_date(start_text, target.year)
        end = _month_day_to_date(end_text, target.year)

        # Ranges that wrap around New Year's (e.g. Oct 1 to Feb 28): check
        # both the "started last year" and "ends next year" interpretations.
        if end < start:
            start_prev = start.replace(year=start.year - 1)
            if start_prev <= target <= end:
                start = start_prev
            else:
                end = end.replace(year=end.year + 1)

        if start <= target <= end:
            return time_str
    return None


def _parse_clock_time(time_str: str) -> time:
    return datetime.strptime(time_str, "%I%p").time()


class MtFrommeGateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetches and parses the DNV parking closing-time schedule."""

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="Mt Fromme Gate",
            update_interval=UPDATE_INTERVAL,
        )
        self._session = async_get_clientsession(hass)

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            closing_times = await self._fetch_gate_closing_times()
        except (aiohttp.ClientError, TimeoutError) as err:
            raise UpdateFailed(f"Error communicating with DNV: {err}") from err
        except (KeyError, IndexError, StopIteration, ValueError) as err:
            raise UpdateFailed(f"Unexpected page content from DNV: {err}") from err

        now = dt_util.now()
        today_time_str = _closing_time_str_for_date(closing_times, now.date())
        if today_time_str is None:
            raise UpdateFailed("Could not determine today's closing time from schedule")

        today_closing = datetime.combine(
            now.date(), _parse_clock_time(today_time_str), tzinfo=now.tzinfo
        )
        if today_closing > now:
            next_closing = today_closing
        else:
            tomorrow = now.date() + timedelta(days=1)
            tomorrow_time_str = _closing_time_str_for_date(closing_times, tomorrow)
            if tomorrow_time_str is None:
                raise UpdateFailed("Could not determine tomorrow's closing time from schedule")
            next_closing = datetime.combine(
                tomorrow, _parse_clock_time(tomorrow_time_str), tzinfo=now.tzinfo
            )

        return {
            "next_closing": next_closing,
            "today_closing_time": today_time_str,
            "schedule": closing_times,
        }

    async def _fetch_gate_closing_times(self) -> dict[str, str]:
        encoded_path = quote(PAGE_PATH, safe="")
        async with asyncio.timeout(REQUEST_TIMEOUT):
            async with self._session.get(API_URL.format(encoded_path)) as response:
                response.raise_for_status()
                data = await response.json(content_type=None)

        body_field = next(f for f in data["model"]["fields"] if f["name"] == "body")
        components = body_field["values"][0]["value"]

        for component in components:
            if "richtext" not in component:
                continue
            found_heading = False
            for node in component["richtext"]["content"]:
                if node["type"] == "heading" and _node_text(node).strip() == HEADING_TEXT:
                    found_heading = True
                    continue
                if found_heading and node["type"] == "table":
                    closing_times: dict[str, str] = {}
                    for row in node["content"][1:]:  # skip header row
                        date_range = _node_text(row["content"][0]).strip()
                        time_str = _node_text(row["content"][1]).strip()
                        closing_times[date_range] = time_str
                    return closing_times

        raise UpdateFailed(f"Could not find '{HEADING_TEXT}' table in page content")
