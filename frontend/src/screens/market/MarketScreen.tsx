import { useState } from 'react'
import type { FormEvent } from 'react'
import { ApiError } from '../../api/client'
import { marketApi } from '../../api/market'
import type { MarketItem } from '../../api/types'
import { ConfirmDialog } from '../../components/ConfirmDialog'
import { EmptyState, ErrorState, LoadingState } from '../../components/ScreenStates'
import { useApiResource } from '../../state/useApiResource'

function MarketItemCreateForm({ onCreated }: { onCreated: (item: MarketItem) => void }) {
  const [name, setName] = useState('')
  const [category, setCategory] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      const item = await marketApi.create({ name, category: category || undefined })
      onCreated(item)
      setName('')
      setCategory('')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Não foi possível adicionar o item.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="create-form">
      <label>
        Item
        <input value={name} onChange={(e) => setName(e.target.value)} required />
      </label>
      <label>
        Categoria
        <input value={category} onChange={(e) => setCategory(e.target.value)} />
      </label>
      {error && <p role="alert">{error}</p>}
      <button type="submit" disabled={submitting}>
        {submitting ? 'Adicionando…' : 'Adicionar'}
      </button>
    </form>
  )
}

function MarketItemRow({
  item,
  onChanged,
  onDeleted,
}: {
  item: MarketItem
  onChanged: (item: MarketItem) => void
  onDeleted: (id: number) => void
}) {
  const [confirmingDelete, setConfirmingDelete] = useState(false)
  const [busy, setBusy] = useState(false)

  async function toggleStatus() {
    setBusy(true)
    try {
      const nextStatus = item.status === 'active' ? 'purchased' : 'active'
      const updated = await marketApi.updateStatus(item.id, nextStatus)
      onChanged(updated)
    } finally {
      setBusy(false)
    }
  }

  async function handleDelete() {
    setBusy(true)
    try {
      await marketApi.remove(item.id)
      onDeleted(item.id)
    } finally {
      setBusy(false)
      setConfirmingDelete(false)
    }
  }

  return (
    <li className="market-row">
      <span className="market-name">{item.name}</span>
      {item.category && <span className="badge">{item.category}</span>}
      <span className={`badge status-${item.status}`}>{item.status}</span>
      <button type="button" onClick={toggleStatus} disabled={busy}>
        {item.status === 'active' ? 'Marcar como comprado' : 'Marcar como ativo'}
      </button>
      <button type="button" onClick={() => setConfirmingDelete(true)} disabled={busy}>
        Excluir
      </button>
      {confirmingDelete && (
        <ConfirmDialog
          message={`Excluir "${item.name}" da lista?`}
          onConfirm={handleDelete}
          onCancel={() => setConfirmingDelete(false)}
        />
      )}
    </li>
  )
}

export function MarketScreen() {
  const { status, data, error, reload, setData } = useApiResource(marketApi.list)

  function handleCreated(item: MarketItem) {
    setData([item, ...(data ?? [])])
  }

  function handleChanged(item: MarketItem) {
    setData((data ?? []).map((i) => (i.id === item.id ? item : i)))
  }

  function handleDeleted(id: number) {
    setData((data ?? []).filter((i) => i.id !== id))
  }

  return (
    <section>
      <h1>Mercado</h1>
      <MarketItemCreateForm onCreated={handleCreated} />

      {status === 'loading' && <LoadingState />}
      {status === 'error' && error && <ErrorState message={error} onRetry={reload} />}
      {status === 'success' && data && data.length === 0 && (
        <EmptyState message="Lista de mercado vazia. Adicione o primeiro item acima." />
      )}
      {status === 'success' && data && data.length > 0 && (
        <ul className="market-list">
          {data.map((item) => (
            <MarketItemRow
              key={item.id}
              item={item}
              onChanged={handleChanged}
              onDeleted={handleDeleted}
            />
          ))}
        </ul>
      )}
    </section>
  )
}
