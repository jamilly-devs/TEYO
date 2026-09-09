import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { pomodoroApi } from '../api/pomodoro'
import type { PomodoroSession } from '../api/types'
import { PomodoroTimer } from './PomodoroTimer'

vi.mock('../api/pomodoro', () => ({
  pomodoroApi: {
    active: vi.fn(),
    start: vi.fn(),
    pause: vi.fn(),
    resume: vi.fn(),
    complete: vi.fn(),
  },
}))

const activeSession: PomodoroSession = {
  id: 1,
  task_id: 7,
  status: 'active',
  started_at: new Date().toISOString(),
  ended_at: null,
}

describe('PomodoroTimer', () => {
  it('starts a session for the task and shows the countdown', async () => {
    vi.mocked(pomodoroApi.active).mockResolvedValue(null)
    vi.mocked(pomodoroApi.start).mockResolvedValue(activeSession)
    render(<PomodoroTimer taskId={7} onClose={() => {}} />)

    fireEvent.click(await screen.findByRole('button', { name: /iniciar pomodoro/i }))

    await waitFor(() => expect(pomodoroApi.start).toHaveBeenCalledWith(7))
    expect(await screen.findByRole('timer')).toBeInTheDocument()
  })

  it('adopts an already running session and can pause / resume / complete it', async () => {
    vi.mocked(pomodoroApi.active).mockResolvedValue(activeSession)
    vi.mocked(pomodoroApi.pause).mockResolvedValue({ ...activeSession, status: 'paused' })
    vi.mocked(pomodoroApi.resume).mockResolvedValue(activeSession)
    vi.mocked(pomodoroApi.complete).mockResolvedValue({
      ...activeSession,
      status: 'completed',
      ended_at: new Date().toISOString(),
    })
    const onClose = vi.fn()
    render(<PomodoroTimer taskId={7} onClose={onClose} />)

    expect(await screen.findByRole('timer')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /^pausar$/i }))
    await waitFor(() => expect(pomodoroApi.pause).toHaveBeenCalledWith(1))

    fireEvent.click(await screen.findByRole('button', { name: /retomar/i }))
    await waitFor(() => expect(pomodoroApi.resume).toHaveBeenCalledWith(1))

    fireEvent.click(screen.getByRole('button', { name: /concluir/i }))
    await waitFor(() => expect(pomodoroApi.complete).toHaveBeenCalledWith(1))
    await waitFor(() => expect(onClose).toHaveBeenCalled())
  })
})
