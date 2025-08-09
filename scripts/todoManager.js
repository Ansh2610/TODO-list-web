// TodoManager: handles loading, CRUD, filtering and sorting of todos via the storage layer.

class TodoManager {
    constructor() {
        // Core state
        this.storage = new TodoStorageManager();
        this.todos = [];
        this.currentFilter = 'all';
        this.currentSort = 'created';

        // Simple event system
        this.listeners = {
            todosChanged: [],
            filterChanged: [],
            sortChanged: []
        };
    }

    // Load todos and settings
    async init() {
        this.todos = await this.storage.getTodos();
        const settings = this.storage.getSettings();
        this.currentFilter = settings.filter || 'all';
        this.currentSort = settings.sortBy || 'created';

        // Notify UI that data is ready
        this.emit('todosChanged', { action: 'loaded', todos: this.todos });
        console.log(`✅ TodoManager initialized: loaded ${this.todos.length} todos`);
    }

    // Event subscription
    addEventListener(event, callback) {
        if (this.listeners[event]) {
            this.listeners[event].push(callback);
        }
    }

    // Event unsubscription
    removeEventListener(event, callback) {
        if (this.listeners[event]) {
            this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
        }
    }

    // Event dispatch
    emit(event, data) {
        if (this.listeners[event]) {
            this.listeners[event].forEach(callback => callback(data));
        }
    }

    // Return a copy of all todos
    getAllTodos() {
        return [...this.todos];
    }

    // Return filtered + sorted todos (no mutation)
    getFilteredTodos() {
        let filteredTodos = [...this.todos];

        // Filter
        switch (this.currentFilter) {
            case 'active':
                filteredTodos = filteredTodos.filter(todo => !todo.completed);
                break;
            case 'completed':
                filteredTodos = filteredTodos.filter(todo => todo.completed);
                break;
            case 'all':
            default:
                break;
        }

        // Sort
        filteredTodos.sort(this.getSortFunction(this.currentSort));
        return filteredTodos;
    }

    // Create todo
    async addTodo(todoData) {
        if (!todoData.text || typeof todoData.text !== 'string' || !todoData.text.trim()) {
            throw new Error('Todo text is required and must be a non-empty string');
        }

        const cleanTodoData = {
            text: todoData.text.trim(),
            priority: this.validatePriority(todoData.priority),
            dueDate: this.validateDate(todoData.dueDate)
        };

        try {
            const newTodo = await this.storage.addTodo(cleanTodoData);
            this.todos = await this.storage.getTodos();

            this.emit('todosChanged', {
                action: 'add',
                todo: newTodo,
                todos: this.getFilteredTodos()
            });

            return newTodo;
        } catch (error) {
            console.error('Error adding todo:', error);
            throw error;
        }
    }

    // Update todo
    updateTodo(id, updates) {
        if (!id) throw new Error('Todo ID is required');

        const validUpdates = {};
        if (updates.text !== undefined) {
            if (typeof updates.text !== 'string' || !updates.text.trim()) {
                throw new Error('Todo text must be a non-empty string');
            }
            validUpdates.text = updates.text.trim();
        }
        if (updates.priority !== undefined) {
            validUpdates.priority = this.validatePriority(updates.priority);
        }
        if (updates.dueDate !== undefined) {
            validUpdates.dueDate = this.validateDate(updates.dueDate);
        }
        if (updates.completed !== undefined) {
            validUpdates.completed = Boolean(updates.completed);
        }

        const updatedTodo = this.storage.updateTodo(id, validUpdates);
        if (updatedTodo) {
            this.todos = this.storage.getTodos();
            this.emit('todosChanged', {
                action: 'update',
                todo: updatedTodo,
                todos: this.getFilteredTodos()
            });
        }
        return updatedTodo;
    }

    // Delete todo
    async deleteTodo(id) {
        if (!id) throw new Error('Todo ID is required');

        try {
            const todoToDelete = this.todos.find(todo => todo.id === id);
            const success = await this.storage.deleteTodo(id);
            if (success) {
                this.todos = await this.storage.getTodos();
                this.emit('todosChanged', {
                    action: 'delete',
                    todo: todoToDelete,
                    todos: this.getFilteredTodos()
                });
            }
            return success;
        } catch (error) {
            console.error('Error deleting todo:', error);
            throw error;
        }
    }

    // Toggle completed
    async toggleTodo(id) {
        if (!id) throw new Error('Todo ID is required');

        try {
            const updatedTodo = await this.storage.toggleTodo(id);
            if (updatedTodo) {
                this.todos = await this.storage.getTodos();
                this.emit('todosChanged', {
                    action: 'toggle',
                    todo: updatedTodo,
                    todos: this.getFilteredTodos()
                });
            }
            return updatedTodo;
        } catch (error) {
            console.error('Error toggling todo:', error);
            throw error;
        }
    }

    // Mark all todos as completed/uncompleted
    markAllTodos(completed = true) {
        const updatedTodos = this.storage.markAllTodos(completed);
        this.todos = updatedTodos;
        this.emit('todosChanged', {
            action: 'markAll',
            completed,
            todos: this.getFilteredTodos()
        });
    }

    // Remove completed todos
    clearCompleted() {
        const remainingTodos = this.storage.clearCompleted();
        this.todos = remainingTodos;
        this.emit('todosChanged', {
            action: 'clearCompleted',
            todos: this.getFilteredTodos()
        });
    }

    // Set current filter: 'all' | 'active' | 'completed'
    async setFilter(filter) {
        const validFilters = ['all', 'active', 'completed'];
        if (!validFilters.includes(filter)) {
            throw new Error(`Invalid filter: ${filter}. Must be one of: ${validFilters.join(', ')}`);
        }
        this.currentFilter = filter;
        await this.storage.saveSettings({ filter });
        this.emit('filterChanged', { filter, todos: this.getFilteredTodos() });
    }

    // Set sort: 'created' | 'priority' | 'dueDate' | 'alphabetical'
    async setSortBy(sortBy) {
        const validSorts = ['created', 'priority', 'dueDate', 'alphabetical'];
        if (!validSorts.includes(sortBy)) {
            throw new Error(`Invalid sort method: ${sortBy}. Must be one of: ${validSorts.join(', ')}`);
        }
        this.currentSort = sortBy;
        await this.storage.saveSettings({ sortBy });
        this.emit('sortChanged', { sortBy, todos: this.getFilteredTodos() });
    }

    // Counts for UI badges
    getTodoCounts() {
        const all = this.todos.length;
        const completed = this.todos.filter(todo => todo.completed).length;
        const active = all - completed;
        return { all, active, completed };
    }

    // Simple helpers
    searchTodos(searchTerm) { return this.storage.searchTodos(searchTerm); }
    getTodosByPriority(priority) { return this.storage.getTodosByPriority(priority); }
    getOverdueTodos() { return this.storage.getOverdueTodos(); }
    getStats() { return this.storage.getStorageStats(); }
    exportTodos() { return this.storage.exportTodos(); }

    importTodos(jsonData) {
        const success = this.storage.importTodos(jsonData);
        if (success) {
            this.todos = this.storage.getTodos();
            const settings = this.storage.getSettings();
            this.currentFilter = settings.filter || 'all';
            this.currentSort = settings.sortBy || 'created';
            this.emit('todosChanged', { action: 'import', todos: this.getFilteredTodos() });
        }
        return success;
    }

    // Validation
    validatePriority(priority) {
        const validPriorities = ['high', 'medium', 'low'];
        if (!priority || !validPriorities.includes(priority)) return 'medium';
        return priority;
    }

    validateDate(date) {
        if (!date) return null;
        const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
        if (!dateRegex.test(date)) return null;
        const dateObj = new Date(date);
        if (isNaN(dateObj.getTime())) return null;
        return date;
    }

    // Sorting
    getSortFunction(sortBy) {
        const priorityOrder = { high: 3, medium: 2, low: 1 };
        switch (sortBy) {
            case 'priority':
                return (a, b) => {
                    const priorityDiff = priorityOrder[b.priority] - priorityOrder[a.priority];
                    if (priorityDiff !== 0) return priorityDiff;
                    return new Date(b.createdAt) - new Date(a.createdAt);
                };
            case 'dueDate':
                return (a, b) => {
                    if (!a.dueDate && !b.dueDate) return 0;
                    if (!a.dueDate) return 1;
                    if (!b.dueDate) return -1;
                    return new Date(a.dueDate) - new Date(b.dueDate);
                };
            case 'alphabetical':
                return (a, b) => a.text.toLowerCase().localeCompare(b.text.toLowerCase());
            case 'created':
            default:
                return (a, b) => new Date(b.createdAt) - new Date(a.createdAt);
        }
    }

    getCurrentFilter() { return this.currentFilter; }
    getCurrentSort() { return this.currentSort; }
}

// Export
window.TodoManager = TodoManager;
