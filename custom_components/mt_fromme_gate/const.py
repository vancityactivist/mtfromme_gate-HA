"""Constants for the Mt Fromme Gate integration."""
from datetime import timedelta

DOMAIN = "mt_fromme_gate"

API_URL = "https://simplicity-api.dnv.org/public/webpage/path/detailed/{}"
PAGE_PATH = "/parks-trails-recreation/hiking-and-cycling-trails-parks"
HEADING_TEXT = "Parking at Fromme Mountain"

# The site's CMS occasionally uses abbreviated month names (e.g. "Sept")
# that %B-style parsing won't recognize.
MONTH_ALIASES = {
    "sept": "September",
}

UPDATE_INTERVAL = timedelta(hours=6)
REQUEST_TIMEOUT = 15
