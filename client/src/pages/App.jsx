import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import AuthPage from './AuthPage.jsx'
import TodosPage from './TodosPage.jsx'

export default function App() {
  return (
    <Routes>
      <Route path="/auth" element={<AuthPage />} />
      <Route path="/" element={<TodosPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
