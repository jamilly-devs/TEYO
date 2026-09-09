import { TasksScreen } from '../tasks/TasksScreen'

// Casa não tem backend próprio (decisão FASE 10): é a tela de Tarefas
// filtrada pela categoria "house". Sem módulo de pets.
export function HouseScreen() {
  return <TasksScreen categoryFilter="house" title="Casa" />
}
