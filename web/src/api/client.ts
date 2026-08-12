export type Role = 'admin' | 'customer'

export interface MeResponse {
  email: string
  role: Role
}

export interface CameraInfo {
  id: string
  name: string
  is_active: boolean
}

export interface Shop {
  id: number
  name: string
  address: string | null
  camera_ids: string[]
  cameras: CameraInfo[]
}

export interface TrafficPoint {
  hour: number
  count: number
}

export interface DwellSummary {
  zone_id: string
  visits: number
  avg_dwell_seconds: number
  max_dwell_seconds: number
}

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

const TOKEN_KEY = 'heatmap_token'

export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setStoredToken(token: string | null): void {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token)
  } else {
    localStorage.removeItem(TOKEN_KEY)
  }
}

async function parseError(res: Response): Promise<string> {
  try {
    const body = await res.json()
    if (typeof body?.detail === 'string') return body.detail
    if (Array.isArray(body?.detail)) {
      return body.detail.map((d: { msg?: string }) => d.msg ?? String(d)).join(', ')
    }
  } catch {
    /* ignore */
  }
  return res.statusText || 'Request failed'
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null,
): Promise<T> {
  const headers = new Headers(options.headers)
  if (!headers.has('Content-Type') && options.body) {
    headers.set('Content-Type', 'application/json')
  }
  const auth = token === undefined ? getStoredToken() : token
  if (auth) {
    headers.set('Authorization', `Bearer ${auth}`)
  }

  const res = await fetch(path, { ...options, headers })
  if (!res.ok) {
    throw new ApiError(res.status, await parseError(res))
  }
  if (res.status === 204) {
    return undefined as T
  }
  return res.json() as Promise<T>
}

export const api = {
  register(email: string, password: string) {
    return request<{ access_token: string }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }, null)
  },

  login(email: string, password: string) {
    return request<{ access_token: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }, null)
  },

  me(token?: string) {
    return request<MeResponse>('/auth/me', {}, token)
  },

  listShops() {
    return request<Shop[]>('/shops')
  },

  renameShop(shopId: number, name: string) {
    return request<Shop>(`/shops/${shopId}`, {
      method: 'PATCH',
      body: JSON.stringify({ name }),
    })
  },

  renameCamera(shopId: number, cameraId: string, name: string) {
    return request<CameraInfo>(`/shops/${shopId}/cameras/${cameraId}`, {
      method: 'PATCH',
      body: JSON.stringify({ name }),
    })
  },

  traffic(cameraId?: string) {
    const qs = cameraId ? `?camera_id=${encodeURIComponent(cameraId)}` : ''
    return request<TrafficPoint[]>(`/analytics/traffic${qs}`)
  },

  dwell(zoneId = 'entrance') {
    return request<DwellSummary>(`/analytics/dwell?zone_id=${encodeURIComponent(zoneId)}`)
  },

  heatmapLiveUrl(cameraId: string, bust = Date.now()) {
    return `/heatmap/live?camera_id=${encodeURIComponent(cameraId)}&t=${bust}`
  },

  heatmapHistoricalUrl(start: number, end: number, cameraId?: string) {
    const params = new URLSearchParams({
      start: String(start),
      end: String(end),
    })
    if (cameraId) params.set('camera_id', cameraId)
    return `/heatmap/historical?${params.toString()}`
  },
}
