# Error on Trajectory Predictor

### [x] Step: Fix longitude conversion bug

The `launch_longitude` parameter in `balloon_predictor/tawhiri.py` was applying `% 360` to the longitude value, converting negative longitudes (e.g., `-1.8`) to their 0–360 equivalent (e.g., `358.2`). The Sondehub Tawhiri API expects longitude in the `-180` to `180` range and returns a 400 Bad Request for values outside that range. Removed the `% 360` modulo so the raw longitude is passed directly.

### [x] Step: Fix invalid dataset parameter

The payload was sending `dataset=gfs` (a string literal) but the Tawhiri API only accepts either no `dataset` parameter (auto-selects latest GFS cycle) or a specific datetime string (e.g., `2026-04-23T12:00:00Z`). Removed `dataset` from the request payload so the API auto-selects the latest available GFS forecast cycle.
