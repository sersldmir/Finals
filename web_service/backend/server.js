import express, { json, urlencoded } from 'express';
import cors from 'cors';
import { config } from 'dotenv';

config();

import apiRoutes from './routes/api.js';

const app = express();

app.use(cors());
app.use(json());
app.use(urlencoded({ extended: true }));

app.use('/api', apiRoutes);


app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({
    success: false,
    message: 'Internal server error',
    error: process.env.NODE_ENV === 'development' ? err.message : undefined
  });
});

const HOST = process.env.HOST || '0.0.0.0';
const PORT = process.env.PORT || 5000;
app.listen(PORT, HOST, () => {
  console.log(`Server running at host ${HOST} on port ${PORT}`);
});

export default app;