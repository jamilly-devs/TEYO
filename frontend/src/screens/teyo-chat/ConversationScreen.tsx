import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { ApiError } from '../../api/client'
import { conversationApi } from '../../api/conversation'
import type { ConversationMessage } from '../../api/types'
import { ErrorState, LoadingState } from '../../components/ScreenStates'
import { useApiResource } from '../../state/useApiResource'

let temporaryIdCounter = -1

export function ConversationScreen() {
  const history = useApiResource(conversationApi.history)
  const [messages, setMessages] = useState<ConversationMessage[]>([])
  const [draft, setDraft] = useState('')
  const [sending, setSending] = useState(false)
  const [sendError, setSendError] = useState<string | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (history.status === 'success' && history.data) {
      setMessages(history.data)
    }
  }, [history.status, history.data])

  useEffect(() => {
    // jsdom (testes) não implementa scrollIntoView — guard evita quebrar lá.
    bottomRef.current?.scrollIntoView?.({ block: 'end' })
  }, [messages])

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    const text = draft.trim()
    if (!text || sending) return

    setSendError(null)
    setDraft('')
    setMessages((current) => [
      ...current,
      {
        id: temporaryIdCounter--,
        role: 'user',
        content: text,
        created_at: new Date().toISOString(),
      },
    ])

    setSending(true)
    try {
      const assistantMessage = await conversationApi.send(text)
      setMessages((current) => [...current, assistantMessage])
    } catch (err) {
      setSendError(
        err instanceof ApiError ? err.message : 'Não consegui falar com o TEYO agora.',
      )
    } finally {
      setSending(false)
    }
  }

  return (
    <section className="conversation-screen">
      <h1>Conversa com TEYO</h1>

      {history.status === 'loading' && <LoadingState label="Carregando conversa…" />}
      {history.status === 'error' && history.error && (
        <ErrorState message={history.error} onRetry={history.reload} />
      )}

      {history.status !== 'loading' && (
        <>
          <ul className="conversation-messages">
            {messages.map((message) => (
              <li key={message.id} className={`message message-${message.role}`}>
                <span>{message.content}</span>
              </li>
            ))}
            {sending && (
              <li className="message message-assistant" role="status">
                <span>TEYO está digitando…</span>
              </li>
            )}
          </ul>
          <div ref={bottomRef} />

          {sendError && <p role="alert">{sendError}</p>}

          <form onSubmit={handleSubmit} className="conversation-input">
            <input
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              placeholder="Fala com o TEYO…"
              disabled={sending}
            />
            <button type="submit" disabled={sending || !draft.trim()}>
              Enviar
            </button>
          </form>
        </>
      )}
    </section>
  )
}
