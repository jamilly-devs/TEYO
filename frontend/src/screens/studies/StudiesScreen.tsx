import { TasksScreen } from '../tasks/TasksScreen'

// Estudos não tem backend próprio (decisão FASE 10): é a tela de Tarefas
// filtrada pela categoria "studies".
export function StudiesScreen() {
  return <TasksScreen categoryFilter="studies" title="Estudos" />
}
