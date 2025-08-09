const express = require('express');
const { body, validationResult } = require('express-validator');
const Todo = require('../models/Todo');
const auth = require('../middleware/auth');

const router = express.Router();

// Apply auth middleware to all routes
router.use(auth);

// Get all todos for the authenticated user
router.get('/', async (req, res) => {
  try {
    const { filter, sortBy, search } = req.query;
    
    // Build query
    let query = { userId: req.user._id };
    
    // Apply filter
    if (filter === 'active') {
      query.completed = false;
    } else if (filter === 'completed') {
      query.completed = true;
    }
    
    // Apply search
    if (search) {
      query.text = { $regex: search, $options: 'i' };
    }
    
    // Build sort object
    let sort = { createdAt: -1 }; // Default sort
    
    switch (sortBy) {
      case 'priority':
        sort = { 
          priority: { $meta: 'textScore' },
          createdAt: -1 
        };
        // Custom priority sorting
        break;
      case 'dueDate':
        sort = { dueDate: 1, createdAt: -1 };
        break;
      case 'alphabetical':
        sort = { text: 1 };
        break;
      case 'created':
      default:
        sort = { createdAt: -1 };
        break;
    }
    
    let todos = await Todo.find(query).sort(sort);
    
    // Custom priority sorting if needed
    if (sortBy === 'priority') {
      const priorityOrder = { high: 3, medium: 2, low: 1 };
      todos = todos.sort((a, b) => {
        const priorityDiff = priorityOrder[b.priority] - priorityOrder[a.priority];
        if (priorityDiff !== 0) return priorityDiff;
        return new Date(b.createdAt) - new Date(a.createdAt);
      });
    }
    
    res.json({
      success: true,
      todos
    });

  } catch (error) {
    console.error('Get todos error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch todos',
      error: error.message
    });
  }
});

// Create a new todo
router.post('/', [
  body('text')
    .notEmpty()
    .withMessage('Todo text is required')
    .isLength({ max: 200 })
    .withMessage('Todo text cannot exceed 200 characters'),
  body('priority')
    .optional()
    .isIn(['high', 'medium', 'low'])
    .withMessage('Priority must be high, medium, or low'),
  body('dueDate')
    .optional()
    .isISO8601()
    .withMessage('Due date must be a valid date')
], async (req, res) => {
  try {
    // Check validation errors
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const { text, priority = 'medium', dueDate } = req.body;
    
    // Create todo
    const todo = new Todo({
      text: text.trim(),
      priority,
      dueDate: dueDate || null,
      userId: req.user._id
    });

    await todo.save();

    res.status(201).json({
      success: true,
      message: 'Todo created successfully',
      todo
    });

  } catch (error) {
    console.error('Create todo error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to create todo',
      error: error.message
    });
  }
});

// Update a todo
router.put('/:id', [
  body('text')
    .optional()
    .notEmpty()
    .withMessage('Todo text cannot be empty')
    .isLength({ max: 200 })
    .withMessage('Todo text cannot exceed 200 characters'),
  body('priority')
    .optional()
    .isIn(['high', 'medium', 'low'])
    .withMessage('Priority must be high, medium, or low'),
  body('completed')
    .optional()
    .isBoolean()
    .withMessage('Completed must be a boolean'),
  body('dueDate')
    .optional()
    .isISO8601()
    .withMessage('Due date must be a valid date')
], async (req, res) => {
  try {
    // Check validation errors
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const { id } = req.params;
    const updates = req.body;

    // Find and update todo
    const todo = await Todo.findOneAndUpdate(
      { _id: id, userId: req.user._id },
      { $set: updates },
      { new: true, runValidators: true }
    );

    if (!todo) {
      return res.status(404).json({
        success: false,
        message: 'Todo not found'
      });
    }

    res.json({
      success: true,
      message: 'Todo updated successfully',
      todo
    });

  } catch (error) {
    console.error('Update todo error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to update todo',
      error: error.message
    });
  }
});

// Delete a todo
router.delete('/:id', async (req, res) => {
  try {
    const { id } = req.params;

    const todo = await Todo.findOneAndDelete({
      _id: id,
      userId: req.user._id
    });

    if (!todo) {
      return res.status(404).json({
        success: false,
        message: 'Todo not found'
      });
    }

    res.json({
      success: true,
      message: 'Todo deleted successfully',
      todo
    });

  } catch (error) {
    console.error('Delete todo error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to delete todo',
      error: error.message
    });
  }
});

// Toggle todo completion
router.patch('/:id/toggle', async (req, res) => {
  try {
    const { id } = req.params;

    const todo = await Todo.findOne({ _id: id, userId: req.user._id });
    
    if (!todo) {
      return res.status(404).json({
        success: false,
        message: 'Todo not found'
      });
    }

    todo.completed = !todo.completed;
    await todo.save();

    res.json({
      success: true,
      message: 'Todo toggled successfully',
      todo
    });

  } catch (error) {
    console.error('Toggle todo error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to toggle todo',
      error: error.message
    });
  }
});

// Mark all todos as completed/uncompleted
router.patch('/mark-all', [
  body('completed')
    .isBoolean()
    .withMessage('Completed must be a boolean')
], async (req, res) => {
  try {
    // Check validation errors
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const { completed } = req.body;

    await Todo.updateMany(
      { userId: req.user._id },
      { $set: { completed } }
    );

    const todos = await Todo.find({ userId: req.user._id }).sort({ createdAt: -1 });

    res.json({
      success: true,
      message: `All todos marked as ${completed ? 'completed' : 'active'}`,
      todos
    });

  } catch (error) {
    console.error('Mark all todos error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to mark all todos',
      error: error.message
    });
  }
});

// Clear completed todos
router.delete('/completed', async (req, res) => {
  try {
    const result = await Todo.deleteMany({
      userId: req.user._id,
      completed: true
    });

    const todos = await Todo.find({ userId: req.user._id }).sort({ createdAt: -1 });

    res.json({
      success: true,
      message: `${result.deletedCount} completed todos deleted`,
      todos
    });

  } catch (error) {
    console.error('Clear completed todos error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to clear completed todos',
      error: error.message
    });
  }
});

// Get todo statistics
router.get('/stats', async (req, res) => {
  try {
    const userId = req.user._id;

    const stats = await Todo.aggregate([
      { $match: { userId } },
      {
        $group: {
          _id: null,
          total: { $sum: 1 },
          completed: { $sum: { $cond: ['$completed', 1, 0] } },
          active: { $sum: { $cond: ['$completed', 0, 1] } },
          high: { $sum: { $cond: [{ $eq: ['$priority', 'high'] }, 1, 0] } },
          medium: { $sum: { $cond: [{ $eq: ['$priority', 'medium'] }, 1, 0] } },
          low: { $sum: { $cond: [{ $eq: ['$priority', 'low'] }, 1, 0] } }
        }
      }
    ]);

    const result = stats[0] || {
      total: 0,
      completed: 0,
      active: 0,
      high: 0,
      medium: 0,
      low: 0
    };

    res.json({
      success: true,
      stats: result
    });

  } catch (error) {
    console.error('Get stats error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to get statistics',
      error: error.message
    });
  }
});

module.exports = router;
