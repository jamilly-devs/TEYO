import { useState } from 'react'
import type { FormEvent } from 'react'
import { ApiError } from '../../api/client'
import { careerApi } from '../../api/career'
import type { JobApplication, JobApplicationStatus } from '../../api/types'
import { EmptyState, ErrorState, LoadingState } from '../../components/ScreenStates'
import { useApiResource } from '../../state/useApiResource'

const STATUS_LABEL: Record<JobApplicationStatus, string> = {
  interested: 'Interesse',
  applied: 'Aplicada',
  interviewing: 'Entrevista',
  offer: 'Proposta',
  rejected: 'Recusada',
}

const STATUS_ORDER: JobApplicationStatus[] = [
  'interested',
  'applied',
  'interviewing',
  'offer',
  'rejected',
]

function ApplicationCreateForm({
  onCreated,
}: {
  onCreated: (application: JobApplication) => void
}) {
  const [company, setCompany] = useState('')
  const [role, setRole] = useState('')
  const [appliedOn, setAppliedOn] = useState('')
  const [notes, setNotes] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      const application = await careerApi.create({
        company,
        role,
        applied_on: appliedOn || undefined,
        notes: notes || undefined,
      })
      onCreated(application)
      setCompany('')
      setRole('')
      setAppliedOn('')
      setNotes('')
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : 'Não foi possível registrar a candidatura.',
      )
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="create-form">
      <label>
        Empresa
        <input value={company} onChange={(e) => setCompany(e.target.value)} required />
      </label>
      <label>
        Cargo/vaga
        <input value={role} onChange={(e) => setRole(e.target.value)} required />
      </label>
      <label>
        Data da candidatura
        <input type="date" value={appliedOn} onChange={(e) => setAppliedOn(e.target.value)} />
      </label>
      <label>
        Observações
        <input value={notes} onChange={(e) => setNotes(e.target.value)} />
      </label>
      {error && <p role="alert">{error}</p>}
      <button type="submit" disabled={submitting}>
        {submitting ? 'Registrando…' : 'Registrar candidatura'}
      </button>
    </form>
  )
}

function ApplicationRow({
  application,
  onChanged,
}: {
  application: JobApplication
  onChanged: (application: JobApplication) => void
}) {
  async function handleStatusChange(next: JobApplicationStatus) {
    onChanged(await careerApi.update(application.id, { status: next }))
  }

  return (
    <li className="career-row">
      <span className="career-title">
        {application.company} — {application.role}
      </span>
      <select
        value={application.status}
        onChange={(e) => handleStatusChange(e.target.value as JobApplicationStatus)}
      >
        {STATUS_ORDER.map((status) => (
          <option key={status} value={status}>
            {STATUS_LABEL[status]}
          </option>
        ))}
      </select>
      {application.applied_on && <span>{application.applied_on}</span>}
    </li>
  )
}

export function CareerScreen() {
  const { status, data, error, reload, setData } = useApiResource(careerApi.list)

  return (
    <section>
      <h1>Carreira</h1>
      <p>Acompanhamento manual de candidaturas — o TEYO não busca vagas.</p>
      <ApplicationCreateForm onCreated={(a) => setData([a, ...(data ?? [])])} />

      {status === 'loading' && <LoadingState />}
      {status === 'error' && error && <ErrorState message={error} onRetry={reload} />}
      {status === 'success' && data && data.length === 0 && (
        <EmptyState message="Nenhuma candidatura registrada ainda." />
      )}
      {status === 'success' && data && data.length > 0 && (
        <ul className="career-list">
          {data.map((application) => (
            <ApplicationRow
              key={application.id}
              application={application}
              onChanged={(updated) =>
                setData((data ?? []).map((a) => (a.id === updated.id ? updated : a)))
              }
            />
          ))}
        </ul>
      )}
    </section>
  )
}
