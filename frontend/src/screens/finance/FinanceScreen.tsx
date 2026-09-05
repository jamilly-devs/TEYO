import { useState } from 'react'
import type { FormEvent } from 'react'
import { ApiError } from '../../api/client'
import { financeApi } from '../../api/finance'
import type { FinancialRecord, FinancialRecordType } from '../../api/types'
import { EmptyState, ErrorState, LoadingState } from '../../components/ScreenStates'
import { useApiResource } from '../../state/useApiResource'

function FinancialRecordCreateForm({
  onCreated,
}: {
  onCreated: (record: FinancialRecord) => void
}) {
  const [type, setType] = useState<FinancialRecordType>('expense')
  const [amount, setAmount] = useState('')
  const [date, setDate] = useState('')
  const [category, setCategory] = useState('')
  const [description, setDescription] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      const record = await financeApi.create({
        type,
        amount,
        date,
        category: category || undefined,
        description: description || undefined,
      })
      onCreated(record)
      setAmount('')
      setDate('')
      setCategory('')
      setDescription('')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Não foi possível registrar.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="create-form">
      <label>
        Tipo
        <select value={type} onChange={(e) => setType(e.target.value as FinancialRecordType)}>
          <option value="income">Entrada</option>
          <option value="expense">Saída</option>
        </select>
      </label>
      <label>
        Valor
        <input
          type="number"
          step="0.01"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          required
        />
      </label>
      <label>
        Data
        <input type="date" value={date} onChange={(e) => setDate(e.target.value)} required />
      </label>
      <label>
        Categoria
        <input value={category} onChange={(e) => setCategory(e.target.value)} />
      </label>
      <label>
        Descrição
        <input value={description} onChange={(e) => setDescription(e.target.value)} />
      </label>
      {error && <p role="alert">{error}</p>}
      <button type="submit" disabled={submitting}>
        {submitting ? 'Registrando…' : 'Registrar'}
      </button>
    </form>
  )
}

export function FinanceScreen() {
  const { status, data, error, reload, setData } = useApiResource(financeApi.list)

  function handleCreated(record: FinancialRecord) {
    setData([record, ...(data ?? [])])
  }

  return (
    <section>
      <h1>Finanças</h1>
      <FinancialRecordCreateForm onCreated={handleCreated} />

      {status === 'loading' && <LoadingState />}
      {status === 'error' && error && <ErrorState message={error} onRetry={reload} />}
      {status === 'success' && data && data.length === 0 && (
        <EmptyState message="Nenhum registro financeiro ainda. Registre o primeiro acima." />
      )}
      {status === 'success' && data && data.length > 0 && (
        <ul className="finance-list">
          {data.map((record) => (
            <li key={record.id} className="finance-row">
              <span className={`badge type-${record.type}`}>{record.type}</span>
              <span>{record.amount}</span>
              <span>{record.date}</span>
              {record.category && <span className="badge">{record.category}</span>}
              {record.description && <span>{record.description}</span>}
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
