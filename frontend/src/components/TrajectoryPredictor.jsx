import { useState, useEffect } from 'react'
import { MapContainer, TileLayer, Polyline, Marker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'

const burstIcon = new L.DivIcon({
  html: '<div style="font-size:22px;line-height:1">💥</div>',
  className: '',
  iconAnchor: [11, 11],
})

const launchIcon = new L.DivIcon({
  html: '<div style="font-size:22px;line-height:1">🚀</div>',
  className: '',
  iconAnchor: [11, 11],
})

const landingIcon = new L.DivIcon({
  html: '<div style="font-size:22px;line-height:1">📍</div>',
  className: '',
  iconAnchor: [11, 22],
})

function now() {
  const d = new Date()
  d.setSeconds(0, 0)
  return d.toISOString().slice(0, 16)
}

const DEFAULT_FORM = {
  launch_lat: '51.5',
  launch_lon: '-1.8',
  launch_alt_m: '0',
  launch_time: now(),
  ascent_rate_mps: '5',
  burst_alt_m: '30000',
  descent_rate_mps: '6',
}

function FitBounds({ points }) {
  const map = useMap()
  useEffect(() => {
    if (points.length > 0) {
      const bounds = L.latLngBounds(points.map((p) => [p.lat, p.lon]))
      map.fitBounds(bounds, { padding: [30, 30] })
    }
  }, [points, map])
  return null
}

function fmtCoord(v) {
  return v.toFixed(4)
}

function fmtAlt(m) {
  return (m / 1000).toFixed(2) + ' km'
}

function fmtTime(iso) {
  return new Date(iso).toLocaleTimeString()
}

export default function TrajectoryPredictor() {
  const [form, setForm] = useState(DEFAULT_FORM)
  const [loading, setLoading] = useState(false)
  const [trajectory, setTrajectory] = useState(null)
  const [error, setError] = useState(null)

  function handleChange(e) {
    const { name, value } = e.target
    setForm((f) => ({ ...f, [name]: value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    setTrajectory(null)
    setLoading(true)

    const body = {
      launch_lat: parseFloat(form.launch_lat),
      launch_lon: parseFloat(form.launch_lon),
      launch_alt_m: parseFloat(form.launch_alt_m),
      launch_time: new Date(form.launch_time).toISOString(),
      ascent_rate_mps: parseFloat(form.ascent_rate_mps),
      burst_alt_m: parseFloat(form.burst_alt_m),
      descent_rate_mps: parseFloat(form.descent_rate_mps),
      model: 'gfs',
    }

    try {
      const res = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      const data = await res.json()
      if (!res.ok) {
        setError(data.detail || 'API error')
      } else {
        setTrajectory(data)
      }
    } catch (err) {
      setError('Network error: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const mapCenter = [parseFloat(form.launch_lat) || 51.5, parseFloat(form.launch_lon) || -1.8]
  const points = trajectory?.points ?? []
  const positions = points.map((p) => [p.lat, p.lon])

  return (
    <div className="card">
      <h2>Trajectory Predictor</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          <div className="form-group">
            <label>Launch latitude</label>
            <input
              type="number"
              name="launch_lat"
              value={form.launch_lat}
              onChange={handleChange}
              step="0.0001"
              min="-90"
              max="90"
              required
            />
          </div>
          <div className="form-group">
            <label>Launch longitude</label>
            <input
              type="number"
              name="launch_lon"
              value={form.launch_lon}
              onChange={handleChange}
              step="0.0001"
              min="-180"
              max="180"
              required
            />
          </div>
          <div className="form-group">
            <label>Launch altitude (m)</label>
            <input
              type="number"
              name="launch_alt_m"
              value={form.launch_alt_m}
              onChange={handleChange}
              step="1"
              min="0"
              required
            />
          </div>
          <div className="form-group">
            <label>Launch time (UTC)</label>
            <input
              type="datetime-local"
              name="launch_time"
              value={form.launch_time}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label>Ascent rate (m/s)</label>
            <input
              type="number"
              name="ascent_rate_mps"
              value={form.ascent_rate_mps}
              onChange={handleChange}
              step="0.1"
              min="0.1"
              required
            />
          </div>
          <div className="form-group">
            <label>Burst altitude (m)</label>
            <input
              type="number"
              name="burst_alt_m"
              value={form.burst_alt_m}
              onChange={handleChange}
              step="100"
              min="1000"
              required
            />
          </div>
          <div className="form-group">
            <label>Descent rate (m/s)</label>
            <input
              type="number"
              name="descent_rate_mps"
              value={form.descent_rate_mps}
              onChange={handleChange}
              step="0.1"
              min="0.1"
              required
            />
          </div>
        </div>

        <button type="submit" className="btn-primary" disabled={loading}>
          {loading && <span className="spinner" />}
          {loading ? 'Predicting…' : 'Predict Flight'}
        </button>
      </form>

      {error && <div className="error-box">{error}</div>}

      <div className="map-container">
        <MapContainer center={mapCenter} zoom={7} style={{ height: '100%', width: '100%' }}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {points.length > 0 && (
            <>
              <Polyline positions={positions} color="#4f6ef7" weight={2.5} />
              <Marker position={[points[0].lat, points[0].lon]} icon={launchIcon}>
                <Popup>
                  <strong>Launch</strong><br />
                  {fmtCoord(points[0].lat)}, {fmtCoord(points[0].lon)}<br />
                  Alt: {fmtAlt(points[0].alt_m)}<br />
                  Time: {fmtTime(points[0].t)}
                </Popup>
              </Marker>
              {trajectory.burst && (
                <Marker position={[trajectory.burst.lat, trajectory.burst.lon]} icon={burstIcon}>
                  <Popup>
                    <strong>Burst</strong><br />
                    {fmtCoord(trajectory.burst.lat)}, {fmtCoord(trajectory.burst.lon)}<br />
                    Alt: {fmtAlt(trajectory.burst.alt_m)}<br />
                    Time: {fmtTime(trajectory.burst.t)}
                  </Popup>
                </Marker>
              )}
              {trajectory.landing && (
                <Marker position={[trajectory.landing.lat, trajectory.landing.lon]} icon={landingIcon}>
                  <Popup>
                    <strong>Landing</strong><br />
                    {fmtCoord(trajectory.landing.lat)}, {fmtCoord(trajectory.landing.lon)}<br />
                    Alt: {fmtAlt(trajectory.landing.alt_m)}<br />
                    Time: {fmtTime(trajectory.landing.t)}
                  </Popup>
                </Marker>
              )}
              <FitBounds points={points} />
            </>
          )}
        </MapContainer>
      </div>

      {trajectory && (
        <div className="trajectory-info">
          <span className="info-chip">
            Points: <strong>{points.length}</strong>
          </span>
          {trajectory.burst && (
            <span className="info-chip">
              Burst alt: <strong>{fmtAlt(trajectory.burst.alt_m)}</strong>
            </span>
          )}
          {trajectory.landing && (
            <span className="info-chip">
              Landing: <strong>{fmtCoord(trajectory.landing.lat)}, {fmtCoord(trajectory.landing.lon)}</strong>
            </span>
          )}
          {trajectory.forecast_cycle && (
            <span className="info-chip">
              Forecast: <strong>{new Date(trajectory.forecast_cycle).toUTCString()}</strong>
            </span>
          )}
        </div>
      )}
    </div>
  )
}
