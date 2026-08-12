import { useCallback, useEffect, useState } from 'react'
import { api, type Shop } from '../api/client'
import { EditableName } from '../components/EditableName'

export function ShopsPage() {
  const [shops, setShops] = useState<Shop[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.listShops()
      setShops(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudieron cargar las tiendas')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void load()
  }, [load])

  async function handleRenameShop(shopId: number, name: string) {
    const updated = await api.renameShop(shopId, name)
    setShops((prev) => prev.map((s) => (s.id === shopId ? updated : s)))
    setNotice(`Tienda renombrada a «${updated.name}»`)
  }

  async function handleRenameCamera(shopId: number, cameraId: string, name: string) {
    const updated = await api.renameCamera(shopId, cameraId, name)
    setShops((prev) =>
      prev.map((shop) => {
        if (shop.id !== shopId) return shop
        return {
          ...shop,
          cameras: shop.cameras.map((cam) => (cam.id === cameraId ? updated : cam)),
        }
      }),
    )
    setNotice(`Cámara renombrada a «${updated.name}»`)
  }

  return (
    <div>
      <header className="page-header">
        <h1>Mis tiendas</h1>
        <p>Edita el nombre de cada tienda y de las cámaras asignadas a ella.</p>
      </header>

      {notice ? <div className="success-banner">{notice}</div> : null}
      {error ? <div className="error-banner">{error}</div> : null}

      <section className="panel">
        {loading ? <p className="empty-state">Cargando tiendas…</p> : null}
        {!loading && shops.length === 0 ? (
          <p className="empty-state">
            Aún no tienes tiendas asignadas. Un administrador debe crear una tienda y
            asociarla a tu cuenta.
          </p>
        ) : null}

        <div className="shop-list">
          {shops.map((shop) => (
            <article key={shop.id} className="shop-block">
              <div className="shop-head">
                <EditableName
                  value={shop.name}
                  emphasized
                  label={`tienda ${shop.name}`}
                  onSave={(name) => handleRenameShop(shop.id, name)}
                />
                <span className="shop-meta">
                  {shop.address ? shop.address : 'Sin dirección'} · {shop.cameras.length}{' '}
                  {shop.cameras.length === 1 ? 'cámara' : 'cámaras'}
                </span>
              </div>

              {shop.cameras.length === 0 ? (
                <p className="empty-state">No hay cámaras activas en esta tienda.</p>
              ) : (
                <ul className="camera-list">
                  {shop.cameras.map((camera) => (
                    <li key={camera.id} className="camera-row">
                      <EditableName
                        value={camera.name}
                        label={`cámara ${camera.name}`}
                        onSave={(name) => handleRenameCamera(shop.id, camera.id, name)}
                      />
                      <span className="camera-id">{camera.id}</span>
                      {camera.is_active ? <span className="status-pill">Activa</span> : null}
                    </li>
                  ))}
                </ul>
              )}
            </article>
          ))}
        </div>
      </section>
    </div>
  )
}
