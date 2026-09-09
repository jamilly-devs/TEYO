import { screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { tasksApi } from '../../api/tasks'
import { taskFixture } from '../../test-fixtures'
import { renderWithRouter } from '../../test-utils'
import { StudiesScreen } from './StudiesScreen'

vi.mock('../../api/tasks', () => ({
  tasksApi: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    remove: vi.fn(),
    complete: vi.fn(),
  },
}))

describe('StudiesScreen', () => {
  it('is the Tasks screen filtered to the studies category', async () => {
    vi.mocked(tasksApi.list).mockResolvedValue([
      { ...taskFixture, id: 1, title: 'ler capítulo', category: 'studies' },
      { ...taskFixture, id: 2, title: 'lavar louça', category: 'house' },
    ])
    renderWithRouter(<StudiesScreen />)

    expect(await screen.findByRole('heading', { name: 'Estudos' })).toBeInTheDocument()
    expect(screen.getByText('ler capítulo')).toBeInTheDocument()
    expect(screen.queryByText('lavar louça')).not.toBeInTheDocument()
  })
})
