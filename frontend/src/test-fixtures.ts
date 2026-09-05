import type { Event, FinancialRecord, Goal, MarketItem, Task, User } from './api/types'

export const userFixture: User = {
  id: 1,
  email: 'user@example.com',
  name: null,
  timezone: 'America/Sao_Paulo',
}

export const taskFixture: Task = {
  id: 1,
  title: 'lavar louça',
  description: null,
  status: 'pending',
  due_date: null,
  priority: 'medium',
  category: null,
  is_recurring: false,
  pomodoro_enabled: false,
  goal_id: null,
  created_at: '2026-01-01T00:00:00',
  updated_at: '2026-01-01T00:00:00',
}

export const eventFixture: Event = {
  id: 1,
  title: 'reunião',
  start_at: '2026-01-01T14:00:00',
  end_at: '2026-01-01T15:00:00',
  source: 'manual',
  created_at: '2026-01-01T00:00:00',
  updated_at: '2026-01-01T00:00:00',
}

export const goalFixture: Goal = {
  id: 1,
  title: 'aprender inglês',
  description: null,
  status: 'active',
  target_date: null,
  created_at: '2026-01-01T00:00:00',
  updated_at: '2026-01-01T00:00:00',
}

export const marketItemFixture: MarketItem = {
  id: 1,
  name: 'arroz',
  category: null,
  is_recurring_suggestion: false,
  status: 'active',
  created_at: '2026-01-01T00:00:00',
}

export const financialRecordFixture: FinancialRecord = {
  id: 1,
  type: 'expense',
  amount: '10.00',
  category: null,
  date: '2026-01-01',
  description: null,
  created_at: '2026-01-01T00:00:00',
}
