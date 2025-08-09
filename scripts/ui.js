// UI Manager: handles rendering, modals, filters, theme, and notifications
class UIManager {
    constructor(todoManager) {
        this.todoManager = todoManager;
        this.elements = {};
        this.currentEditingId = null;
        
        this.init();
        this.setupEventListeners();
        this.setupTodoManagerListeners();
    }

    init() {
        // Cache DOM elements
        this.elements = {
            // Enhanced add task elements
            personalizedAddBtn: document.getElementById('personalizedAddBtn'),
            personalizedGreeting: document.getElementById('personalizedGreeting'),
            createTaskModal: document.getElementById('createTaskModal'),
            enhancedTaskForm: document.getElementById('enhancedTaskForm'),
            closeCreateModal: document.getElementById('closeCreateModal'),
            cancelCreateTask: document.getElementById('cancelCreateTask'),
            createTaskBtn: document.getElementById('createTaskBtn'),
            
            // Enhanced form fields
            taskTitle: document.getElementById('taskTitle'),
            taskDescription: document.getElementById('taskDescription'),
            taskPriority: document.getElementById('taskPriority'),
            taskDueDate: document.getElementById('taskDueDate'),
            taskDueTime: document.getElementById('taskDueTime'),
            taskCategory: document.getElementById('taskCategory'),
            enableEmailNotifications: document.getElementById('enableEmailNotifications'),
            notificationOptions: document.getElementById('notificationOptions'),
            reminderFrequency: document.getElementById('reminderFrequency'),
            
            // Filter elements
            filterButtons: document.querySelectorAll('.filter-btn'),
            sortSelect: document.getElementById('sortBy'),
            
            // Count elements
            allCount: document.getElementById('allCount'),
            activeCount: document.getElementById('activeCount'),
            completedCount: document.getElementById('completedCount'),
            
            // Todo list
            todoList: document.getElementById('todoList'),
            emptyState: document.getElementById('emptyState'),
            
            // Bulk actions
            markAllCompleteBtn: document.getElementById('markAllComplete'),
            clearCompletedBtn: document.getElementById('clearCompleted'),
            
            // Theme toggle
            themeToggle: document.getElementById('themeToggle'),
            
            // Modal elements
            editModal: document.getElementById('editModal'),
            editTodoForm: document.getElementById('editTodoForm'),
            editTodoText: document.getElementById('editTodoText'),
            editTodoPriority: document.getElementById('editTodoPriority'),
            editTodoDueDate: document.getElementById('editTodoDueDate'),
            closeEditModal: document.getElementById('closeEditModal'),
            cancelEdit: document.getElementById('cancelEdit'),
            saveEdit: document.getElementById('saveEdit')
        };

        // Check for missing elements
        Object.keys(this.elements).forEach(key => {
            if (!this.elements[key]) {
                console.error(`Missing element: ${key}`);
            } else if (this.elements[key].length === 0) {
                console.error(`Empty NodeList for: ${key}`);
            } else {
                console.log(`✓ Found element: ${key}`);
            }
        });

        // Ensure modals are properly hidden on initialization
        this.ensureModalsHidden();

        // Initialize theme
        this.initializeTheme();
        
        // Update personalized greeting
        this.updatePersonalizedGreeting();
        
        // Initial render
        this.renderTodos();
        this.updateCounts();
        this.updateFilterButtons();
        this.updateSortSelect();
    }

    setupEventListeners() {
        console.log('Setting up event listeners...');
        
        // Enhanced add task button
        if (this.elements.personalizedAddBtn) {
            this.elements.personalizedAddBtn.addEventListener('click', () => {
                this.openCreateTaskModal();
            });
        } else {
            console.error('personalizedAddBtn element not found');
        }

        // Enhanced task creation modal
        if (this.elements.enhancedTaskForm) {
            this.elements.enhancedTaskForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleEnhancedTaskCreation();
            });
        } else {
            console.error('enhancedTaskForm element not found');
        }

        if (this.elements.closeCreateModal) {
            this.elements.closeCreateModal.addEventListener('click', () => {
                this.closeCreateTaskModal();
            });
        } else {
            console.error('closeCreateModal element not found');
        }

        if (this.elements.cancelCreateTask) {
            this.elements.cancelCreateTask.addEventListener('click', () => {
                this.closeCreateTaskModal();
            });
        } else {
            console.error('cancelCreateTask element not found');
        }

        if (this.elements.createTaskBtn) {
            this.elements.createTaskBtn.addEventListener('click', () => {
                this.handleEnhancedTaskCreation();
            });
        } else {
            console.error('createTaskBtn element not found');
        }

        // Email notifications toggle
        if (this.elements.enableEmailNotifications) {
            this.elements.enableEmailNotifications.addEventListener('change', (e) => {
                if (this.elements.notificationOptions) {
                    this.elements.notificationOptions.style.display = e.target.checked ? 'block' : 'none';
                }
            });
        } else {
            console.error('enableEmailNotifications element not found');
        }

        // Modal backdrop click to close
        if (this.elements.createTaskModal) {
            this.elements.createTaskModal.addEventListener('click', (e) => {
                if (e.target === this.elements.createTaskModal) {
                    this.closeCreateTaskModal();
                }
            });
        } else {
            console.error('createTaskModal element not found');
        }

        // Filter buttons with debouncing
        let filterTimeout;
        if (this.elements.filterButtons && this.elements.filterButtons.length > 0) {
            this.elements.filterButtons.forEach(btn => {
                btn.addEventListener('click', async (e) => {
                    try {
                        // Clear previous timeout
                        clearTimeout(filterTimeout);
                        
                        // Disable all filter buttons temporarily
                        this.elements.filterButtons.forEach(b => b.disabled = true);
                        
                        const filter = e.target.dataset.filter;
                        
                        // Add small delay to prevent rapid clicking
                        filterTimeout = setTimeout(async () => {
                            try {
                                await this.todoManager.setFilter(filter);
                            } catch (error) {
                                console.error('Error setting filter:', error);
                                this.showError('Failed to change filter. Please try again.');
                            } finally {
                                // Re-enable filter buttons
                                this.elements.filterButtons.forEach(b => b.disabled = false);
                            }
                        }, 100);
                    } catch (error) {
                        console.error('Error setting filter:', error);
                        this.showError('Failed to change filter. Please try again.');
                        this.elements.filterButtons.forEach(b => b.disabled = false);
                    }
                });
            });
        } else {
            console.error('filterButtons elements not found');
        }

        // Sort select
        if (this.elements.sortSelect) {
            this.elements.sortSelect.addEventListener('change', async (e) => {
                try {
                    await this.todoManager.setSortBy(e.target.value);
                } catch (error) {
                    console.error('Error setting sort:', error);
                    this.showError('Failed to change sort order. Please try again.');
                }
            });
        } else {
            console.error('sortSelect element not found');
        }

        // Bulk actions
        if (this.elements.markAllCompleteBtn) {
            this.elements.markAllCompleteBtn.addEventListener('click', () => {
                this.handleMarkAllComplete();
            });
        } else {
            console.error('markAllCompleteBtn element not found');
        }

        if (this.elements.clearCompletedBtn) {
            this.elements.clearCompletedBtn.addEventListener('click', () => {
                this.handleClearCompleted();
            });
        } else {
            console.error('clearCompletedBtn element not found');
        }

        // Theme toggle
        if (this.elements.themeToggle) {
            this.elements.themeToggle.addEventListener('click', () => {
                this.toggleTheme();
            });
        } else {
            console.error('themeToggle element not found');
        }

        // Modal events
        if (this.elements.closeEditModal) {
            this.elements.closeEditModal.addEventListener('click', () => {
                this.closeEditModal();
            });
        } else {
            console.error('closeEditModal element not found');
        }

        if (this.elements.cancelEdit) {
            this.elements.cancelEdit.addEventListener('click', () => {
                this.closeEditModal();
            });
        } else {
            console.error('cancelEdit element not found');
        }

        if (this.elements.saveEdit) {
            this.elements.saveEdit.addEventListener('click', () => {
                this.handleSaveEdit();
            });
        } else {
            console.error('saveEdit element not found');
        }

        // Additional listeners that were previously outside any method
        if (this.elements.editModal) {
            this.elements.editModal.addEventListener('click', (e) => {
                if (e.target === this.elements.editModal) {
                    this.closeEditModal();
                }
            });
        }

        if (this.elements.editTodoForm) {
            this.elements.editTodoForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleSaveEdit();
            });
        }

        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });

        // Auto-resize for textarea inputs (enhanced editor)
        if (this.elements.taskDescription) {
            this.elements.taskDescription.addEventListener('input', (e) => {
                this.adjustInputHeight(e.target);
            });
        }

        console.log('Event listener setup complete');
    }

    setupTodoManagerListeners() {
        // Listen to todo manager events
        this.todoManager.addEventListener('todosChanged', (data) => {
            this.renderTodos();
            this.updateCounts();
            
            // Don't show notification for initial data loading
            if (data.action !== 'loaded') {
                this.showNotification(this.getActionMessage(data.action, data.todo));
            }
        });

        this.todoManager.addEventListener('filterChanged', () => {
            this.renderTodos();
            this.updateFilterButtons();
        });

        this.todoManager.addEventListener('sortChanged', () => {
            this.renderTodos();
            this.updateSortSelect();
        });
    }

    handleAddTodo() {
        const text = this.elements.todoInput.value.trim();
        const priority = this.elements.todoPriority.value;
        const dueDate = this.elements.todoDueDate.value;

        if (!text) {
            this.showNotification('Please enter a todo text', 'error');
            this.elements.todoInput.focus();
            return;
        }

        try {
            this.todoManager.addTodo({
                text,
                priority,
                dueDate: dueDate || null
            });

            // Reset form
            this.elements.addTodoForm.reset();
            this.elements.todoInput.focus();
        } catch (error) {
            this.showNotification(error.message, 'error');
        }
    }

    handleMarkAllComplete() {
        const activeTodos = this.todoManager.getAllTodos().filter(todo => !todo.completed);
        const shouldComplete = activeTodos.length > 0;
        
        this.todoManager.markAllTodos(shouldComplete);
    }

    handleClearCompleted() {
        const completedCount = this.todoManager.getAllTodos().filter(todo => todo.completed).length;
        
        if (completedCount === 0) {
            this.showNotification('No completed todos to clear', 'info');
            return;
        }

        if (confirm(`Are you sure you want to delete ${completedCount} completed todo(s)?`)) {
            this.todoManager.clearCompleted();
        }
    }

    async handleTodoToggle(id) {
        try {
            await this.todoManager.toggleTodo(id);
        } catch (error) {
            console.error('Error toggling todo:', error);
            this.showError('Failed to update todo. Please try again.');
        }
    }

    async handleTodoDelete(id) {
        try {
            const todo = this.todoManager.getAllTodos().find(t => t.id === id);
            if (todo && confirm(`Are you sure you want to delete "${todo.text}"?`)) {
                await this.todoManager.deleteTodo(id);
            }
        } catch (error) {
            console.error('Error deleting todo:', error);
            this.showError('Failed to delete todo. Please try again.');
        }
    }

    handleTodoEdit(id) {
        const todo = this.todoManager.getAllTodos().find(t => t.id === id);
        if (!todo) return;

        this.currentEditingId = id;
        this.elements.editTodoText.value = todo.text;
        this.elements.editTodoPriority.value = todo.priority;
        this.elements.editTodoDueDate.value = todo.dueDate || '';
        
        this.openEditModal();
    }

    handleSaveEdit() {
        const text = this.elements.editTodoText.value.trim();
        const priority = this.elements.editTodoPriority.value;
        const dueDate = this.elements.editTodoDueDate.value;

        if (!text) {
            this.showNotification('Please enter a todo text', 'error');
            this.elements.editTodoText.focus();
            return;
        }

        try {
            this.todoManager.updateTodo(this.currentEditingId, {
                text,
                priority,
                dueDate: dueDate || null
            });

            this.closeEditModal();
        } catch (error) {
            this.showNotification(error.message, 'error');
        }
    }

    openEditModal() {
        this.elements.editModal.style.display = '';
        this.elements.editModal.classList.add('active');
        this.elements.editTodoText.focus();
        document.body.style.overflow = 'hidden';
    }

    closeEditModal() {
        this.elements.editModal.classList.remove('active');
        this.elements.editModal.style.display = 'none';
        this.currentEditingId = null;
        document.body.style.overflow = '';
    }

    // Enhanced Task Creation Methods
    openCreateTaskModal() {
        this.elements.createTaskModal.style.display = '';
        this.elements.createTaskModal.classList.add('active');
        this.elements.taskTitle.focus();
        document.body.style.overflow = 'hidden';
        
        // Set default values
        this.elements.taskDueDate.value = new Date().toISOString().split('T')[0];
        this.elements.enableEmailNotifications.checked = false;
        this.elements.notificationOptions.style.display = 'none';
    }

    closeCreateTaskModal() {
        this.elements.createTaskModal.classList.remove('active');
        this.elements.createTaskModal.style.display = 'none';
        this.elements.enhancedTaskForm.reset();
        document.body.style.overflow = '';
    }

    ensureModalsHidden() {
        // Force hide all modals on initialization
        if (this.elements.createTaskModal) {
            this.elements.createTaskModal.classList.remove('active');
            this.elements.createTaskModal.style.display = 'none';
            console.log('✓ Create task modal hidden on init');
        }
        
        if (this.elements.editModal) {
            this.elements.editModal.classList.remove('active');
            this.elements.editModal.style.display = 'none';
            console.log('✓ Edit modal hidden on init');
        }
        
        // Ensure body overflow is reset
        document.body.style.overflow = '';
    }

    async handleEnhancedTaskCreation() {
        const title = this.elements.taskTitle.value.trim();
        const description = this.elements.taskDescription.value.trim();
        const priority = this.elements.taskPriority.value;
        const dueDate = this.elements.taskDueDate.value;
        const dueTime = this.elements.taskDueTime.value;
        const category = this.elements.taskCategory.value;
        const emailNotifications = this.elements.enableEmailNotifications.checked;
        const reminderFrequency = this.elements.reminderFrequency.value;

        if (!title) {
            this.showError('Please enter a task title');
            this.elements.taskTitle.focus();
            return;
        }

        try {
            // Show loading state
            this.elements.createTaskBtn.classList.add('loading');
            this.elements.createTaskBtn.disabled = true;

            // Combine date and time if both provided
            let combinedDueDate = dueDate;
            if (dueDate && dueTime) {
                combinedDueDate = `${dueDate}T${dueTime}`;
            }

            // Create enhanced task data
            const taskData = {
                text: title,
                description: description || null,
                priority: priority,
                dueDate: combinedDueDate || null,
                category: category || null,
                emailNotifications: emailNotifications,
                reminderFrequency: emailNotifications ? reminderFrequency : null
            };

            // Add the task
            await this.todoManager.addTodo(taskData);
            
            // Close modal and show success
            this.closeCreateTaskModal();
            this.showSuccess(`Task "${title}" created successfully!`);

        } catch (error) {
            console.error('Error creating task:', error);
            this.showError('Failed to create task. Please try again.');
        } finally {
            // Remove loading state
            this.elements.createTaskBtn.classList.remove('loading');
            this.elements.createTaskBtn.disabled = false;
        }
    }

    updatePersonalizedGreeting() {
        const userStr = localStorage.getItem('user');
        if (userStr) {
            try {
                const user = JSON.parse(userStr);
                const firstName = user.username.split(/[^a-zA-Z]/)[0]; // Get first part before any non-letter
                this.elements.personalizedGreeting.textContent = `Hey ${firstName}! Add a new task`;
            } catch (error) {
                console.error('Error parsing user data:', error);
                this.elements.personalizedGreeting.textContent = 'Hey there! Add a new task';
            }
        }
    }

    renderTodos() {
        const todos = this.todoManager.getFilteredTodos();
        
        if (todos.length === 0) {
            this.showEmptyState();
        } else {
            this.hideEmptyState();
            this.renderTodoList(todos);
        }
    }

    renderTodoList(todos) {
        this.elements.todoList.innerHTML = '';
        
        todos.forEach(todo => {
            const todoElement = this.createTodoElement(todo);
            this.elements.todoList.appendChild(todoElement);
        });
    }

    createTodoElement(todo) {
        const li = document.createElement('li');
        li.className = `todo-item ${todo.completed ? 'completed' : ''}`;
        li.dataset.id = todo.id;

        const priorityClass = `priority-${todo.priority}`;
        const isOverdue = this.isOverdue(todo.dueDate);
        const dueDateText = this.formatDueDate(todo.dueDate);

        li.innerHTML = `
            <input 
                type="checkbox" 
                class="todo-checkbox" 
                ${todo.completed ? 'checked' : ''}
                aria-label="Mark as ${todo.completed ? 'incomplete' : 'complete'}"
            >
            <div class="todo-content">
                <span class="todo-text">${this.escapeHtml(todo.text)}</span>
                <div class="todo-meta">
                    <span class="priority-badge ${priorityClass}">${todo.priority}</span>
                    ${todo.dueDate ? `
                        <span class="due-date ${isOverdue ? 'overdue' : ''}">
                            <i class="fas fa-calendar"></i>
                            ${dueDateText}
                        </span>
                    ` : ''}
                    <span class="created-date">
                        <i class="fas fa-clock"></i>
                        ${this.formatDate(todo.createdAt)}
                    </span>
                </div>
            </div>
            <div class="todo-actions">
                <button class="action-btn edit" title="Edit todo" aria-label="Edit todo">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="action-btn delete" title="Delete todo" aria-label="Delete todo">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;

        // Add event listeners
        const checkbox = li.querySelector('.todo-checkbox');
        const editBtn = li.querySelector('.edit');
        const deleteBtn = li.querySelector('.delete');

        checkbox.addEventListener('change', () => {
            this.handleTodoToggle(todo.id);
        });

        editBtn.addEventListener('click', () => {
            this.handleTodoEdit(todo.id);
        });

        deleteBtn.addEventListener('click', () => {
            this.handleTodoDelete(todo.id);
        });

        // Add double-click to edit
        li.addEventListener('dblclick', (e) => {
            if (!e.target.closest('.todo-actions') && !e.target.closest('.todo-checkbox')) {
                this.handleTodoEdit(todo.id);
            }
        });

        return li;
    }

    showEmptyState() {
        this.elements.emptyState.style.display = 'block';
        this.elements.todoList.style.display = 'none';
    }

    hideEmptyState() {
        this.elements.emptyState.style.display = 'none';
        this.elements.todoList.style.display = 'flex';
    }

    updateCounts() {
        const counts = this.todoManager.getTodoCounts();
        this.elements.allCount.textContent = counts.all;
        this.elements.activeCount.textContent = counts.active;
        this.elements.completedCount.textContent = counts.completed;
    }

    updateFilterButtons() {
        const currentFilter = this.todoManager.getCurrentFilter();
        this.elements.filterButtons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.filter === currentFilter);
        });
    }

    updateSortSelect() {
        const currentSort = this.todoManager.getCurrentSort();
        this.elements.sortSelect.value = currentSort;
    }

    initializeTheme() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        this.applyTheme(savedTheme);
    }

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(newTheme);
    }

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        const icon = this.elements.themeToggle.querySelector('i');
        icon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }

    showNotification(message, type = 'success') {
        // Create notification element if it doesn't exist
        let notification = document.querySelector('.notification');
        if (!notification) {
            notification = document.createElement('div');
            notification.className = 'notification';
            document.body.appendChild(notification);
        }

        notification.className = `notification ${type}`;
        notification.textContent = message;
        notification.style.display = 'block';

        // Auto-hide notification
        setTimeout(() => {
            notification.style.display = 'none';
        }, 3000);
    }

    handleKeyboardShortcuts(e) {
        // Ctrl/Cmd + Enter to add todo via enhanced modal
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            if (document.activeElement === this.elements.taskTitle ||
                document.activeElement === this.elements.taskDescription) {
                e.preventDefault();
                this.handleEnhancedTaskCreation();
            }
        }

        // Escape to close modal
        if (e.key === 'Escape') {
            if (this.elements.editModal && this.elements.editModal.classList.contains('active')) {
                this.closeEditModal();
            }
            if (this.elements.createTaskModal && this.elements.createTaskModal.classList.contains('active')) {
                this.closeCreateTaskModal();
            }
        }

        // Ctrl/Cmd + A to mark all complete (avoid inside inputs)
        if ((e.ctrlKey || e.metaKey) && e.key === 'a' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
            e.preventDefault();
            this.handleMarkAllComplete();
        }
    }

    adjustInputHeight(input) {
        input.style.height = 'auto';
        input.style.height = input.scrollHeight + 'px';
    }

    getActionMessage(action, todo) {
        switch (action) {
            case 'add':
                return `Added "${todo.text}"`;
            case 'update':
                return `Updated "${todo.text}"`;
            case 'delete':
                return `Deleted "${todo.text}"`;
            case 'toggle':
                return todo.completed ? `Completed "${todo.text}"` : `Reopened "${todo.text}"`;
            case 'markAll':
                return 'Updated all todos';
            case 'clearCompleted':
                return 'Cleared completed todos';
            case 'import':
                return 'Imported todos successfully';
            default:
                return 'Action completed';
        }
    }

    isOverdue(dueDate) {
        if (!dueDate) return false;
        const today = new Date().toISOString().split('T')[0];
        return dueDate < today;
    }

    formatDueDate(dueDate) {
        if (!dueDate) return '';
        
        const date = new Date(dueDate);
        const today = new Date();
        const diffTime = date - today;
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

        if (diffDays === 0) return 'Today';
        if (diffDays === 1) return 'Tomorrow';
        if (diffDays === -1) return 'Yesterday';
        if (diffDays < -1) return `${Math.abs(diffDays)} days ago`;
        if (diffDays > 1) return `In ${diffDays} days`;
        
        return date.toLocaleDateString();
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffTime = now - date;
        const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

        if (diffDays === 0) return 'Today';
        if (diffDays === 1) return 'Yesterday';
        if (diffDays < 7) return `${diffDays} days ago`;
        if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
        
        return date.toLocaleDateString();
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showError(message) {
        // Create a temporary error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.style.cssText = `
            background: var(--danger-color);
            color: var(--pixel-dark);
            border: 3px solid var(--pixel-dark);
            padding: var(--spacing-md);
            margin: var(--spacing-sm) 0;
            font-weight: bold;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            max-width: 300px;
        `;
        errorDiv.textContent = message;
        
        document.body.appendChild(errorDiv);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.parentNode.removeChild(errorDiv);
            }
        }, 3000);
    }

    showSuccess(message) {
        // Create a temporary success message
        const successDiv = document.createElement('div');
        successDiv.className = 'success-message';
        successDiv.style.cssText = `
            background: var(--success-color);
            color: var(--pixel-dark);
            border: 3px solid var(--pixel-dark);
            padding: var(--spacing-md);
            margin: var(--spacing-sm) 0;
            font-weight: bold;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            max-width: 300px;
            box-shadow: var(--shadow-md);
        `;
        successDiv.innerHTML = `<i class="fas fa-check-circle" style="margin-right: 8px;"></i>${message}`;
        
        document.body.appendChild(successDiv);
        
        // Auto-remove after 4 seconds
        setTimeout(() => {
            if (successDiv.parentNode) {
                successDiv.parentNode.removeChild(successDiv);
            }
        }, 4000);
    }
}

// Export for use in other modules
window.UIManager = UIManager;
