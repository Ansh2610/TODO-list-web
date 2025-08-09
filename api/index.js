// Vercel serverless entrypoint wrapping the Express app
const serverless = require('serverless-http');
const mongoose = require('mongoose');
const { app } = require('../server/app');

let cached = global.__MONGO_CONN__;

async function ensureDb() {
  if (cached) return;
  await mongoose.connect(process.env.MONGODB_URI);
  cached = global.__MONGO_CONN__ = mongoose.connection.readyState === 1;
}

module.exports = async (req, res) => {
  await ensureDb();
  const handler = serverless(app);
  return handler(req, res);
};
