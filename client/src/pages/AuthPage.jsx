import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

const API = import.meta.env.VITE_API_URL || '/api'

export default function AuthPage() {
  const navigate = useNavigate()
  const [isLogin, setIsLogin] = useState(true)
  const [login, setLogin] = useState('')
  const [email, setEmail] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState('')

  // Check if already logged in
  useEffect(() => {
    const token = localStorage.getItem('authToken')
    if (token) {
      navigate('/')
    }
  }, [])

  const toggle = () => { setIsLogin(!isLogin); setError('') }

  async function handleLogin(e) {
    e.preventDefault()
    setError('')
    try {
      const res = await fetch(`${API}/auth/login`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ login, password }) })
      const data = await res.json()
      if (!data.success) throw new Error(data.message || 'Login failed')
      localStorage.setItem('authToken', data.token)
      localStorage.setItem('user', JSON.stringify(data.user))
      navigate('/')
    } catch (e) { setError(e.message) }
  }

  async function handleRegister(e) {
    e.preventDefault()
    setError('')
    if (password !== confirm) return setError('Passwords do not match')
    try {
      const res = await fetch(`${API}/auth/register`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username, email, password }) })
      const data = await res.json()
      if (!data.success) throw new Error(data.message || 'Registration failed')
      localStorage.setItem('authToken', data.token)
      localStorage.setItem('user', JSON.stringify(data.user))
      navigate('/')
    } catch (e) { setError(e.message) }
  }

  return (
    <div className="app-container">
      <div className="main-content">
        <div className="auth-box">
          <div style={{ textAlign: 'center', marginBottom: 24 }}>
            <h1 style={{ fontSize: '2rem', color: 'var(--text-primary)', marginBottom: 8 }}>🎮 Pixel TODO</h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Retro task management</p>
          </div>
          
          <h2 style={{ marginBottom: 16, textAlign: 'center' }}>{isLogin ? 'Login' : 'Register'}</h2>
          {error && <div className="error-message">{error}</div>}
          
          {isLogin ? (
            <form onSubmit={handleLogin}>
              <input className="form-input" placeholder="Username or Email" value={login} onChange={e=>setLogin(e.target.value)} required />
              <input className="form-input" placeholder="Password" type="password" value={password} onChange={e=>setPassword(e.target.value)} required />
              <button className="btn btn-primary" type="submit" style={{ width: '100%', marginBottom: 16 }}>Login</button>
            </form>
          ) : (
            <form onSubmit={handleRegister}>
              <input className="form-input" placeholder="Username" value={username} onChange={e=>setUsername(e.target.value)} required />
              <input className="form-input" placeholder="Email" type="email" value={email} onChange={e=>setEmail(e.target.value)} required />
              <input className="form-input" placeholder="Password" type="password" value={password} onChange={e=>setPassword(e.target.value)} required />
              <input className="form-input" placeholder="Confirm Password" type="password" value={confirm} onChange={e=>setConfirm(e.target.value)} required />
              <button className="btn btn-primary" type="submit" style={{ width: '100%', marginBottom: 16 }}>Register</button>
            </form>
          )}
          
          <div style={{ textAlign: 'center' }}>
            <button className="btn btn-ghost" onClick={toggle}>
              {isLogin ? 'Need an account? Register' : 'Have an account? Login'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
