import { useEffect, useMemo, useState } from 'react'
import { api, type Shop } from '../api/client'

export function HistoricalPage() {
  const [shops, setShops] = useState<Shop[]>([])
  const [cameraId, setCameraId] = useState('')
  const [hours, setHours] = useState(24)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    async function load() {
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
    void load()
    return () => {
      cancelled = true
    }
  }, [])

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

  const end = Date.now() / 1000
  const start = end - hours * 3600
  const imageUrl = cameraId
    ? api.heatmapHistoricalUrl(start, end, cameraId)
    : api.heatmapHistoricalUrl(start, end)

  return (
    <div>
      <header className="page-header">
        <h1>Análisis histórico</h1>
        <p>Densidad acumulada de tráfico en el intervalo seleccionado.</p>
      </header>
      {error ? <div className="error-banner">{error}</div> : null}
      <section className="panel">
        <div className="toolbar">
          <div className="field">
            <label htmlFor="hist-camera">Cámara</label>
            <select
              id="hist-camera"
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
          <div className="field">
            <label htmlFor="hist-hours">Últimas horas</label>
            <select
              id="hist-hours"
              value={hours}
              onChange={(e) => setHours(Number(e.target.value))}
              style={{
                padding: '0.7rem 0.85rem',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--border-default)',
                background: 'var(--bg-primary)',
                color: 'var(--text-primary)',
              }}
            >
              <option value={6}>6 h</option>
              <option value={12}>12 h</option>
              <option value={24}>24 h</option>
              <option value={72}>72 h</option>
            </select>
          </div>
        </div>
        <img
          key={imageUrl}
          className="heatmap-frame"
          src={imageUrl}
          alt="Mapa de calor histórico"
        />
      </section>
    </div>
  )
}
