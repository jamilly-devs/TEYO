import { fireEvent, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { ApiError } from '../../api/client'
import { tasksApi } from '../../api/tasks'
import { taskFixture } from '../../test-fixtures'
import { renderWithRouter } from '../../test-utils'
import { TasksScreen } from './TasksScreen'

vi.mock('../../api/tasks', () => ({
  tasksApi: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    remove: vi.fn(),
    complete: vi.fn(),
  },
}))

describe('TasksScreen', () => {
  it('shows the loading state while fetching', () => {
    vi.mocked(tasksApi.list).mockReturnValue(new Promise(() => {}))
    renderWithRouter(<TasksScreen />)
    expect(screen.getByRole('status')).toHaveTextContent(/carregando/i)
  })

  it('shows the empty state when there are no tasks', async () => {
    vi.mocked(tasksApi.list).mockResolvedValue([])
    renderWithRouter(<TasksScreen />)
    expect(await screen.findByText(/nenhuma tarefa ainda/i)).toBeInTheDocument()
  })

  it('shows the error state when the request fails', async () => {
    vi.mocked(tasksApi.list).mockRejectedValue(new ApiError(500, 'falha no servidor'))
    renderWithRouter(<TasksScreen />)
    expect(await screen.findByRole('alert')).toHaveTextContent('falha no servidor')
  })

  it('lists a task and shows the pomodoro indicator without a timer', async () => {
    vi.mocked(tasksApi.list).mockResolvedValue([{ ...taskFixture, pomodoro_enabled: true }])
    renderWithRouter(<TasksScreen />)
    expect(await screen.findByText('lavar louça')).toBeInTheDocument()
    expect(screen.getByText('🍅 pomodoro')).toBeInTheDocument()
    expect(screen.queryByRole('timer')).not.toBeInTheDocument()
  })

  it('requires confirmation before deleting a task', async () => {
    vi.mocked(tasksApi.list).mockResolvedValue([taskFixture])
    vi.mocked(tasksApi.remove).mockResolvedValue(undefined)
    renderWithRouter(<TasksScreen />)

    fireEvent.click(await screen.findByRole('button', { name: /excluir/i }))
    expect(screen.getByRole('dialog')).toBeInTheDocument()
    expect(tasksApi.remove).not.toHaveBeenCalled()

    fireEvent.click(screen.getByRole('button', { name: /confirmar/i }))
    await waitFor(() => expect(tasksApi.remove).toHaveBeenCalledWith(1))
  })

  it('shows a success confirmation after completing a task', async () => {
    vi.mocked(tasksApi.list).mockResolvedValue([taskFixture])
    vi.mocked(tasksApi.complete).mockResolvedValue({ ...taskFixture, status: 'done' })
    renderWithRouter(<TasksScreen />)

    fireEvent.click(await screen.findByRole('button', { name: /concluir/i }))
    expect(await screen.findByText(/tarefa concluída/i)).toBeInTheDocument()
  })

  it('creates a task using only the documented fields', async () => {
    vi.mocked(tasksApi.list).mockResolvedValue([])
    vi.mocked(tasksApi.create).mockResolvedValue(taskFixture)
    renderWithRouter(<TasksScreen />)

    fireEvent.change(await screen.findByLabelText(/título/i), {
      target: { value: 'estudar inglês' },
    })
    fireEvent.click(screen.getByRole('button', { name: /criar tarefa/i }))

    await waitFor(() =>
      expect(tasksApi.create).toHaveBeenCalledWith(
        expect.objectContaining({ title: 'estudar inglês', priority: 'medium' }),
      ),
    )
  })
})
