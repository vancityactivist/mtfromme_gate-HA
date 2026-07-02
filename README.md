# Mt Fromme Gate — Home Assistant

A Home Assistant integration and sensor for the current parking lot closing
time at Mt Fromme (District of North Vancouver), so you can use it on
dashboards, notifications, or countdown automations.

**UPDATE JULY 2026**: Fixed, and rebuilt as a proper HACS custom integration.
DNV rebuilt their site as a client-rendered React app (SimpliCity CMS), so
scraping the rendered HTML no longer worked. The integration now calls the
CMS's underlying JSON API directly
(`simplicity-api.dnv.org/public/webpage/path/detailed/...`) instead of
scraping HTML. [GitHub Issue Link](https://github.com/vancityactivist/mtfromme_gate-HA/issues/2)

There are two ways to use this repo:

- **[HACS custom integration](#installation-hacs-recommended)** (recommended) —
  install through HACS, configure via the UI, no scripts or YAML editing, no
  Python dependencies to manage inside the container.
- **[Legacy `command_line` script](#legacy-installation-command_line-script)** —
  the original standalone `fromme.py`, for anyone who'd rather not add a
  custom integration.

## How it works

Both the integration and the standalone script request DNV's page-content API
for the ["Hiking and cycling trails in parks"](https://www.dnv.org/parks-trails-recreation/hiking-and-cycling-trails-parks)
page, find the "Parking at Fromme Mountain" table in the returned JSON, and
resolve today's (and tomorrow's) applicable closing time from the listed date
ranges — correctly handling ranges that wrap around New Year's (e.g.
October–February).

## Installation (HACS, recommended)

1. **Add this repository to HACS** as a custom repository:
   - HACS → the `⋮` menu (top right) → **Custom repositories**
   - Repository: `https://github.com/vancityactivist/mtfromme_gate-HA`
   - Category: **Integration**
   - Click **Add**

2. **Install the integration.**
   Find "Mt Fromme Gate" in HACS → Integrations, click **Download**, then
   restart Home Assistant (Settings → System → Restart, or restart the
   container: `docker restart homeassistant` on unRAID).

3. **Add the integration via the UI.**
   Settings → Devices & Services → **Add Integration** → search for
   "Mt Fromme Gate" → follow the prompt. No configuration is required — it
   just creates the entity.

4. **Verify it worked.**
   You'll get a `sensor.mt_fromme_gate_closing_time` entity with:
   - **State**: a timestamp — the *next* upcoming gate closing (today's if
     it hasn't passed yet, otherwise tomorrow's), so Lovelace can render it
     as "in 3 hours" and automations can trigger relative to it.
   - **Attribute `today_closing_time`**: today's closing time as `HH:MM`.
   - **Attribute `schedule`**: the full date-range → closing-time table, as
     fetched from DNV.

   If the entity doesn't appear or shows unavailable, check Settings →
   System → Logs for `mt_fromme_gate` errors.

## Legacy installation (`command_line` script)

If you'd rather not add a custom integration, `fromme.py` is a standalone
script you can run via a `command_line` sensor. These steps assume Home
Assistant is running in Docker on unRAID with its config directory mapped to
a host path such as `/mnt/user/appdata/homeassistant`.

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

3. **Verify `requests` is available inside the container.**
   The official Home Assistant image already ships `requests` (HA core
   depends on it), but it's worth a quick check from the unRAID host:
   ```bash
   docker exec -it homeassistant python3 -c "import requests; print('ok')"
   ```
   If that fails, install it inside the container's Python environment:
   ```bash
   docker exec -it homeassistant pip3 install requests
   ```
   Note this won't survive a container recreation/update.

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

5. **Restart the Home Assistant container** to apply the change.

6. **Verify it worked.**
   Developer Tools → States → `sensor.mt_fromme_gate_closing_time` should
   show a time like `21:00`.

### Legacy script troubleshooting

- **Run it manually first.**
  ```bash
  docker exec -it homeassistant python3 /config/scripts/fromme.py
  ```
  This should print a time like `18:00`. Any traceback points at the real
  problem (missing `requests`, network/DNS issue, or the DNV API shape has
  changed again).
- **`scan_interval: 86400`** means Home Assistant only refreshes this sensor
  once a day — restart HA or call `homeassistant.update_entity` on the
  sensor to force an immediate refresh.
- **Sensor stuck on `unknown`** usually means the command exited non-zero or
  printed nothing — check Settings → System → Logs for `command_line` errors.

## Repository structure

```
custom_components/mt_fromme_gate/   HACS-installable integration
fromme.py                           Standalone script for the legacy method
hacs.json                           HACS repository metadata
```

## Risks

Both the integration and the script call an undocumented internal API used
by the DNV website's CMS (SimpliCity), not an official public API. This may
break at any time if DNV changes their CMS, API, or page structure, with no
advance notice.

## Contributing

Feel free to fork the project, make improvements, and submit pull requests.

## License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for the full text.
