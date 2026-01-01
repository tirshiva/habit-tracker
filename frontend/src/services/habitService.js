import api from './api';

export const habitService = {
  getAll: async () => {
    const response = await api.get('/habits');
    return response.data;
  },

  getById: async (id) => {
    const response = await api.get(`/habits/${id}`);
    return response.data;
  },

  create: async (habitData) => {
    const response = await api.post('/habits', habitData);
    return response.data;
  },

  update: async (id, habitData) => {
    const response = await api.put(`/habits/${id}`, habitData);
    return response.data;
  },

  delete: async (id) => {
    await api.delete(`/habits/${id}`);
  },
};

