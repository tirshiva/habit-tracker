import api from './api';

export const completionService = {
  create: async (completionData) => {
    const response = await api.post('/completions', completionData);
    return response.data;
  },

  getByHabit: async (habitId, startDate, endDate) => {
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    
    const response = await api.get(`/completions/habit/${habitId}`, { params });
    return response.data;
  },

  update: async (id, completionData) => {
    const response = await api.put(`/completions/${id}`, completionData);
    return response.data;
  },

  delete: async (id) => {
    await api.delete(`/completions/${id}`);
  },
};

