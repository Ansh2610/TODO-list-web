// TodoStorageManager: talks to the REST API (MongoDB) with a localStorage fallback; also reads/saves user preferences.

class TodoStorageManager {
    constructor() {
        this.apiBase = '/api';
        this.authToken = localStorage.getItem('authToken');
        this.init();
    }

    // Placeholder init (kept for symmetry with other managers)
    init() {
        return true;
    }

    // Headers for authenticated requests
    getAuthHeaders() {
        return {
            'Authorization': `Bearer ${this.authToken}`,
            'Content-Type': 'application/json'
        };
    }

    // Centralized API error handling (logout on 401)
    handleApiError(error, response) {
        console.error('API Error:', error);
        if (response && response.status === 401) {
            localStorage.removeItem('authToken');
            localStorage.removeItem('user');
            window.location.href = '/auth.html';
        }
    }

    // Load todos from API or fallback to localStorage
    async getTodos() {
        try {
            const response = await fetch(`${this.apiBase}/todos`, {
                headers: this.getAuthHeaders()
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();
            return data.todos || [];
        } catch (error) {
            console.warn('API not available, using local storage fallback');
            const todos = localStorage.getItem('todos');
            return todos ? JSON.parse(todos) : [];
        }
    }

    // Create todo via API or local fallback
    async addTodo(todo) {
        try {
            const response = await fetch(`${this.apiBase}/todos`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify(todo)
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();
            return data.todo;
        } catch (error) {
            console.warn('API not available, using local storage fallback');
            const newTodo = {
                ...todo,
                id: Date.now().toString(),
                _id: Date.now().toString(), // keep both for compatibility
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString(),
                completed: false
            };
            const todos = await this.getTodos();
            todos.push(newTodo);
            localStorage.setItem('todos', JSON.stringify(todos));
            return newTodo;
        }
    }

    // Update todo via API or local fallback
    async updateTodo(id, updates) {
        try {
            const response = await fetch(`${this.apiBase}/todos/${id}`, {
                method: 'PUT',
                headers: this.getAuthHeaders(),
                body: JSON.stringify(updates)
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();
            return data.todo;
        } catch (error) {
            console.warn('API not available, using local storage fallback');
            const todos = await this.getTodos();
            const todoIndex = todos.findIndex(t => t.id === id || t._id === id);
            if (todoIndex !== -1) {
                todos[todoIndex] = { ...todos[todoIndex], ...updates, updatedAt: new Date().toISOString() };
                localStorage.setItem('todos', JSON.stringify(todos));
                return todos[todoIndex];
            }
            return null;
        }
    }

    // Delete todo via API or local fallback
    async deleteTodo(id) {
        try {
            const response = await fetch(`${this.apiBase}/todos/${id}`, {
                method: 'DELETE',
                headers: this.getAuthHeaders()
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();
            return data.success;
        } catch (error) {
            console.warn('API not available, using local storage fallback');
            const todos = await this.getTodos();
            const filteredTodos = todos.filter(t => t.id !== id && t._id !== id);
            if (filteredTodos.length !== todos.length) {
                localStorage.setItem('todos', JSON.stringify(filteredTodos));
                return true;
            }
            return false;
        }
    }

    // Toggle completion via API or local fallback
    async toggleTodo(id) {
        try {
            const response = await fetch(`${this.apiBase}/todos/${id}/toggle`, {
                method: 'PATCH',
                headers: this.getAuthHeaders()
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();
            return data.todo;
        } catch (error) {
            console.warn('API not available, using local storage fallback');
            const todos = await this.getTodos();
            const todoIndex = todos.findIndex(t => t.id === id || t._id === id);
            if (todoIndex !== -1) {
                todos[todoIndex].completed = !todos[todoIndex].completed;
                todos[todoIndex].updatedAt = new Date().toISOString();
                localStorage.setItem('todos', JSON.stringify(todos));
                return todos[todoIndex];
            }
            return null;
        }
    }

    // Batch complete/uncomplete via API or local fallback
    async markAllTodos(completed) {
        try {
            const response = await fetch(`${this.apiBase}/todos/mark-all`, {
                method: 'PATCH',
                headers: this.getAuthHeaders(),
                body: JSON.stringify({ completed })
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();
            return data.todos || [];
        } catch (error) {
            console.warn('API not available, using local storage fallback');
            const todos = await this.getTodos();
            const updatedTodos = todos.map(todo => ({
                ...todo,
                completed,
                updatedAt: new Date().toISOString()
            }));
            localStorage.setItem('todos', JSON.stringify(updatedTodos));
            return updatedTodos;
        }
    }

    // Remove completed via API or local fallback
    async clearCompleted() {
        try {
            const response = await fetch(`${this.apiBase}/todos/completed`, {
                method: 'DELETE',
                headers: this.getAuthHeaders()
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();
            return data.todos || [];
        } catch (error) {
            console.warn('API not available, using local storage fallback');
            const todos = await this.getTodos();
            const remainingTodos = todos.filter(todo => !todo.completed);
            localStorage.setItem('todos', JSON.stringify(remainingTodos));
            return remainingTodos;
        }
    }

    // Read settings from user profile (or defaults)
    getSettings() {
        try {
            const user = JSON.parse(localStorage.getItem('user') || '{}');
            return user.preferences || { theme: 'light', sortBy: 'created', filter: 'all' };
        } catch (error) {
            console.error('Error loading settings:', error);
            return { theme: 'light', sortBy: 'created', filter: 'all' };
        }
    }

    // Save settings to user profile via API
    async saveSettings(settings) {
        try {
            const response = await fetch(`${this.apiBase}/auth/preferences`, {
                method: 'PUT',
                headers: this.getAuthHeaders(),
                body: JSON.stringify(settings)
            });
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    localStorage.setItem('user', JSON.stringify(data.user));
                    return true;
                }
            }
            return false;
        } catch (error) {
            console.error('Error saving settings:', error);
            return false;
        }
    }
}

// Export
window.TodoStorageManager = TodoStorageManager;
