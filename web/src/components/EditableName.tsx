import { useEffect, useRef, useState } from 'react'

interface EditableNameProps {
  value: string
  onSave: (next: string) => Promise<void>
  label?: string
  emphasized?: boolean
}

export function EditableName({ value, onSave, label, emphasized = false }: EditableNameProps) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(value)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    setDraft(value)
  }, [value])

  useEffect(() => {
    if (editing) {
      inputRef.current?.focus()
      inputRef.current?.select()
    }
  }, [editing])

  async function commit() {
    const next = draft.trim()
    if (!next) {
      setError('El nombre no puede estar vacío')
      return
    }
    if (next === value) {
      setEditing(false)
      setError(null)
      return
    }
    setSaving(true)
    setError(null)
    try {
      await onSave(next)
      setEditing(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo guardar')
    } finally {
      setSaving(false)
    }
  }

  if (!editing) {
    return (
      <div className="editable-name">
        {emphasized ? <strong>{value}</strong> : <span className="name-text">{value}</span>}
        <button
          type="button"
          className="btn btn-ghost btn-sm"
          onClick={() => setEditing(true)}
          aria-label={label ? `Editar ${label}` : 'Editar nombre'}
        >
          Renombrar
        </button>
      </div>
    )
  }

  return (
    <div className="editable-name">
      <input
        ref={inputRef}
        value={draft}
        disabled={saving}
        maxLength={128}
        aria-label={label ?? 'Nombre'}
        onChange={(e) => setDraft(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') void commit()
          if (e.key === 'Escape') {
            setDraft(value)
            setEditing(false)
            setError(null)
          }
        }}
      />
      <button type="button" className="btn btn-primary btn-sm" disabled={saving} onClick={() => void commit()}>
        {saving ? 'Guardando…' : 'Guardar'}
      </button>
      <button
        type="button"
        className="btn btn-ghost btn-sm"
        disabled={saving}
        onClick={() => {
          setDraft(value)
          setEditing(false)
          setError(null)
        }}
      >
        Cancelar
      </button>
      {error ? <span className="error-banner" style={{ margin: 0, padding: '0.35rem 0.6rem' }}>{error}</span> : null}
    </div>
  )
}
