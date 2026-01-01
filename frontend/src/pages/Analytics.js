import React, { useState, useEffect } from 'react';
import { analyticsService } from '../services/analyticsService';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import './Analytics.css';

const Analytics = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      const data = await analyticsService.getAnalytics();
      setAnalytics(data);
    } catch (error) {
      console.error('Error loading analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (!analytics) {
    return <div className="loading">No data available</div>;
  }

  // Prepare weekly data for chart
  const weeklyData = Object.entries(analytics.weekly_completions || {})
    .map(([date, count]) => ({
      date: new Date(date).toLocaleDateString('en-US', { weekday: 'short' }),
      completions: count,
    }));

  // Prepare monthly data for chart
  const monthlyData = Object.entries(analytics.monthly_completions || {})
    .map(([date, count]) => ({
      date: new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      completions: count,
    }))
    .slice(-30); // Last 30 days

  return (
    <div className="container">
      <h1 className="page-title">Analytics</h1>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{analytics.total_habits}</div>
          <div className="stat-label">Total Habits</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{analytics.active_habits}</div>
          <div className="stat-label">Active Habits</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{analytics.completions_this_week}</div>
          <div className="stat-label">This Week</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{analytics.completions_this_month}</div>
          <div className="stat-label">This Month</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{analytics.overall_completion_rate.toFixed(1)}%</div>
          <div className="stat-label">Completion Rate</div>
        </div>
      </div>

      {analytics.streaks && analytics.streaks.length > 0 && (
        <div className="card">
          <h2 className="card-title">Current Streaks</h2>
          <div className="streaks-grid">
            {analytics.streaks.map((streak) => (
              <div key={streak.habit_id} className="streak-card">
                <div className="streak-habit-name">{streak.habit_name}</div>
                <div className="streak-current">{streak.current_streak} days</div>
                <div className="streak-longest">Best: {streak.longest_streak} days</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {weeklyData.length > 0 && (
        <div className="card">
          <h2 className="card-title">Weekly Completions</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={weeklyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="completions" stroke="#3B82F6" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {monthlyData.length > 0 && (
        <div className="card">
          <h2 className="card-title">Monthly Completions (Last 30 Days)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={monthlyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="completions" fill="#3B82F6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {analytics.habit_stats && analytics.habit_stats.length > 0 && (
        <div className="card">
          <h2 className="card-title">Habit Performance</h2>
          <div className="table-container">
            <table className="stats-table">
              <thead>
                <tr>
                  <th>Habit</th>
                  <th>Total Completions</th>
                  <th>Current Streak</th>
                  <th>Longest Streak</th>
                  <th>Completion Rate</th>
                </tr>
              </thead>
              <tbody>
                {analytics.habit_stats.map((stat) => (
                  <tr key={stat.habit_id}>
                    <td>{stat.habit_name}</td>
                    <td>{stat.total_completions}</td>
                    <td>{stat.current_streak} days</td>
                    <td>{stat.longest_streak} days</td>
                    <td>{stat.completion_rate.toFixed(1)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default Analytics;

