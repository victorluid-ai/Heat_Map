import { useEffect, useMemo, useState } from 'react'
import { api, type Shop } from '../api/client'

export function LivePage() {
  const [shops, setShops] = useState<Shop[]>([])
  const [cameraId, setCameraId] = useState('')
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

  return (
    <div>
      <header className="page-header">
        <h1>Vista en vivo</h1>
        <p>Vídeo continuo de la cámara, con mapa de calor y tracks identificados.</p>
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
            key={cameraId}
            className="live-stream"
            src={api.streamUrl(cameraId)}
            alt={`Vídeo en directo de ${cameraId}`}
          />
        ) : (
          <p className="empty-state">
            No hay cámaras asignadas a tus tiendas. Un administrador debe asociar una cámara.
          </p>
        )}
      </section>
    </div>
  )
}
