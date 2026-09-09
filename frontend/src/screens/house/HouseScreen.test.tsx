import { screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { tasksApi } from '../../api/tasks'
import { taskFixture } from '../../test-fixtures'
import { renderWithRouter } from '../../test-utils'
import { HouseScreen } from './HouseScreen'

vi.mock('../../api/tasks', () => ({
  tasksApi: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    remove: vi.fn(),
    complete: vi.fn(),
  },
}))

describe('HouseScreen', () => {
  it('is the Tasks screen filtered to the house category', async () => {
    vi.mocked(tasksApi.list).mockResolvedValue([
      { ...taskFixture, id: 1, title: 'lavar louça', category: 'house' },
      { ...taskFixture, id: 2, title: 'ler capítulo', category: 'studies' },
    ])
    renderWithRouter(<HouseScreen />)

    expect(await screen.findByRole('heading', { name: 'Casa' })).toBeInTheDocument()
    expect(screen.getByText('lavar louça')).toBeInTheDocument()
    expect(screen.queryByText('ler capítulo')).not.toBeInTheDocument()
  })
})
