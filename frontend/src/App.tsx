import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { AppLayout } from './components/AppLayout'
import { ProtectedRoute } from './components/ProtectedRoute'
import { AgendaScreen } from './screens/agenda/AgendaScreen'
import { FinanceScreen } from './screens/finance/FinanceScreen'
import { GoalsScreen } from './screens/goals/GoalsScreen'
import { HomeScreen } from './screens/home/HomeScreen'
import { LoginScreen } from './screens/login/LoginScreen'
import { RegisterScreen } from './screens/login/RegisterScreen'
import { MarketScreen } from './screens/market/MarketScreen'
import { TasksScreen } from './screens/tasks/TasksScreen'
import { ConversationScreen } from './screens/teyo-chat/ConversationScreen'
import { AuthProvider } from './state/AuthContext'

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginScreen />} />
          <Route path="/register" element={<RegisterScreen />} />
          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route path="/" element={<HomeScreen />} />
              <Route path="/conversa" element={<ConversationScreen />} />
              <Route path="/tasks" element={<TasksScreen />} />
              <Route path="/agenda" element={<AgendaScreen />} />
              <Route path="/goals" element={<GoalsScreen />} />
              <Route path="/market" element={<MarketScreen />} />
              <Route path="/finance" element={<FinanceScreen />} />
            </Route>
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
