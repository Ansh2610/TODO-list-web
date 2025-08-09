import React, { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'

const API = import.meta.env.VITE_API_URL || '/api'

export default function TodosPage() {
  const navigate = useNavigate()
  const [todos, setTodos] = useState([])
  const [text, setText] = useState('')
  const [description, setDescription] = useState('')
  const [priority, setPriority] = useState('medium')
  const [dueDate, setDueDate] = useState('')
  const [dueTime, setDueTime] = useState('')
  const [category, setCategory] = useState('')
  const [emailReminders, setEmailReminders] = useState(false)
  const [loading, setLoading] = useState(false)
  const [showModal, setShowModal] = useState(false)
  const [filter, setFilter] = useState('all')
  const [sortBy, setSortBy] = useState('dueDate')
  const [user, setUser] = useState(null)
  const token = localStorage.getItem('authToken')

  useEffect(() => {
    if (!token) {
      navigate('/auth')
      return
    }
    
    // Get user info
    const userData = localStorage.getItem('user')
    if (userData) {
      setUser(JSON.parse(userData))
    }
    
    fetchTodos()
  }, [token])

  async function fetchTodos() {
    setLoading(true)
    try {
      const params = new URLSearchParams({ filter, sortBy })
      const res = await fetch(`${API}/todos?${params}`, { headers: { Authorization: `Bearer ${token}` } })
      const data = await res.json()
      if (!data.success) throw new Error(data.message || 'Failed to fetch')
      setTodos(data.todos)
    } catch (e) { 
      console.error(e)
      if (e.message.includes('401') || e.message.includes('token')) {
        logout()
      }
    }
    finally { setLoading(false) }
  }

  useEffect(() => {
    if (token) fetchTodos()
  }, [filter, sortBy])

  async function addTodo(e) {
    e.preventDefault()
    if (!text.trim()) return
    
    let finalDueDate = null
    if (dueDate) {
      finalDueDate = dueTime ? `${dueDate}T${dueTime}` : `${dueDate}T23:59`
    }
    
    const todoData = { 
      text: text.trim(), 
      description: description.trim(),
      priority,
      category: category || undefined,
      ...(finalDueDate && { dueDate: new Date(finalDueDate).toISOString() })
    }
    
    const res = await fetch(`${API}/todos`, { 
      method: 'POST', 
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` }, 
      body: JSON.stringify(todoData) 
    })
    const data = await res.json()
    if (data.success) { 
      setTodos([data.todo, ...todos])
      // Reset form
      setText('')
      setDescription('')
      setPriority('medium')
      setDueDate('')
      setDueTime('')
      setCategory('')
      setEmailReminders(false)
      setShowModal(false)
    }
  }

  async function toggleTodo(id) {
    const res = await fetch(`${API}/todos/${id}/toggle`, { method: 'PATCH', headers: { Authorization: `Bearer ${token}` } })
    const data = await res.json()
    if (data.success) setTodos(todos.map(t => t._id === id ? data.todo : t))
  }

  async function deleteTodo(id) {
    const res = await fetch(`${API}/todos/${id}`, { method: 'DELETE', headers: { Authorization: `Bearer ${token}` } })
    const data = await res.json()
    if (data.success) setTodos(todos.filter(t => t._id !== id))
  }

  function logout() {
    localStorage.removeItem('authToken')
    localStorage.removeItem('user')
    navigate('/auth')
  }

  const filteredTodos = useMemo(() => {
    return todos.filter(t => {
      if (filter === 'active') return !t.completed
      if (filter === 'completed') return t.completed
      return true
    })
  }, [todos, filter])

  const counts = useMemo(() => ({
    all: todos.length,
    completed: todos.filter(t => t.completed).length,
    active: todos.filter(t => !t.completed).length,
  }), [todos])

  return (
    <div className="app-container">
        <div className="app-header">
          <div className="header-content">
            <div className="app-title">
              <i className="fas fa-tasks"></i>
              My TODO List
            </div>
            <div className="header-actions">
              <button className="btn btn-theme" onClick={logout}>
                <i className="fas fa-sign-out-alt"></i> Logout
              </button>
              <button className="btn btn-theme" onClick={() => setShowModal(true)}>
                <i className="fas fa-moon"></i>
              </button>
            </div>
          </div>
        </div>

      <div className="main-content">
        {/* Add Todo Section */}
        <div className="add-todo-section">
          <button 
            className="personalized-add-btn" 
            onClick={() => setShowModal(true)}
          >
            <i className="fas fa-plus"></i>
            <span>HEY ANSH! ADD A NEW TASK</span>
          </button>
        </div>

        {/* Filter Section */}
        <div className="filter-section">
          <div className="filter-container">
            <div className="filter-buttons">
              <button className={`filter-btn ${filter === 'all' ? 'active' : ''}`} onClick={() => setFilter('all')}>
                All ({counts.all})
              </button>
              <button className={`filter-btn ${filter === 'active' ? 'active' : ''}`} onClick={() => setFilter('active')}>
                Active ({counts.active})
              </button>
              <button className={`filter-btn ${filter === 'completed' ? 'active' : ''}`} onClick={() => setFilter('completed')}>
                Completed ({counts.completed})
              </button>
            </div>
            
            <select className="sort-select" value={sortBy} onChange={e => setSortBy(e.target.value)}>
              <option value="created">Sort by Created</option>
              <option value="priority">Sort by Priority</option>
              <option value="dueDate">Sort by Due Date</option>
              <option value="alphabetical">Sort Alphabetically</option>
            </select>
          </div>
        </div>

        {/* Todo List */}
        <div className="todo-list-section">
          <div className="todo-list-container">
            {loading ? (
              <div className="empty-state">
                <div className="empty-icon">⏳</div>
                <h3>Loading...</h3>
              </div>
            ) : filteredTodos.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">📝</div>
                <h3>No tasks found</h3>
                <p>Add a new task to get started!</p>
              </div>
            ) : (
              <ul className="todo-list">
                {filteredTodos.map(todo => (
                  <TodoItem 
                    key={todo._id} 
                    todo={todo} 
                    onToggle={toggleTodo} 
                    onDelete={deleteTodo} 
                  />
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>

      {/* Add Todo Modal */}
      {showModal && (
        <div className="modal-overlay active" onClick={() => setShowModal(false)}>
          <div className="modal active">
            <div className="modal-content enhanced-modal" onClick={e => e.stopPropagation()}>
              <div className="modal-header">
                <h3>
                  <i className="fas fa-tasks"></i>
                  Create New Task
                </h3>
                <button className="btn action-btn modal-close" onClick={() => setShowModal(false)}>
                  <i className="fas fa-times"></i>
                </button>
              </div>
              
              <div className="modal-body">
                <form onSubmit={addTodo}>
                  <div className="form-section">
                    <label>
                      <i className="fas fa-edit"></i>
                      TASK TITLE
                    </label>
                    <input 
                      className="form-input" 
                      placeholder="What needs to be done?" 
                      value={text} 
                      onChange={e => setText(e.target.value)}
                      autoFocus
                      required
                    />
                  </div>
                  
                  <div className="form-section">
                    <label>
                      <i className="fas fa-align-left"></i>
                      DESCRIPTION (OPTIONAL)
                    </label>
                    <textarea 
                      className="form-textarea" 
                      placeholder="Add more details about this task..."
                      value={description} 
                      onChange={e => setDescription(e.target.value)}
                      rows={3}
                    />
                  </div>
                  
                  <div className="form-row">
                    <div className="form-section">
                      <label>
                        <i className="fas fa-flag"></i>
                        PRIORITY
                      </label>
                      <select className="form-select" value={priority} onChange={e => setPriority(e.target.value)}>
                        <option value="low">🟢 Low Priority</option>
                        <option value="medium">🟡 Medium Priority</option>
                        <option value="high">🔴 High Priority</option>
                      </select>
                    </div>
                    
                    <div className="form-section">
                      <label>
                        <i className="fas fa-calendar"></i>
                        DUE DATE
                      </label>
                      <input 
                        className="form-input" 
                        type="date" 
                        value={dueDate} 
                        onChange={e => setDueDate(e.target.value)}
                      />
                    </div>
                  </div>
                  
                  <div className="form-row">
                    <div className="form-section">
                      <label>
                        <i className="fas fa-clock"></i>
                        DUE TIME (OPTIONAL)
                      </label>
                      <input 
                        className="form-input" 
                        type="time" 
                        value={dueTime} 
                        onChange={e => setDueTime(e.target.value)}
                      />
                    </div>
                    
                    <div className="form-section">
                      <label>
                        <i className="fas fa-tag"></i>
                        CATEGORY (OPTIONAL)
                      </label>
                      <select className="form-select" value={category} onChange={e => setCategory(e.target.value)}>
                        <option value="">No Category</option>
                        <option value="work">Work</option>
                        <option value="personal">Personal</option>
                        <option value="study">Study</option>
                        <option value="health">Health</option>
                        <option value="finance">Finance</option>
                        <option value="shopping">Shopping</option>
                      </select>
                    </div>
                  </div>
                  
                  <div className="email-notifications">
                    <div className="checkbox-wrapper">
                      <input 
                        type="checkbox" 
                        className="form-checkbox" 
                        id="emailReminders"
                        checked={emailReminders}
                        onChange={e => setEmailReminders(e.target.checked)}
                      />
                      <label htmlFor="emailReminders" style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <i className="fas fa-envelope"></i>
                        ENABLE EMAIL REMINDERS
                      </label>
                    </div>
                  </div>
                  
                  <div className="modal-footer">
                    <button type="button" className="btn btn-ghost" onClick={() => setShowModal(false)}>
                      Cancel
                    </button>
                    <button type="submit" className="btn btn-primary">
                      <i className="fas fa-plus"></i>
                      Create Task
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// Todo Item Component
function TodoItem({ todo, onToggle, onDelete }) {
  const isOverdue = todo.dueDate && new Date(todo.dueDate) < new Date() && !todo.completed
  
  return (
    <li className={`todo-item ${todo.completed ? 'completed' : ''}`}>
      <input 
        type="checkbox" 
        className="todo-checkbox" 
        checked={todo.completed} 
        onChange={() => onToggle(todo._id)} 
      />
      <div className="todo-content">
        <span className="todo-text">{todo.text}</span>
        {todo.description && (
          <div className="todo-description">{todo.description}</div>
        )}
        <div className="todo-meta">
          <span className={`priority-badge priority-${todo.priority}`}>
            {todo.priority.toUpperCase()}
          </span>
          {todo.category && (
            <span className="category-badge">
              <i className="fas fa-tag"></i>
              {todo.category}
            </span>
          )}
          {todo.dueDate && (
            <span className={`due-date ${isOverdue ? 'overdue' : ''}`}>
              <i className="fas fa-calendar"></i>
              {new Date(todo.dueDate).toLocaleDateString()}
            </span>
          )}
          <span className="created-date">
            <i className="fas fa-clock"></i>
            Today
          </span>
        </div>
      </div>
      <div className="todo-actions">
        <button className="action-btn edit" title="Edit">
          <i className="fas fa-edit"/>
        </button>
        <button className="action-btn delete" onClick={() => onDelete(todo._id)} title="Delete">
          <i className="fas fa-trash"/>
        </button>
      </div>
    </li>
  )
}
