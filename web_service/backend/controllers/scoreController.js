import { query } from '../config/db.js';

export async function getScore(req, res) {
  try {
    const { token, client_id } = req.query;
    
    if (!token || !client_id) {
      return res.status(400).json({ message: 'Token and client_id are required' });
    }
    
    const userQuery = await query('SELECT id FROM users WHERE token = $1', [token]);
    
    if (userQuery.rows.length === 0) {
      return res.status(401).json({ message: 'Invalid token' });
    }
    
    const userId = userQuery.rows[0].id;
    
    await query(
      'UPDATE statistics SET queries_made = queries_made + 1 WHERE user_id = $1',
      [userId]
    );
    
    const scoreQuery = await query(
      'SELECT score FROM scores_service WHERE id = $1',
      [client_id]
    );
    
    if (scoreQuery.rows.length === 0) {

      await query(
            'UPDATE statistics SET queries_failed = queries_failed + 1 WHERE user_id = $1',
            [userId]
        );

      return res.status(404).json({ message: 'Client ID not found' });
    }

    await query(
        'UPDATE statistics SET queries_succeeded = queries_succeeded + 1 WHERE user_id = $1',
        [userId]
      );
      
      res.json({
        client_id,
        score: scoreQuery.rows[0].score
      });
    } catch (error) {
      console.error('Error getting score:', error);
      res.status(500).json({ message: 'Server error' });
    }
}