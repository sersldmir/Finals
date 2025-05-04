import { Pool } from 'pg';

const pool = new Pool({
  user: process.env.DB_USER || 'postgres_dev',
  host: process.env.DB_HOST || 'localhost',
  database: process.env.DB_NAME || 'scoring',
  password: process.env.DB_PASSWORD || '',
  port: process.env.DB_PORT || 5432,
});

export function query(text, params) { return pool.query(text, params); }