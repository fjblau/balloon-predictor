# Error on Trajectory Predictor

### [x] Step: Fix longitude conversion bug

The `launch_longitude` parameter in `balloon_predictor/tawhiri.py` was applying `% 360` to the longitude value, converting negative longitudes (e.g., `-1.8`) to their 0–360 equivalent (e.g., `358.2`). The Sondehub Tawhiri API expects longitude in the `-180` to `180` range and returns a 400 Bad Request for values outside that range. Removed the `% 360` modulo so the raw longitude is passed directly.
