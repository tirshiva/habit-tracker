import React, { useState, useEffect } from 'react';
import { habitService } from '../services/habitService';
import { completionService } from '../services/completionService';
import { analyticsService } from '../services/analyticsService';
import { format } from 'date-fns';
import './Dashboard.css';

const Dashboard = () => {
  const [habits, setHabits] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState(format(new Date(), 'yyyy-MM-dd'));

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [habitsData, analyticsData] = await Promise.all([
        habitService.getAll(),
        analyticsService.getAnalytics(),
      ]);
      setHabits(habitsData.filter(h => h.is_active));
      setAnalytics(analyticsData);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleComplete = async (habitId) => {
    try {
      await completionService.create({
        habit_id: habitId,
        completion_date: selectedDate,
      });
      loadData();
    } catch (error) {
      console.error('Error completing habit:', error);
      alert('Failed to mark habit as complete');
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="container">
      <h1 className="page-title">Dashboard</h1>
      
      {analytics && (
        <div className="stats-grid">
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
      )}

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Today's Habits</h2>
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="date-input"
          />
        </div>
        
        {habits.length === 0 ? (
          <p className="empty-state">No active habits. <a href="/habits">Create one</a> to get started!</p>
        ) : (
          <div className="habits-list">
            {habits.map((habit) => (
              <div key={habit.id} className="habit-item">
                <div className="habit-info">
                  <div
                    className="habit-color"
                    style={{ backgroundColor: habit.color }}
                  ></div>
                  <div>
                    <h3 className="habit-name">{habit.name}</h3>
                    {habit.description && (
                      <p className="habit-description">{habit.description}</p>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => handleComplete(habit.id)}
                  className="btn btn-primary"
                >
                  Mark Complete
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {analytics && analytics.streaks && analytics.streaks.length > 0 && (
        <div className="card">
          <h2 className="card-title">Current Streaks</h2>
          <div className="streaks-list">
            {analytics.streaks.map((streak) => (
              <div key={streak.habit_id} className="streak-item">
                <div className="streak-habit">{streak.habit_name}</div>
                <div className="streak-value">{streak.current_streak} days</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;

