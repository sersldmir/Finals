import { query } from '../config/db.js';
import { genSalt, hash } from 'bcrypt';
import { createHash } from 'crypto';


export async function createUser(req, res) {
  try {
    const { username, password } = req.body;
    
    if (!username || !password) {
      return res.status(400).json({ message: 'Username and password are required' });
    }
    
    const userCheck = await query('SELECT * FROM users WHERE username = $1', [username]);
    if (userCheck.rows.length > 0) {
      return res.status(400).json({ message: 'Username already exists' });
    }
    
    const salt = await genSalt(10);
    const hashedPassword = await hash(password, salt);
    
    const token = createHash('sha256')
      .update(`${username}${password}${Date.now()}`)
      .digest('hex');
    
    const newUser = await query(
      'INSERT INTO users (username, password, token) VALUES ($1, $2, $3) RETURNING id, username, token',
      [username, hashedPassword, token]
    );
    
    await query(
      'INSERT INTO statistics (user_id, queries_made, queries_succeeded, queries_failed) VALUES ($1, 0, 0, 0)',
      [newUser.rows[0].id]
    );
    
    res.status(201).json({
      id: newUser.rows[0].id,
      username: newUser.rows[0].username,
      token: newUser.rows[0].token
    });
  } catch (error) {
    console.error('Error creating user:', error);
    res.status(500).json({ message : 'Server error' });
    }
};


export async function deleteUser(req, res) {
    try {
      const { id } = req.params;
      
      const deletedUser = await query('DELETE FROM users WHERE id = $1 RETURNING id', [id]);
      
      if (deletedUser.rows.length === 0) {
        return res.status(404).json({ message: 'User not found' });
      }
      
      res.json({ message: 'User deleted successfully' });
    } catch (error) {
      console.error('Error deleting user:', error);
      res.status(500).json({ message: 'Server error' });
    }
};

export async function listAllUsers(req, res) {
    try {
      const users = await query('SELECT id, username, token FROM users ORDER BY created_at DESC');
      res.json(users.rows);
    } catch (error) {
      console.error('Error listing users:', error);
      res.status(500).json({ message: 'Server error' });
    }
};

export async function getUser(req, res) {
    try {
      const { id } = req.params;
      
      const user = await query('SELECT id, username, token FROM users WHERE id = $1', [id]);
      
      if (user.rows.length === 0) {
        return res.status(404).json({ message: 'User not found' });
      }
      
      res.json(user.rows[0]);
    } catch (error) {
      console.error('Error getting user:', error);
      res.status(500).json({ message: 'Server error' });
    }
};


export async function getStatsForUser(req, res) {
    try {
      const { id } = req.params;
      
      const stats = await query('SELECT * FROM statistics WHERE user_id = $1', [id]);
      
      if (stats.rows.length === 0) {
        return res.status(404).json({ message: 'Statistics not found for this user' });
      }
      
      res.json(stats.rows[0]);
    } catch (error) {
      console.error('Error getting user statistics:', error);
      res.status(500).json({ message: 'Server error' });
    }
};

export async function getStatsForAll (req, res) {
    try {
      const stats = await query(`
        SELECT 
          u.id,
          u.username,
          s.queries_made,
          s.queries_succeeded,
          s.queries_failed
        FROM 
          users u
        LEFT JOIN 
          statistics s ON u.id = s.user_id
        ORDER BY 
          u.username
      `);
      
      const totalStats = stats.rows.reduce(
        (acc, curr) => {
          acc.queries_made += Number(curr.queries_made || 0);
          acc.queries_succeeded += Number(curr.queries_succeeded || 0);
          acc.queries_failed += Number(curr.queries_failed || 0);
          return acc;
        },
        { queries_made: 0, queries_succeeded: 0, queries_failed: 0 }
      );
      
      res.json({ 
        users: stats.rows,
        totals: totalStats
      });
    } catch (error) {
      console.error('Error getting all statistics:', error);
      res.status(500).json({ message: 'Server error' });
    }
};
