import { useCallback, useEffect, useState } from 'react'
import { ApiError } from '../api/client'

export type ResourceStatus = 'loading' | 'error' | 'success'

export interface ApiResource<T> {
  status: ResourceStatus
  data: T | null
  error: string | null
  reload: () => void
  setData: (data: T) => void
}

export function useApiResource<T>(fetcher: () => Promise<T>): ApiResource<T> {
  const [status, setStatus] = useState<ResourceStatus>('loading')
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(() => {
    setStatus('loading')
    fetcher()
      .then((result) => {
        setData(result)
        setStatus('success')
      })
      .catch((err) => {
        setError(err instanceof ApiError ? err.message : 'Erro inesperado.')
        setStatus('error')
      })
    // fetcher is expected to be stable (defined inline per-call-site); this
    // hook intentionally reloads only on mount or on an explicit reload().
  }, [])

  useEffect(() => {
    load()
  }, [load])

  return { status, data, error, reload: load, setData }
}
