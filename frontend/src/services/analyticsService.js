import api from './api';

export const analyticsService = {
  getAnalytics: async () => {
    const response = await api.get('/analytics');
    return response.data;
  },

  getStreaks: async () => {
    const response = await api.get('/analytics/streaks');
    return response.data;
  },
};

