// Todo model: user-scoped tasks with metadata, indexes, and virtuals
const mongoose = require('mongoose');

const todoSchema = new mongoose.Schema({
  text: {
    type: String,
    required: [true, 'Todo text is required'],
    trim: true,
    maxlength: [200, 'Todo text cannot exceed 200 characters']
  },
  completed: { type: Boolean, default: false },
  priority: { type: String, enum: ['high', 'medium', 'low'], default: 'medium' },
  dueDate: { type: Date },
  description: { type: String, maxlength: [500, 'Description cannot exceed 500 characters'], trim: true },
  category: { type: String, enum: ['work', 'personal', 'shopping', 'health', 'education', 'other'], default: null },
  emailNotifications: { type: Boolean, default: false },
  reminderFrequency: { type: String, enum: ['1h', '2h', '12h', '1d', '3d', '7d'], default: null },
  userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  order: { type: Number, default: 0 }
}, { timestamps: true });

// Query indexes
todoSchema.index({ userId: 1, createdAt: -1 });
todoSchema.index({ userId: 1, completed: 1 });
todoSchema.index({ userId: 1, priority: 1 });
todoSchema.index({ userId: 1, dueDate: 1 });

// Virtual: overdue if past due and not completed
todoSchema.virtual('isOverdue').get(function() {
  if (!this.dueDate || this.completed) return false;
  return this.dueDate < new Date().setHours(0, 0, 0, 0);
});

// Include virtuals in JSON
todoSchema.set('toJSON', { virtuals: true });

module.exports = mongoose.model('Todo', todoSchema);
