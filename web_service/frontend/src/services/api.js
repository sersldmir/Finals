import axios from 'axios';

const API_URL = process.env.REACT_APP_API_HOST || 'http://localhost:5000/api';


const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

export const listAllUsers = async () => {
  try {
    const response = await apiClient.get('/listAllUsers');
    return response.data;
  } catch (error) {
    console.error('Error fetching users:', error);
    throw error;
  }
};

export const getUser = async (id) => {
  try {
    const response = await apiClient.get(`/getUser/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching user ${id}:`, error);
    throw error;
  }
};

export const deleteUser = async (id) => {
  try {
    const response = await apiClient.delete(`/deleteUser/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error deleting user ${id}:`, error);
    throw error;
  }
};

export const createUser = async (userData) => {
  try {
    const response = await apiClient.post('/createUser', userData);
    return response.data;
  } catch (error) {
    console.error('Error creating user:', error);
    throw error;
  }
};

export const getStatsForUser = async (id) => {
  try {
    const response = await apiClient.get(`/getStatsForUser/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching stats for user ${id}:`, error);
    throw error;
  }
};

export const getStatsForAll = async () => {
  try {
    const response = await apiClient.get('/getStatsForAll');
    return response.data;
  } catch (error) {
    console.error('Error fetching all stats:', error);
    throw error;
  }
};

export const getScore = async (token, clientId) => {
  try {
    const response = await apiClient.get('/getScore', {
      params: { client_id: clientId, token: token },
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  } catch (error) {
    console.error(`Error fetching score for client ${clientId}:`, error);
    throw error;
  }
};


export default {
  listAllUsers,
  getUser,
  deleteUser,
  createUser,
  getStatsForUser,
  getStatsForAll,
  getScore
};