import { useState } from 'react'
import type { FormEvent } from 'react'
import { ApiError } from '../../api/client'
import { tasksApi } from '../../api/tasks'
import type { Task, TaskCategory, TaskPriority } from '../../api/types'
import { ConfirmDialog } from '../../components/ConfirmDialog'
import { PomodoroTimer } from '../../components/PomodoroTimer'
import { EmptyState, ErrorState, LoadingState } from '../../components/ScreenStates'
import { useApiResource } from '../../state/useApiResource'

function TaskCreateForm({
  onCreated,
  defaultCategory,
}: {
  onCreated: (task: Task) => void
  defaultCategory?: TaskCategory
}) {
  const [title, setTitle] = useState('')
  const [dueDate, setDueDate] = useState('')
  const [priority, setPriority] = useState<TaskPriority>('medium')
  const [category, setCategory] = useState<TaskCategory | ''>(defaultCategory ?? '')
  const [pomodoroEnabled, setPomodoroEnabled] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      const task = await tasksApi.create({
        title,
        due_date: dueDate || undefined,
        priority,
        category: category || undefined,
        pomodoro_enabled: pomodoroEnabled,
      })
      onCreated(task)
      setTitle('')
      setDueDate('')
      setPriority('medium')
      setCategory(defaultCategory ?? '')
      setPomodoroEnabled(false)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Não foi possível criar a tarefa.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="create-form">
      <label>
        Título
        <input value={title} onChange={(e) => setTitle(e.target.value)} required />
      </label>
      <label>
        Data/hora
        <input
          type="datetime-local"
          value={dueDate}
          onChange={(e) => setDueDate(e.target.value)}
        />
      </label>
      <label>
        Prioridade
        <select value={priority} onChange={(e) => setPriority(e.target.value as TaskPriority)}>
          <option value="low">Baixa</option>
          <option value="medium">Média</option>
          <option value="high">Alta</option>
        </select>
      </label>
      <label>
        Categoria
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value as TaskCategory | '')}
        >
          <option value="">Nenhuma</option>
          <option value="general">Geral</option>
          <option value="studies">Estudos</option>
          <option value="house">Casa</option>
        </select>
      </label>
      <label>
        <input
          type="checkbox"
          checked={pomodoroEnabled}
          onChange={(e) => setPomodoroEnabled(e.target.checked)}
        />
        Pomodoro
      </label>
      {error && <p role="alert">{error}</p>}
      <button type="submit" disabled={submitting}>
        {submitting ? 'Criando…' : 'Criar tarefa'}
      </button>
    </form>
  )
}

function TaskRow({
  task,
  onChanged,
  onDeleted,
}: {
  task: Task
  onChanged: (task: Task) => void
  onDeleted: (id: number) => void
}) {
  const [confirmingDelete, setConfirmingDelete] = useState(false)
  const [feedback, setFeedback] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [showPomodoro, setShowPomodoro] = useState(false)

  async function handleComplete() {
    setBusy(true)
    try {
      const updated = await tasksApi.complete(task.id)
      onChanged(updated)
      setFeedback('Tarefa concluída.')
    } finally {
      setBusy(false)
    }
  }

  async function handleDelete() {
    setBusy(true)
    try {
      await tasksApi.remove(task.id)
      onDeleted(task.id)
    } finally {
      setBusy(false)
      setConfirmingDelete(false)
    }
  }

  return (
    <li className="task-row">
      <span className="task-title">{task.title}</span>
      <span className={`badge status-${task.status}`}>{task.status}</span>
      <span className={`badge priority-${task.priority}`}>{task.priority}</span>
      {task.category && <span className="badge category">{task.category}</span>}
      {task.pomodoro_enabled && <span className="badge pomodoro">🍅 pomodoro</span>}
      {task.due_date && <span className="task-due">{task.due_date}</span>}
      {feedback && <span role="status">{feedback}</span>}
      <div className="task-actions">
        {task.status !== 'done' && (
          <button type="button" onClick={handleComplete} disabled={busy}>
            Concluir
          </button>
        )}
        {task.pomodoro_enabled && (
          <button type="button" onClick={() => setShowPomodoro((v) => !v)}>
            {showPomodoro ? 'Fechar Pomodoro' : 'Pomodoro'}
          </button>
        )}
        <button type="button" onClick={() => setConfirmingDelete(true)} disabled={busy}>
          Excluir
        </button>
      </div>
      {showPomodoro && (
        <PomodoroTimer taskId={task.id} onClose={() => setShowPomodoro(false)} />
      )}
      {confirmingDelete && (
        <ConfirmDialog
          message={`Excluir a tarefa "${task.title}"?`}
          onConfirm={handleDelete}
          onCancel={() => setConfirmingDelete(false)}
        />
      )}
    </li>
  )
}

export function TasksScreen({
  categoryFilter,
  title = 'Tarefas',
}: {
  // Estudos e Casa são visões filtradas desta tela por categoria — sem
  // backend próprio (decisão FASE 10). Sem `categoryFilter` a tela é a de
  // Tarefas completa, comportamento inalterado.
  categoryFilter?: TaskCategory
  title?: string
} = {}) {
  const { status, data, error, reload, setData } = useApiResource(tasksApi.list)

  function handleCreated(task: Task) {
    setData([task, ...(data ?? [])])
  }

  function handleChanged(task: Task) {
    setData((data ?? []).map((t) => (t.id === task.id ? task : t)))
  }

  function handleDeleted(id: number) {
    setData((data ?? []).filter((t) => t.id !== id))
  }

  const visible = categoryFilter
    ? (data ?? []).filter((t) => t.category === categoryFilter)
    : (data ?? [])
  const emptyMessage = categoryFilter
    ? `Nada em ${title} ainda. Crie a primeira tarefa acima ou fale com o TEYO.`
    : 'Nenhuma tarefa ainda. Crie a primeira acima.'

  return (
    <section>
      <h1>{title}</h1>
      <TaskCreateForm onCreated={handleCreated} defaultCategory={categoryFilter} />

      {status === 'loading' && <LoadingState />}
      {status === 'error' && error && <ErrorState message={error} onRetry={reload} />}
      {status === 'success' && visible.length === 0 && <EmptyState message={emptyMessage} />}
      {status === 'success' && visible.length > 0 && (
        <ul className="task-list">
          {visible.map((task) => (
            <TaskRow
              key={task.id}
              task={task}
              onChanged={handleChanged}
              onDeleted={handleDeleted}
            />
          ))}
        </ul>
      )}
    </section>
  )
}
