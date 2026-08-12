import { useEffect, useMemo, useState } from 'react'
import { api, type DwellSummary, type Shop, type TrafficPoint } from '../api/client'

export function AnalyticsPage() {
  const [shops, setShops] = useState<Shop[]>([])
  const [cameraId, setCameraId] = useState('')
  const [traffic, setTraffic] = useState<TrafficPoint[]>([])
  const [dwell, setDwell] = useState<DwellSummary | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    async function loadShops() {
      try {
        const data = await api.listShops()
        if (cancelled) return
        setShops(data)
        const first = data.flatMap((s) => s.cameras)[0]
        if (first) setCameraId((prev) => prev || first.id)
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Error al cargar cámaras')
        }
      }
    }
    void loadShops()
    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    let cancelled = false
    async function loadAnalytics() {
      try {
        const [trafficData, dwellData] = await Promise.all([
          api.traffic(cameraId || undefined),
          api.dwell('entrance'),
        ])
        if (cancelled) return
        setTraffic(trafficData)
        setDwell(dwellData)
        setError(null)
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Error al cargar analítica')
        }
      }
    }
    void loadAnalytics()
    return () => {
      cancelled = true
    }
  }, [cameraId])

  const options = useMemo(
    () =>
      shops.flatMap((shop) =>
        shop.cameras.map((cam) => ({
          id: cam.id,
          label: `${shop.name} · ${cam.name}`,
        })),
      ),
    [shops],
  )

  const totalEvents = traffic.reduce((sum, p) => sum + p.count, 0)
  const peak = traffic.reduce(
    (best, p) => (p.count > best.count ? p : best),
    { hour: 0, count: 0 },
  )

  return (
    <div>
      <header className="page-header">
        <h1>Analítica</h1>
        <p>Resumen de tráfico horario y tiempos de permanencia por zona.</p>
      </header>
      {error ? <div className="error-banner">{error}</div> : null}
      <section className="panel">
        <div className="toolbar">
          <div className="field">
            <label htmlFor="analytics-camera">Cámara</label>
            <select
              id="analytics-camera"
              value={cameraId}
              onChange={(e) => setCameraId(e.target.value)}
              style={{
                padding: '0.7rem 0.85rem',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--border-default)',
                background: 'var(--bg-primary)',
                color: 'var(--text-primary)',
              }}
            >
              <option value="">Todas</option>
              {options.map((opt) => (
                <option key={opt.id} value={opt.id}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="stats-grid">
          <div className="stat">
            <div className="stat-label">Eventos (24 h)</div>
            <div className="stat-value">{totalEvents}</div>
          </div>
          <div className="stat">
            <div className="stat-label">Pico horario</div>
            <div className="stat-value">{peak.count}</div>
          </div>
          <div className="stat">
            <div className="stat-label">Visitas zona</div>
            <div className="stat-value">{dwell?.visits ?? 0}</div>
          </div>
          <div className="stat">
            <div className="stat-label">Permanencia media</div>
            <div className="stat-value">
              {dwell ? `${dwell.avg_dwell_seconds.toFixed(1)} s` : '—'}
            </div>
          </div>
        </div>

        <h2>Tráfico por hora</h2>
        {traffic.length === 0 ? (
          <p className="empty-state">Sin datos de tráfico en el periodo.</p>
        ) : (
          <ul className="camera-list">
            {traffic.slice(-12).map((point) => (
              <li key={point.hour} className="camera-row">
                <span className="camera-id">
                  {new Date(point.hour * 1000).toLocaleString()}
                </span>
                <strong style={{ marginLeft: 'auto' }}>{point.count}</strong>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}
