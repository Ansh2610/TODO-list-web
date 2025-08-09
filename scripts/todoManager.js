/**
 * TODO Manager - Core business logic for the TODO List Application
 * Handles todo operations and data management
 */

class TodoManager {
    constructor() {
        this.storage = new TodoStorageManager();
        this.todos = [];
        this.currentFilter = 'all';
        this.currentSort = 'created';
        this.listeners = {
            todosChanged: [],
            filterChanged: [],
            sortChanged: []
        };
        
        this.init();
    }

    async init() {
        // Load todos and settings from storage
        this.todos = await this.storage.getTodos();
        const settings = this.storage.getSettings();
        this.currentFilter = settings.filter || 'all';
        this.currentSort = settings.sortBy || 'created';
    }

    /**
     * Add event listener
     * @param {string} event - Event name
     * @param {Function} callback - Callback function
     */
    addEventListener(event, callback) {
        if (this.listeners[event]) {
            this.listeners[event].push(callback);
        }
    }

    /**
     * Remove event listener
     * @param {string} event - Event name
     * @param {Function} callback - Callback function to remove
     */
    removeEventListener(event, callback) {
        if (this.listeners[event]) {
            this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
        }
    }

    /**
     * Emit event to all listeners
     * @param {string} event - Event name
     * @param {*} data - Data to pass to listeners
     */
    emit(event, data) {
        if (this.listeners[event]) {
            this.listeners[event].forEach(callback => callback(data));
        }
    }

    /**
     * Get all todos
     * @returns {Array} Array of all todos
     */
    getAllTodos() {
        return [...this.todos];
    }

    /**
     * Get filtered and sorted todos
     * @returns {Array} Filtered and sorted todos
     */
    getFilteredTodos() {
        let filteredTodos = [...this.todos];

        // Apply filter
        switch (this.currentFilter) {
            case 'active':
                filteredTodos = filteredTodos.filter(todo => !todo.completed);
                break;
            case 'completed':
                filteredTodos = filteredTodos.filter(todo => todo.completed);
                break;
            case 'all':
            default:
                // No filtering needed
                break;
        }

        // Apply sorting
        filteredTodos.sort(this.getSortFunction(this.currentSort));

        return filteredTodos;
    }

    /**
     * Add a new todo
     * @param {Object} todoData - Todo data object
     * @returns {Object} The created todo
     */
    async addTodo(todoData) {
        // Validate input
        if (!todoData.text || typeof todoData.text !== 'string' || !todoData.text.trim()) {
            throw new Error('Todo text is required and must be a non-empty string');
        }

        // Clean and validate the todo data
        const cleanTodoData = {
            text: todoData.text.trim(),
            priority: this.validatePriority(todoData.priority),
            dueDate: this.validateDate(todoData.dueDate)
        };

        try {
            // Add to storage
            const newTodo = await this.storage.addTodo(cleanTodoData);
            
            // Update local todos array
            this.todos = await this.storage.getTodos();
            
            // Emit change event
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

    /**
     * Update an existing todo
     * @param {string} id - Todo ID
     * @param {Object} updates - Updates to apply
     * @returns {Object|null} Updated todo or null if not found
     */
    updateTodo(id, updates) {
        if (!id) {
            throw new Error('Todo ID is required');
        }

        // Validate updates
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

        // Update in storage
        const updatedTodo = this.storage.updateTodo(id, validUpdates);
        
        if (updatedTodo) {
            // Update local todos array
            this.todos = this.storage.getTodos();
            
            // Emit change event
            this.emit('todosChanged', {
                action: 'update',
                todo: updatedTodo,
                todos: this.getFilteredTodos()
            });
        }

        return updatedTodo;
    }

    /**
     * Delete a todo
     * @param {string} id - Todo ID to delete
     * @returns {boolean} True if deleted successfully
     */
    async deleteTodo(id) {
        if (!id) {
            throw new Error('Todo ID is required');
        }

        try {
            const todoToDelete = this.todos.find(todo => todo.id === id);
            const success = await this.storage.deleteTodo(id);
            
            if (success) {
                // Update local todos array
                this.todos = await this.storage.getTodos();
                
                // Emit change event
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

    /**
     * Toggle todo completion
     * @param {string} id - Todo ID
     * @returns {Object|null} Updated todo or null if not found
     */
    async toggleTodo(id) {
        if (!id) {
            throw new Error('Todo ID is required');
        }

        try {
            const updatedTodo = await this.storage.toggleTodo(id);
            
            if (updatedTodo) {
                // Update local todos array
                this.todos = await this.storage.getTodos();
                
                // Emit change event
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

    /**
     * Mark all todos as completed or uncompleted
     * @param {boolean} completed - Completion status
     */
    markAllTodos(completed = true) {
        const updatedTodos = this.storage.markAllTodos(completed);
        this.todos = updatedTodos;
        
        this.emit('todosChanged', {
            action: 'markAll',
            completed,
            todos: this.getFilteredTodos()
        });
    }

    /**
     * Clear all completed todos
     */
    clearCompleted() {
        const remainingTodos = this.storage.clearCompleted();
        this.todos = remainingTodos;
        
        this.emit('todosChanged', {
            action: 'clearCompleted',
            todos: this.getFilteredTodos()
        });
    }

    /**
     * Set current filter
     * @param {string} filter - Filter type ('all', 'active', 'completed')
     */
    async setFilter(filter) {
        const validFilters = ['all', 'active', 'completed'];
        if (!validFilters.includes(filter)) {
            throw new Error(`Invalid filter: ${filter}. Must be one of: ${validFilters.join(', ')}`);
        }

        this.currentFilter = filter;
        await this.storage.saveSettings({ filter });
        
        this.emit('filterChanged', {
            filter,
            todos: this.getFilteredTodos()
        });
    }

    /**
     * Set current sort method
     * @param {string} sortBy - Sort method ('created', 'priority', 'dueDate', 'alphabetical')
     */
    async setSortBy(sortBy) {
        const validSorts = ['created', 'priority', 'dueDate', 'alphabetical'];
        if (!validSorts.includes(sortBy)) {
            throw new Error(`Invalid sort method: ${sortBy}. Must be one of: ${validSorts.join(', ')}`);
        }

        this.currentSort = sortBy;
        await this.storage.saveSettings({ sortBy });
        
        this.emit('sortChanged', {
            sortBy,
            todos: this.getFilteredTodos()
        });
    }

    /**
     * Get todo counts by status
     * @returns {Object} Count object with all, active, and completed counts
     */
    getTodoCounts() {
        const all = this.todos.length;
        const completed = this.todos.filter(todo => todo.completed).length;
        const active = all - completed;

        return { all, active, completed };
    }

    /**
     * Search todos by text
     * @param {string} searchTerm - Search term
     * @returns {Array} Matching todos
     */
    searchTodos(searchTerm) {
        return this.storage.searchTodos(searchTerm);
    }

    /**
     * Get todos by priority
     * @param {string} priority - Priority level
     * @returns {Array} Todos with specified priority
     */
    getTodosByPriority(priority) {
        return this.storage.getTodosByPriority(priority);
    }

    /**
     * Get overdue todos
     * @returns {Array} Overdue todos
     */
    getOverdueTodos() {
        return this.storage.getOverdueTodos();
    }

    /**
     * Get storage statistics
     * @returns {Object} Storage statistics
     */
    getStats() {
        return this.storage.getStorageStats();
    }

    /**
     * Export todos as JSON
     * @returns {string} JSON string of export data
     */
    exportTodos() {
        return this.storage.exportTodos();
    }

    /**
     * Import todos from JSON
     * @param {string} jsonData - JSON data to import
     * @returns {boolean} Success status
     */
    importTodos(jsonData) {
        const success = this.storage.importTodos(jsonData);
        if (success) {
            this.todos = this.storage.getTodos();
            const settings = this.storage.getSettings();
            this.currentFilter = settings.filter || 'all';
            this.currentSort = settings.sortBy || 'created';
            
            this.emit('todosChanged', {
                action: 'import',
                todos: this.getFilteredTodos()
            });
        }
        return success;
    }

    /**
     * Validate priority value
     * @param {string} priority - Priority to validate
     * @returns {string} Valid priority
     */
    validatePriority(priority) {
        const validPriorities = ['high', 'medium', 'low'];
        if (!priority || !validPriorities.includes(priority)) {
            return 'medium'; // Default priority
        }
        return priority;
    }

    /**
     * Validate date value
     * @param {string} date - Date to validate
     * @returns {string|null} Valid date string or null
     */
    validateDate(date) {
        if (!date) return null;
        
        // Check if it's a valid date string (YYYY-MM-DD format)
        const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
        if (!dateRegex.test(date)) {
            return null;
        }

        const dateObj = new Date(date);
        if (isNaN(dateObj.getTime())) {
            return null;
        }

        return date;
    }

    /**
     * Get sort function based on sort method
     * @param {string} sortBy - Sort method
     * @returns {Function} Sort function
     */
    getSortFunction(sortBy) {
        const priorityOrder = { high: 3, medium: 2, low: 1 };

        switch (sortBy) {
            case 'priority':
                return (a, b) => {
                    const priorityDiff = priorityOrder[b.priority] - priorityOrder[a.priority];
                    if (priorityDiff !== 0) return priorityDiff;
                    // Secondary sort by creation date if priorities are equal
                    return new Date(b.createdAt) - new Date(a.createdAt);
                };

            case 'dueDate':
                return (a, b) => {
                    // Items without due dates go to the end
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

    /**
     * Get current filter
     * @returns {string} Current filter
     */
    getCurrentFilter() {
        return this.currentFilter;
    }

    /**
     * Get current sort method
     * @returns {string} Current sort method
     */
    getCurrentSort() {
        return this.currentSort;
    }
}

// Export for use in other modules
window.TodoManager = TodoManager;
