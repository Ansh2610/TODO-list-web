// Express server: security, API routes, MongoDB connection, and static hosting
const mongoose = require('mongoose');
require('dotenv').config();
const { app } = require('./server/app');

// MongoDB
mongoose.connect(process.env.MONGODB_URI)
.then(() => {
  console.log('✅ Connected to MongoDB');
})
.catch((error) => {
  console.error('❌ MongoDB connection error:', error);
  process.exit(1);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
  console.log(`📱 App available at http://localhost:${PORT}`);
});
