import { useEffect, useMemo, useState } from 'react'
import { api, type Shop } from '../api/client'

const REFRESH_MS = 2000

export function LivePage() {
  const [shops, setShops] = useState<Shop[]>([])
  const [cameraId, setCameraId] = useState('')
  const [bust, setBust] = useState(Date.now())
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

  useEffect(() => {
    if (!cameraId) return
    const id = window.setInterval(() => setBust(Date.now()), REFRESH_MS)
    return () => window.clearInterval(id)
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

  return (
    <div>
      <header className="page-header">
        <h1>Vista en vivo</h1>
        <p>Mapa de calor en tiempo real de la cámara seleccionada.</p>
      </header>
      {error ? <div className="error-banner">{error}</div> : null}
      <section className="panel">
        <div className="toolbar">
          <div className="field">
            <label htmlFor="live-camera">Cámara</label>
            <select
              id="live-camera"
              value={cameraId}
              onChange={(e) => setCameraId(e.target.value)}
              disabled={options.length === 0}
              style={{
                padding: '0.7rem 0.85rem',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--border-default)',
                background: 'var(--bg-primary)',
                color: 'var(--text-primary)',
              }}
            >
              {options.length === 0 ? <option value="">Sin cámaras</option> : null}
              {options.map((opt) => (
                <option key={opt.id} value={opt.id}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
        </div>
        {cameraId ? (
          <img
            className="heatmap-frame"
            src={api.heatmapLiveUrl(cameraId, bust)}
            alt={`Mapa de calor en vivo de ${cameraId}`}
          />
        ) : (
          <p className="empty-state">Selecciona una cámara para ver el mapa en vivo.</p>
        )}
      </section>
    </div>
  )
}
