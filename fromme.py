import calendar
import datetime
import urllib.parse

import requests

API_URL = "https://simplicity-api.dnv.org/public/webpage/path/detailed/{}"
PAGE_PATH = "/parks-trails-recreation/hiking-and-cycling-trails-parks"
HEADING_TEXT = "Parking at Fromme Mountain"

# The site's CMS occasionally uses abbreviated month names (e.g. "Sept")
# that datetime's %B directive won't parse.
MONTH_ALIASES = {
    "sept": "September",
}


def _node_text(node):
    if "text" in node:
        return node["text"]
    return "".join(_node_text(child) for child in node.get("content", []))


def fetch_gate_closing_times():
    encoded_path = urllib.parse.quote(PAGE_PATH, safe="")
    response = requests.get(API_URL.format(encoded_path), timeout=15)
    response.raise_for_status()
    data = response.json()

    body_field = next(f for f in data["model"]["fields"] if f["name"] == "body")
    components = body_field["values"][0]["value"]

    closing_times = {}
    for component in components:
        if "richtext" not in component:
            continue
        nodes = component["richtext"]["content"]
        found_heading = False
        for node in nodes:
            if node["type"] == "heading" and _node_text(node).strip() == HEADING_TEXT:
                found_heading = True
                continue
            if found_heading and node["type"] == "table":
                for row in node["content"][1:]:  # skip header row
                    date_range = _node_text(row["content"][0]).strip()
                    time_str = _node_text(row["content"][1]).strip()
                    closing_times[date_range] = time_str
                return closing_times

    raise RuntimeError(f"Could not find '{HEADING_TEXT}' table in page content")


def _parse_month_day(text, year):
    text = text.strip()
    parts = text.split()
    month_name, day = parts[0], int(parts[1])
    month_name = MONTH_ALIASES.get(month_name.lower(), month_name)
    date = datetime.datetime.strptime(f"{month_name} {year}", "%B %Y")
    last_day = calendar.monthrange(year, date.month)[1]
    day = min(day, last_day)  # clamp invalid days like "Sept 31"
    return date.replace(day=day)


def get_current_closing_time(closing_times):
    now = datetime.datetime.now()
    for date_range, time in closing_times.items():
        start_text, end_text = date_range.split(" to ")
        start_date = _parse_month_day(start_text, now.year)
        end_date = _parse_month_day(end_text, now.year).replace(hour=23, minute=59, second=59)

        # Adjust for ranges that wrap around New Year's (e.g. Oct 1 to Feb 28):
        # check both the "started last year, ends this year" and "started this
        # year, ends next year" interpretations.
        if end_date < start_date:
            if start_date.replace(year=start_date.year - 1) <= now <= end_date:
                start_date = start_date.replace(year=start_date.year - 1)
            else:
                end_date = end_date.replace(year=end_date.year + 1)

        if start_date <= now <= end_date:
            # Convert time to 24-hour format
            closing_time_24hr = datetime.datetime.strptime(time, "%I%p").strftime("%H:%M")
            return closing_time_24hr
    return "Closing time not found"


def main():
    closing_times = fetch_gate_closing_times()
    current_closing_time = get_current_closing_time(closing_times)
    print(current_closing_time)


if __name__ == "__main__":
    main()
