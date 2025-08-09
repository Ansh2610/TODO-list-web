/**
 * API Storage Manager for TODO List Application
 * Handles all data operations through REST API with MongoDB backend
 */

class TodoStorageManager {
    constructor() {
        this.apiBase = '/api';
        this.authToken = localStorage.getItem('authToken');
        this.init();
    }

    init() {
        // Storage manager is now initialized after auth check in app.js
        return true;
    }

    /**
     * Get authentication headers
     */
    getAuthHeaders() {
        return {
            'Authorization': `Bearer ${this.authToken}`,
            'Content-Type': 'application/json'
        };
    }

    /**
     * Handle API errors
     */
    handleApiError(error, response) {
        console.error('API Error:', error);
        if (response && response.status === 401) {
            // Unauthorized - redirect to login
            localStorage.removeItem('authToken');
            localStorage.removeItem('user');
            window.location.href = '/auth.html';
        }
    }

    /**
     * Get all todos for the authenticated user
     * @returns {Array} Array of todo objects
     */
    async getTodos() {
        try {
            const response = await fetch(`${this.apiBase}/todos`, {
                headers: this.getAuthHeaders()
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data.todos || [];
        } catch (error) {
            console.warn('API not available, using local storage fallback');
            // Fallback to local storage for testing
            const todos = localStorage.getItem('todos');
            return todos ? JSON.parse(todos) : [];
        }
    }

    /**
     * Add a new todo
     * @param {Object} todo - Todo object to add
     * @returns {Object} The added todo with generated ID
     */
    async addTodo(todo) {
        try {
            const response = await fetch(`${this.apiBase}/todos`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify(todo)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data.todo;
        } catch (error) {
            console.warn('API not available, using local storage fallback');
            // Fallback to local storage for testing
            const newTodo = {
                ...todo,
                id: Date.now().toString(),
                _id: Date.now().toString(), // Keep both for compatibility
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

    /**
     * Update an existing todo
     * @param {string} id - Todo ID to update
     * @param {Object} updates - Object with properties to update
     * @returns {Object|null} Updated todo or null if not found
     */
    async updateTodo(id, updates) {
        try {
            const response = await fetch(`${this.apiBase}/todos/${id}`, {
                method: 'PUT',
                headers: this.getAuthHeaders(),
                body: JSON.stringify(updates)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data.todo;
        } catch (error) {
            console.warn('API not available, using local storage fallback');
            // Fallback to local storage for testing
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

    /**
     * Delete a todo
     * @param {string} id - Todo ID to delete
     * @returns {boolean} True if deleted, false if not found
     */
    async deleteTodo(id) {
        try {
            const response = await fetch(`${this.apiBase}/todos/${id}`, {
                method: 'DELETE',
                headers: this.getAuthHeaders()
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data.success;
        } catch (error) {
            console.warn('API not available, using local storage fallback');
            // Fallback to local storage for testing
            const todos = await this.getTodos();
            const filteredTodos = todos.filter(t => t.id !== id && t._id !== id);
            
            if (filteredTodos.length !== todos.length) {
                localStorage.setItem('todos', JSON.stringify(filteredTodos));
                return true;
            }
            return false;
        }
    }

    /**
     * Toggle todo completion status
     * @param {string} id - Todo ID to toggle
     * @returns {Object|null} Updated todo or null if not found
     */
    async toggleTodo(id) {
        try {
            const response = await fetch(`${this.apiBase}/todos/${id}/toggle`, {
                method: 'PATCH',
                headers: this.getAuthHeaders()
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data.todo;
        } catch (error) {
            console.warn('API not available, using local storage fallback');
            // Fallback to local storage for testing
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

    /**
     * Mark all todos as completed or uncompleted
     * @param {boolean} completed - Whether to mark as completed
     * @returns {Array} Updated todos array
     */
    async markAllTodos(completed) {
        try {
            const response = await fetch(`${this.apiBase}/todos/mark-all`, {
                method: 'PATCH',
                headers: this.getAuthHeaders(),
                body: JSON.stringify({ completed })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data.todos || [];
        } catch (error) {
            console.warn('API not available, using local storage fallback');
            // Fallback to local storage for testing
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

    /**
     * Delete all completed todos
     * @returns {Array} Remaining todos array
     */
    async clearCompleted() {
        try {
            const response = await fetch(`${this.apiBase}/todos/completed`, {
                method: 'DELETE',
                headers: this.getAuthHeaders()
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data.todos || [];
        } catch (error) {
            console.warn('API not available, using local storage fallback');
            // Fallback to local storage for testing
            const todos = await this.getTodos();
            const remainingTodos = todos.filter(todo => !todo.completed);
            localStorage.setItem('todos', JSON.stringify(remainingTodos));
            return remainingTodos;
        }
    }

    /**
     * Get app settings from user preferences
     * @returns {Object} Settings object
     */
    getSettings() {
        try {
            const user = JSON.parse(localStorage.getItem('user') || '{}');
            return user.preferences || {
                theme: 'light',
                sortBy: 'created',
                filter: 'all'
            };
        } catch (error) {
            console.error('Error loading settings:', error);
            return {
                theme: 'light',
                sortBy: 'created',
                filter: 'all'
            };
        }
    }

    /**
     * Save app settings to user preferences
     * @param {Object} settings - Settings object to save
     */
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
                    // Update local user data
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

// Export for use in other modules
window.TodoStorageManager = TodoStorageManager;
