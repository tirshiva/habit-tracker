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
  const [completingHabitId, setCompletingHabitId] = useState(null);
  const [completedHabits, setCompletedHabits] = useState(new Set());

  useEffect(() => {
    loadData();
  }, [selectedDate]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [habitsData, analyticsData] = await Promise.all([
        habitService.getAll(),
        analyticsService.getAnalytics(),
      ]);
      const activeHabits = habitsData.filter(h => h.is_active);
      setHabits(activeHabits);
      setAnalytics(analyticsData);
      
      // Load completions for the selected date to show which habits are completed
      const completionsPromises = activeHabits.map(async (habit) => {
        try {
          const completions = await completionService.getByHabit(habit.id, selectedDate, selectedDate);
          return { habitId: habit.id, completions };
        } catch (error) {
          console.error(`Error loading completions for habit ${habit.id}:`, error);
          return { habitId: habit.id, completions: [] };
        }
      });
      
      const completionsResults = await Promise.all(completionsPromises);
      const completedSet = new Set();
      completionsResults.forEach(({ habitId, completions }) => {
        const hasCompletion = completions.some(c => {
          const completionDate = typeof c.completion_date === 'string' 
            ? c.completion_date.split('T')[0]
            : c.completion_date;
          return completionDate === selectedDate;
        });
        if (hasCompletion) {
          completedSet.add(habitId);
        }
      });
      setCompletedHabits(completedSet);
    } catch (error) {
      console.error('Error loading data:', error);
      // Set empty state on error instead of leaving loading state
      setHabits([]);
      setAnalytics(null);
    } finally {
      setLoading(false);
    }
  };

  const handleComplete = async (habitId) => {
    if (completingHabitId) {
      return; // Prevent multiple clicks
    }
    
    setCompletingHabitId(habitId);
    try {
      console.log('Marking habit complete:', habitId, 'for date:', selectedDate);
      
      // Check if completion already exists by getting completions for this habit and date
      const completions = await completionService.getByHabit(habitId, selectedDate, selectedDate);
      console.log('Existing completions:', completions);
      
      // Compare dates (completion_date might be in ISO format or just the date string)
      const existingCompletion = completions.find(c => {
        const completionDate = typeof c.completion_date === 'string' 
          ? c.completion_date.split('T')[0]  // Handle ISO datetime format
          : c.completion_date;
        return completionDate === selectedDate;
      });
      
      if (existingCompletion) {
        // Toggle: Delete if exists
        console.log('Deleting existing completion:', existingCompletion.id);
        await completionService.delete(existingCompletion.id);
        setCompletedHabits(prev => {
          const newSet = new Set(prev);
          newSet.delete(habitId);
          return newSet;
        });
      } else {
        // Create new completion
        console.log('Creating new completion');
        await completionService.create({
          habit_id: habitId,
          completion_date: selectedDate,
        });
        setCompletedHabits(prev => {
          const newSet = new Set(prev);
          newSet.add(habitId);
          return newSet;
        });
      }
      
      // Reload analytics to reflect changes
      try {
        const analyticsData = await analyticsService.getAnalytics();
        setAnalytics(analyticsData);
      } catch (error) {
        console.error('Error reloading analytics:', error);
      }
      
      console.log('Completion updated successfully');
    } catch (error) {
      console.error('Error completing habit:', error);
      // If error is "already exists", try to delete it
      if (error.response?.data?.detail?.includes('already exists')) {
        try {
          // Get the existing completion and delete it
          const completions = await completionService.getByHabit(habitId, selectedDate, selectedDate);
          const existingCompletion = completions.find(c => {
            const completionDate = typeof c.completion_date === 'string' 
              ? c.completion_date.split('T')[0]
              : c.completion_date;
            return completionDate === selectedDate;
          });
          if (existingCompletion) {
            await completionService.delete(existingCompletion.id);
            await loadData();
            return;
          }
        } catch (deleteError) {
          console.error('Error deleting completion:', deleteError);
        }
      }
      const errorMessage = error.response?.data?.detail || 
                          error.message || 
                          'Failed to mark habit as complete';
      alert(errorMessage);
    } finally {
      setCompletingHabitId(null);
    }
  };

  if (loading) {
    return (
      <div className="container">
        <div className="loading">Loading...</div>
      </div>
    );
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
                  className={`btn ${completedHabits.has(habit.id) ? 'btn-secondary' : 'btn-primary'}`}
                  disabled={completingHabitId === habit.id}
                >
                  {completingHabitId === habit.id 
                    ? 'Processing...' 
                    : completedHabits.has(habit.id) 
                      ? 'Mark Incomplete' 
                      : 'Mark Complete'}
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

