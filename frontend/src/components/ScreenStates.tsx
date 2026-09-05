import type { ReactNode } from 'react'

export function LoadingState({ label = 'Carregando…' }: { label?: string }) {
  return <p role="status">{label}</p>
}

export function ErrorState({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div role="alert" className="error-state">
      <p>Não foi possível carregar: {message}</p>
      <button type="button" onClick={onRetry}>
        Tentar de novo
      </button>
    </div>
  )
}

export function EmptyState({ message, children }: { message: string; children?: ReactNode }) {
  return (
    <div className="empty-state">
      <p>{message}</p>
      {children}
    </div>
  )
}
