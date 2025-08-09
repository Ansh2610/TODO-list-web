import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import React from 'react'
import TodosPage from '../TodosPage.jsx'

const mockTodos = [
  { _id: '1', text: 'Task A', completed: false },
  { _id: '2', text: 'Task B', completed: true },
]

describe('TodosPage', () => {
  beforeEach(() => {
    localStorage.clear()
    localStorage.setItem('authToken', 'token')
    vi.spyOn(window, 'fetch').mockImplementation((url, opts={}) => {
      if (url.toString().includes('/api/todos') && (!opts.method || opts.method === 'GET')) {
        return Promise.resolve({ json: () => Promise.resolve({ success: true, todos: mockTodos }) })
      }
      if (url.toString().includes('/api/todos') && opts.method === 'POST') {
        return Promise.resolve({ json: () => Promise.resolve({ success: true, todo: { _id: '3', text: 'New Task', completed: false } }) })
      }
      if (url.toString().includes('/toggle') && opts.method === 'PATCH') {
        return Promise.resolve({ json: () => Promise.resolve({ success: true, todo: { ...mockTodos[0], completed: true } }) })
      }
      if (opts.method === 'DELETE') {
        return Promise.resolve({ json: () => Promise.resolve({ success: true }) })
      }
      return Promise.resolve({ json: () => Promise.resolve({ success: false }) })
    })
  })

  it('renders counts and list', async () => {
    render(<TodosPage />)
    expect(await screen.findByText(/All:/)).toBeInTheDocument()
    expect(screen.getByText('Task A')).toBeInTheDocument()
    expect(screen.getByText('Task B')).toBeInTheDocument()
  })

  it('adds a todo', async () => {
    render(<TodosPage />)
    fireEvent.change(screen.getByPlaceholderText('Add a task'), { target: { value: 'New Task' } })
    fireEvent.click(screen.getByText('Add'))
    await waitFor(() => expect(screen.getByText('New Task')).toBeInTheDocument())
  })
})
