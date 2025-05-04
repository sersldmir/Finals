import { Router } from 'express';
const router = Router();
import { validateToken } from '../middleware/auth.js';
import { createUser, deleteUser, listAllUsers, getUser, getStatsForUser, getStatsForAll} from '../controllers/userController.js';
import { getScore } from '../controllers/scoreController.js';

router.post('/createUser', createUser);
router.delete('/deleteUser/:id', deleteUser);
router.get('/listAllUsers', listAllUsers);
router.get('/getUser/:id', getUser);
router.get('/getStatsForUser/:id', getStatsForUser);
router.get('/getStatsForAll', getStatsForAll);

router.get('/getScore', validateToken, getScore);

export default router;
