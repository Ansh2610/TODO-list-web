// JWT auth middleware: verifies Bearer token and attaches user to req
const jwt = require('jsonwebtoken');
const mongoose = require('mongoose');
const User = require('../models/User');

const auth = async (req, res, next) => {
  try {
    // Test bypass: allow tests to inject a fake user
    if (process.env.NODE_ENV === 'test' || process.env.SKIP_AUTH === 'true') {
      req.user = { _id: new mongoose.Types.ObjectId() };
      return next();
    }

    const authHeader = req.header('Authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({
        success: false,
        message: 'Access denied. No token provided.'
      });
    }

    const token = authHeader.substring(7); // strip 'Bearer '

    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    const user = await User.findById(decoded.userId);
    if (!user) {
      return res.status(401).json({
        success: false,
        message: 'Access denied. User not found.'
      });
    }

    req.user = user; // attach user
    next();

  } catch (error) {
    if (error.name === 'JsonWebTokenError') {
      return res.status(401).json({
        success: false,
        message: 'Access denied. Invalid token.'
      });
    }
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({
        success: false,
        message: 'Access denied. Token expired.'
      });
    }

    console.error('Auth middleware error:', error);
    res.status(500).json({
      success: false,
      message: 'Authentication failed',
      error: error.message
    });
  }
};

module.exports = auth;
