import { useState, useEffect } from 'react'

const DEFAULT_FORM = {
  balloon: '',
  payload_mass_kg: '0.5',
  mode: 'ascent_rate',
  target_ascent_rate_mps: '5',
  neck_lift_g: '500',
}

export default function BurstCalculator() {
  const [balloons, setBalloons] = useState([])
  const [form, setForm] = useState(DEFAULT_FORM)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch('/api/balloons')
      .then((r) => r.json())
      .then((data) => {
        setBalloons(data.balloons || [])
        if (data.balloons?.length) {
          setForm((f) => ({ ...f, balloon: data.balloons[0] }))
        }
      })
      .catch(() => setError('Failed to load balloon types from API.'))
  }, [])

  function handleChange(e) {
    const { name, value } = e.target
    setForm((f) => ({ ...f, [name]: value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    setResult(null)
    setLoading(true)

    const body = {
      balloon: form.balloon,
      payload_mass_kg: parseFloat(form.payload_mass_kg),
    }
    if (form.mode === 'ascent_rate') {
      body.target_ascent_rate_mps = parseFloat(form.target_ascent_rate_mps)
    } else {
      body.neck_lift_g = parseFloat(form.neck_lift_g)
    }

    try {
      const res = await fetch('/api/burst', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      const data = await res.json()
      if (!res.ok) {
        setError(data.detail || 'API error')
      } else {
        setResult(data)
      }
    } catch (err) {
      setError('Network error: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h2>Burst Calculator</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          <div className="form-group">
            <label>Balloon type</label>
            <select name="balloon" value={form.balloon} onChange={handleChange} required>
              {balloons.map((b) => (
                <option key={b} value={b}>{b}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Payload mass (kg)</label>
            <input
              type="number"
              name="payload_mass_kg"
              value={form.payload_mass_kg}
              onChange={handleChange}
              step="0.01"
              min="0.01"
              required
            />
          </div>

          <div className="form-group full-width">
            <label>Input mode</label>
            <div className="radio-group">
              <label>
                <input
                  type="radio"
                  name="mode"
                  value="ascent_rate"
                  checked={form.mode === 'ascent_rate'}
                  onChange={handleChange}
                />
                Target ascent rate
              </label>
              <label>
                <input
                  type="radio"
                  name="mode"
                  value="neck_lift"
                  checked={form.mode === 'neck_lift'}
                  onChange={handleChange}
                />
                Neck lift
              </label>
            </div>
          </div>

          {form.mode === 'ascent_rate' && (
            <div className="form-group">
              <label>Target ascent rate (m/s)</label>
              <input
                type="number"
                name="target_ascent_rate_mps"
                value={form.target_ascent_rate_mps}
                onChange={handleChange}
                step="0.1"
                min="0.1"
                required
              />
            </div>
          )}

          {form.mode === 'neck_lift' && (
            <div className="form-group">
              <label>Neck lift (g)</label>
              <input
                type="number"
                name="neck_lift_g"
                value={form.neck_lift_g}
                onChange={handleChange}
                step="1"
                min="1"
                required
              />
            </div>
          )}
        </div>

        <button type="submit" className="btn-primary" disabled={loading || !form.balloon}>
          {loading && <span className="spinner" />}
          {loading ? 'Calculating…' : 'Calculate'}
        </button>
      </form>

      {error && <div className="error-box">{error}</div>}

      {result && (
        <div className="result-box">
          <h3>Results</h3>
          <div className="result-grid">
            <div className="result-item">
              <span className="result-label">Burst Altitude</span>
              <span className="result-value">
                {result.burst_altitude_m.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                <span className="result-unit">m</span>
              </span>
            </div>
            <div className="result-item">
              <span className="result-label">Ascent Rate</span>
              <span className="result-value">
                {result.ascent_rate_mps.toFixed(2)}
                <span className="result-unit">m/s</span>
              </span>
            </div>
            <div className="result-item">
              <span className="result-label">Neck Lift</span>
              <span className="result-value">
                {result.neck_lift_g.toFixed(1)}
                <span className="result-unit">g</span>
              </span>
            </div>
            <div className="result-item">
              <span className="result-label">Helium Mass</span>
              <span className="result-value">
                {result.helium_mass_kg.toFixed(3)}
                <span className="result-unit">kg</span>
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
