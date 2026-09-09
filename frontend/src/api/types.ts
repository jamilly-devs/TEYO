export interface User {
  id: number
  email: string
  name: string | null
  timezone: string
}

export type TaskStatus = 'pending' | 'in_progress' | 'done' | 'cancelled'
export type TaskPriority = 'low' | 'medium' | 'high'
export type TaskCategory = 'general' | 'studies' | 'house'

export interface Task {
  id: number
  title: string
  description: string | null
  status: TaskStatus
  due_date: string | null
  priority: TaskPriority
  category: TaskCategory | null
  is_recurring: boolean
  pomodoro_enabled: boolean
  goal_id: number | null
  created_at: string
  updated_at: string
}

export type EventSource = 'manual' | 'teyo_nlu'

export interface Event {
  id: number
  title: string
  start_at: string
  end_at: string
  source: EventSource
  created_at: string
  updated_at: string
}

export type GoalStatus = 'active' | 'completed' | 'abandoned'

export interface Goal {
  id: number
  title: string
  description: string | null
  status: GoalStatus
  target_date: string | null
  created_at: string
  updated_at: string
}

export type MarketItemStatus = 'active' | 'purchased'

export interface MarketItem {
  id: number
  name: string
  category: string | null
  is_recurring_suggestion: boolean
  status: MarketItemStatus
  created_at: string
}

export type FinancialRecordType = 'income' | 'expense'

export interface FinancialRecord {
  id: number
  type: FinancialRecordType
  amount: string
  category: string | null
  date: string
  description: string | null
  created_at: string
}

export type MessageRole = 'user' | 'assistant' | 'tool'

export interface ConversationMessage {
  id: number
  role: MessageRole
  content: string
  created_at: string
}

export type DayPeriod = 'madrugada' | 'manhã' | 'tarde' | 'noite'

export interface DailyPlanItem {
  kind: 'task' | 'event'
  id: number
  title: string
  period: DayPeriod | null
  start_at: string | null
  priority: TaskPriority | null
  reason: string | null
  suggested_due_date: string | null
}

export interface DailyPlan {
  date: string
  items: DailyPlanItem[]
}

export interface Achievement {
  code: string
  title: string
  description: string
  unlocked_at: string
}

export interface GamificationState {
  xp_total: number
  level: number
  xp_into_level: number
  xp_for_next_level: number
  streak_days: number
  achievements: Achievement[]
}

export type MascotExpression =
  | 'idle'
  | 'happy'
  | 'proud'
  | 'celebrating'
  | 'caring'
  | 'tired'

export interface MascotState {
  evolution_stage: number
  current_expression: MascotExpression
  color: string
  unlocked_features: string[]
  updated_at: string | null
}
