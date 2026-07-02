# Mt Fromme Gate Closing Time Home Assistant Sensor

A Home Assistant `command_line` sensor that fetches the current parking lot
closing time for Mt Fromme (District of North Vancouver) and exposes it as a
24-hour time string (e.g. `21:00`), so you can use it for dashboards,
notifications, or countdown automations.

**UPDATE JULY 2026**: Fixed. DNV rebuilt their site as a client-rendered React
app (SimpliCity CMS), so scraping the rendered HTML no longer worked. The
script now calls the CMS's underlying JSON API directly
(`simplicity-api.dnv.org/public/webpage/path/detailed/...`) instead of
scraping HTML. [GitHub Issue Link](https://github.com/vancityactivist/mtfromme_gate-HA/issues/2)

## How it works

`fromme.py` requests DNV's page-content API for the
["Hiking and cycling trails in parks"](https://www.dnv.org/parks-trails-recreation/hiking-and-cycling-trails-parks)
page, finds the "Parking at Fromme Mountain" table in the returned JSON, and
matches today's date against the listed date ranges to print the closing time
in 24-hour format (e.g. `18:00`).

## Requirements

- Home Assistant (any install method)
- Python 3 with the `requests` package available to whatever runs the script

## Installation (Home Assistant in Docker on unRAID)

These steps assume you're running the official Home Assistant container
(e.g. via unRAID's Community Applications) with its config directory mapped
to a host path such as `/mnt/user/appdata/homeassistant`.

1. **Find your HA config share.**
   In the unRAID UI, go to the Home Assistant container's settings and note
   the host path mapped to the container's `/config` (typically
   `/mnt/user/appdata/homeassistant`).

2. **Create a `scripts` folder and copy the script in.**
   Using the unRAID terminal, a file manager plugin (Krusader), or an SMB
   share to that path:
   ```bash
   mkdir -p /mnt/user/appdata/homeassistant/scripts
   cd /mnt/user/appdata/homeassistant/scripts
   curl -O https://raw.githubusercontent.com/vancityactivist/mtfromme_gate-HA/main/fromme.py
   ```
   (Or clone the repo and copy `fromme.py` into that folder.)

3. **Verify `requests` is available inside the container.**
   The official Home Assistant image already ships `requests` (HA core
   depends on it), but it's worth a quick check from the unRAID host:
   ```bash
   docker exec -it homeassistant python3 -c "import requests; print('ok')"
   ```
   If that fails, install it inside the container's Python environment, e.g.:
   ```bash
   docker exec -it homeassistant pip3 install requests
   ```
   Note this won't survive a container recreation/update — if you hit this,
   consider a startup script or a custom Dockerfile layer instead.

4. **Add the sensor to `configuration.yaml`.**
   Edit `/mnt/user/appdata/homeassistant/configuration.yaml` (same folder as
   `scripts/`) and add:
   ```yaml
   command_line:
     - sensor:
         name: mt_fromme_gate_closing_time
         command: "python3 /config/scripts/fromme.py"
         scan_interval: 86400
   ```
   Note the path is `/config/scripts/fromme.py` — that's the path *inside the
   container*, which is where `/mnt/user/appdata/homeassistant` is mounted.

5. **Restart the Home Assistant container** (Docker tab in unRAID, or
   `docker restart homeassistant`) to apply the change.

6. **Verify it worked.**
   In Home Assistant, go to **Developer Tools → States** and search for
   `sensor.mt_fromme_gate_closing_time`. Its state should be a time like
   `21:00`. If it instead shows `unknown` or an error, see
   [Troubleshooting](#troubleshooting) below.

## Post-Installation

Once installed, add the sensor to your Home Assistant dashboard to monitor
the Mt Fromme gate closing time from your home screen, or reference
`sensor.mt_fromme_gate_closing_time` in automations (e.g. a notification an
hour before closing).

![Sensor Card](https://images2.imgbox.com/29/a7/Fi85HIVc_o.png)

![Example](https://images2.imgbox.com/ad/09/DVDFeLtb_o.png)

## Troubleshooting

- **Run it manually first.** From the unRAID host:
  ```bash
  docker exec -it homeassistant python3 /config/scripts/fromme.py
  ```
  This should print a time like `18:00`. Any traceback will point at the
  real problem (missing `requests`, network/DNS issue, or the DNV API
  shape has changed again).
- **`scan_interval: 86400`** means Home Assistant only refreshes this sensor
  once a day — after editing the script, restart HA or call
  `homeassistant.update_entity` on the sensor to force an immediate refresh.
- **Sensor stuck on `unknown`** usually means the command exited non-zero or
  printed nothing — check the Home Assistant logs (Settings → System → Logs)
  for `command_line` errors.

## Features

- **Automatic updates**: the sensor refetches DNV's data once per day.
- **24-hour output**: returns a plain `HH:MM` string suitable for countdowns,
  automations, or complications (e.g. an Apple Watch face).
- **Handles year wrap-around**: date ranges spanning New Year's (e.g.
  October–February) are resolved correctly regardless of the current month.

## Risks

This script calls an undocumented internal API used by the DNV website's CMS
(SimpliCity), not an official public API. It may break at any time if DNV
changes their CMS, API, or page structure, with no advance notice.

## Contributing

Feel free to fork the project, make improvements, and submit pull requests.

## License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for the full text.
