import { query } from '../config/db.js';

export const validateToken = async (req, res, next) => {
  try {
    const token = req.headers.authorization?.split(' ')[1] || req.query.token;
    
    if (!token) {
      return res.status(401).json({ 
        success: false, 
        message: 'Access denied. No token provided.' 
      });
    }

    const userResult = await query(
      'SELECT id, username FROM users WHERE token = $1',
      [token]
    );

    if (userResult.rows.length === 0) {
      return res.status(401).json({ 
        success: false, 
        message: 'Invalid token.' 
      });
    }

    // Attach user info to request
    req.user = userResult.rows[0];
    next();
  } catch (error) {
    console.error('Authentication error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Internal server error during authentication.'
    });
  }
};

export default {
  validateToken,
};