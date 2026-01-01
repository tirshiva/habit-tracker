import React, { useState, useEffect, useCallback } from 'react';
import { analyticsService } from '../services/analyticsService';
// Analytics component with improved charts showing all dates
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
  Cell,
} from 'recharts';
import './Analytics.css';

const Analytics = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const loadAnalytics = useCallback(async (showRefreshing = false) => {
    try {
      if (showRefreshing) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      setError(null);
      const data = await analyticsService.getAnalytics();
      
      // Validate and ensure all required fields exist
      const validatedData = {
        total_habits: data?.total_habits ?? 0,
        active_habits: data?.active_habits ?? 0,
        total_completions: data?.total_completions ?? 0,
        completions_this_week: data?.completions_this_week ?? 0,
        completions_this_month: data?.completions_this_month ?? 0,
        overall_completion_rate: data?.overall_completion_rate ?? 0,
        streaks: Array.isArray(data?.streaks) ? data.streaks : [],
        habit_stats: Array.isArray(data?.habit_stats) ? data.habit_stats : [],
        weekly_completions: data?.weekly_completions && typeof data.weekly_completions === 'object' 
          ? data.weekly_completions 
          : {},
        monthly_completions: data?.monthly_completions && typeof data.monthly_completions === 'object'
          ? data.monthly_completions
          : {},
      };
      
      setAnalytics(validatedData);
    } catch (error) {
      console.error('Error loading analytics:', error);
      setError(error.response?.data?.detail || error.message || 'Failed to load analytics data');
      // Set empty state on error
      setAnalytics({
        total_habits: 0,
        active_habits: 0,
        total_completions: 0,
        completions_this_week: 0,
        completions_this_month: 0,
        overall_completion_rate: 0,
        streaks: [],
        habit_stats: [],
        weekly_completions: {},
        monthly_completions: {},
      });
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadAnalytics();
    
    // Refresh data when component comes into focus (user navigates back)
    const handleFocus = () => {
      loadAnalytics(true);
    };
    
    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, [loadAnalytics]);

  const handleRefresh = () => {
    loadAnalytics(true);
  };

  if (loading) {
    return (
      <div className="container">
        <div className="loading">Loading analytics...</div>
      </div>
    );
  }

  if (error && !analytics) {
    return (
      <div className="container">
        <div className="error-message">
          <p>{error}</p>
          <button onClick={handleRefresh} className="btn btn-primary">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="container">
        <div className="loading">No data available</div>
      </div>
    );
  }

  // Calculate streak summary
  const maxCurrentStreak = analytics.streaks && analytics.streaks.length > 0
    ? Math.max(...analytics.streaks.map(s => s.current_streak))
    : 0;
  const maxLongestStreak = analytics.streaks && analytics.streaks.length > 0
    ? Math.max(...analytics.streaks.map(s => s.longest_streak))
    : 0;

  // Helper function to generate all dates in a range
  const generateDateRange = (startDate, days) => {
    const dates = [];
    for (let i = days - 1; i >= 0; i--) {
      const date = new Date(startDate);
      date.setDate(date.getDate() - i);
      dates.push(date.toISOString().split('T')[0]);
    }
    return dates;
  };

  // Prepare weekly data for chart (last 7 days) - fill in all dates
  const today = new Date();
  today.setHours(0, 0, 0, 0); // Normalize to start of day
  const last7Days = generateDateRange(today, 7);
  const weeklyCompletionsMap = analytics.weekly_completions || {};
  
  // Normalize date keys in the map to YYYY-MM-DD format
  const normalizedWeeklyMap = {};
  Object.keys(weeklyCompletionsMap).forEach(key => {
    // Handle different date formats from backend
    const dateKey = key.split(' ')[0]; // Get date part if there's time
    normalizedWeeklyMap[dateKey] = weeklyCompletionsMap[key];
  });
  
  const weeklyData = last7Days.map((dateStr) => {
    const dateObj = new Date(dateStr + 'T00:00:00'); // Ensure consistent timezone
    const todayStr = today.toISOString().split('T')[0];
    
    // Try multiple date format matches
    let completions = 0;
    if (normalizedWeeklyMap[dateStr] !== undefined) {
      completions = Number(normalizedWeeklyMap[dateStr]) || 0;
    } else {
      // Try matching with different formats
      const dateVariations = [
        dateStr,
        dateObj.toISOString().split('T')[0],
        dateObj.toLocaleDateString('en-CA'), // YYYY-MM-DD format
      ];
      for (const variation of dateVariations) {
        if (normalizedWeeklyMap[variation] !== undefined) {
          completions = Number(normalizedWeeklyMap[variation]) || 0;
          break;
        }
      }
    }
    
    return {
      date: dateObj.toLocaleDateString('en-US', { weekday: 'short' }),
      fullDate: dateStr,
      completions: completions,
      hasCompletions: completions > 0,
      isToday: dateStr === todayStr,
    };
  });

  // Prepare monthly data for chart (last 30 days) - fill in all dates
  const last30Days = generateDateRange(today, 30);
  const monthlyCompletionsMap = analytics.monthly_completions || {};
  
  // Normalize date keys in the map to YYYY-MM-DD format
  const normalizedMonthlyMap = {};
  Object.keys(monthlyCompletionsMap).forEach(key => {
    // Handle different date formats from backend
    const dateKey = key.split(' ')[0]; // Get date part if there's time
    normalizedMonthlyMap[dateKey] = monthlyCompletionsMap[key];
  });
  
  const monthlyData = last30Days.map((dateStr) => {
    const dateObj = new Date(dateStr + 'T00:00:00'); // Ensure consistent timezone
    const todayStr = today.toISOString().split('T')[0];
    
    // Try multiple date format matches
    let completions = 0;
    if (normalizedMonthlyMap[dateStr] !== undefined) {
      completions = Number(normalizedMonthlyMap[dateStr]) || 0;
    } else {
      // Try matching with different formats
      const dateVariations = [
        dateStr,
        dateObj.toISOString().split('T')[0],
        dateObj.toLocaleDateString('en-CA'), // YYYY-MM-DD format
      ];
      for (const variation of dateVariations) {
        if (normalizedMonthlyMap[variation] !== undefined) {
          completions = Number(normalizedMonthlyMap[variation]) || 0;
          break;
        }
      }
    }
    
    return {
      date: dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      fullDate: dateStr,
      completions: completions,
      hasCompletions: completions > 0,
      isToday: dateStr === todayStr,
    };
  });

  // Custom tooltip for charts
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const completions = payload[0].value;
      const isCompleted = completions > 0;
      
      return (
        <div className="chart-tooltip">
          <p className="tooltip-label">{label}</p>
          <p className="tooltip-value">
            <span className="tooltip-dot" style={{ backgroundColor: isCompleted ? '#10b981' : '#e5e7eb' }}></span>
            {completions} {completions === 1 ? 'completion' : 'completions'}
          </p>
          {data.isToday && (
            <p className="tooltip-note">✨ Today</p>
          )}
          {!isCompleted && (
            <p className="tooltip-note">💪 Keep going!</p>
          )}
        </div>
      );
    }
    return null;
  };

  // Color for bars based on completion count - more motivating colors
  const getBarColor = (entry) => {
    if (entry.completions === 0) return '#e5e7eb'; // Light gray for no completions
    if (entry.isToday && entry.completions > 0) return '#10b981'; // Green for today's completions
    if (entry.completions >= 5) return '#059669'; // Dark green for high activity
    if (entry.completions >= 3) return '#3b82f6'; // Blue for good activity
    return '#60a5fa'; // Light blue for some activity
  };

  // Calculate streak in the data for visual indicators
  const calculateStreakInData = (data) => {
    let currentStreak = 0;
    let maxStreak = 0;
    let tempStreak = 0;
    
    for (let i = data.length - 1; i >= 0; i--) {
      if (data[i].hasCompletions) {
        tempStreak++;
        currentStreak = tempStreak;
        maxStreak = Math.max(maxStreak, tempStreak);
      } else {
        tempStreak = 0;
      }
    }
    
    return { currentStreak, maxStreak };
  };

  const weeklyStreak = calculateStreakInData(weeklyData);
  const monthlyStreak = calculateStreakInData(monthlyData);

  return (
    <div className="container">
      <div className="page-header">
        <h1 className="page-title">Analytics</h1>
        <button 
          onClick={handleRefresh} 
          className="btn btn-secondary refresh-btn"
          disabled={refreshing}
        >
          {refreshing ? 'Refreshing...' : '🔄 Refresh'}
        </button>
      </div>

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

      {/* Streak Summary Cards */}
      {analytics.streaks && analytics.streaks.length > 0 ? (
        <div className="streak-summary-grid">
          <div className="streak-summary-card highlight">
            <div className="streak-summary-icon">🔥</div>
            <div className="streak-summary-content">
              <div className="streak-summary-value">{maxCurrentStreak}</div>
              <div className="streak-summary-label">Current Best Streak</div>
            </div>
          </div>
          <div className="streak-summary-card">
            <div className="streak-summary-icon">⭐</div>
            <div className="streak-summary-content">
              <div className="streak-summary-value">{maxLongestStreak}</div>
              <div className="streak-summary-label">All-Time Best Streak</div>
            </div>
          </div>
        </div>
      ) : (
        <div className="card">
          <p className="empty-state-message">No streaks yet. Start completing habits to build your streaks!</p>
        </div>
      )}

      {/* Individual Streaks */}
      {analytics.streaks && analytics.streaks.length > 0 ? (
        <div className="card">
          <h2 className="card-title">Streak Details</h2>
          <div className="streaks-grid">
            {analytics.streaks.map((streak) => {
              const progress = streak.longest_streak > 0 
                ? (streak.current_streak / streak.longest_streak) * 100 
                : 0;
              return (
                <div key={streak.habit_id} className="streak-card">
                  <div className="streak-habit-name">{streak.habit_name}</div>
                  <div className="streak-values">
                    <div className="streak-current-section">
                      <div className="streak-label">Current</div>
                      <div className="streak-current">{streak.current_streak} days</div>
                    </div>
                    <div className="streak-longest-section">
                      <div className="streak-label">Best</div>
                      <div className="streak-longest">{streak.longest_streak} days</div>
                    </div>
                  </div>
                  {streak.longest_streak > 0 && (
                    <div className="streak-progress">
                      <div className="streak-progress-bar">
                        <div 
                          className="streak-progress-fill" 
                          style={{ width: `${Math.min(progress, 100)}%` }}
                        ></div>
                      </div>
                      <div className="streak-progress-text">
                        {progress.toFixed(0)}% of best
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      ) : null}

      {/* Weekly Completions Chart */}
      <div className="card">
        <div className="chart-header">
          <div>
            <h2 className="card-title">Weekly Activity (Last 7 Days)</h2>
            {weeklyStreak.currentStreak > 0 && (
              <p className="streak-indicator">
                🔥 {weeklyStreak.currentStreak} day streak!
              </p>
            )}
          </div>
          <div className="chart-stats">
            <div className="chart-stat-item">
              <span className="chart-stat-value">{weeklyData.filter(d => d.hasCompletions).length}</span>
              <span className="chart-stat-label">Active Days</span>
            </div>
            <div className="chart-stat-item">
              <span className="chart-stat-value">{weeklyData.reduce((sum, d) => sum + d.completions, 0)}</span>
              <span className="chart-stat-label">Total Completions</span>
            </div>
          </div>
        </div>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={weeklyData} margin={{ top: 20, right: 10, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis 
                dataKey="date" 
                tick={{ fill: '#6b7280', fontSize: 12, fontWeight: 500 }}
                stroke="#d1d5db"
              />
              <YAxis 
                tick={{ fill: '#6b7280', fontSize: 12 }}
                stroke="#d1d5db"
                domain={[0, Math.max(1, Math.max(...weeklyData.map(d => d.completions)) + 1)]}
                allowDecimals={false}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar 
                dataKey="completions" 
                radius={[8, 8, 0, 0]} 
                strokeWidth={2}
                minPointSize={3}
              >
                {weeklyData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={getBarColor(entry)}
                    stroke={entry.isToday ? '#059669' : (entry.completions === 0 ? '#d1d5db' : 'none')}
                    strokeWidth={entry.isToday ? 3 : (entry.completions === 0 ? 1 : 0)}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="chart-legend">
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: '#10b981' }}></div>
            <span>Today</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: '#3b82f6' }}></div>
            <span>Completed</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: '#e5e7eb' }}></div>
            <span>Missed</span>
          </div>
        </div>
      </div>

      {/* Monthly Completions Chart */}
      <div className="card">
        <div className="chart-header">
          <div>
            <h2 className="card-title">Monthly Activity (Last 30 Days)</h2>
            {monthlyStreak.currentStreak > 0 && (
              <p className="streak-indicator">
                🔥 {monthlyStreak.currentStreak} day streak! {monthlyStreak.maxStreak > monthlyStreak.currentStreak && `(Best: ${monthlyStreak.maxStreak} days)`}
              </p>
            )}
          </div>
          <div className="chart-stats">
            <div className="chart-stat-item">
              <span className="chart-stat-value">{monthlyData.filter(d => d.hasCompletions).length}</span>
              <span className="chart-stat-label">Active Days</span>
            </div>
            <div className="chart-stat-item">
              <span className="chart-stat-value">{monthlyData.reduce((sum, d) => sum + d.completions, 0)}</span>
              <span className="chart-stat-label">Total Completions</span>
            </div>
            <div className="chart-stat-item">
              <span className="chart-stat-value">{Math.round((monthlyData.filter(d => d.hasCompletions).length / monthlyData.length) * 100)}%</span>
              <span className="chart-stat-label">Consistency</span>
            </div>
          </div>
        </div>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={monthlyData} margin={{ top: 20, right: 10, left: 0, bottom: 80 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis 
                dataKey="date" 
                tick={{ fill: '#6b7280', fontSize: 10 }}
                stroke="#d1d5db"
                angle={-45}
                textAnchor="end"
                height={80}
                interval={2}
              />
              <YAxis 
                tick={{ fill: '#6b7280', fontSize: 12 }}
                stroke="#d1d5db"
                domain={[0, Math.max(1, Math.max(...monthlyData.map(d => d.completions)) + 1)]}
                allowDecimals={false}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar 
                dataKey="completions" 
                radius={[4, 4, 0, 0]} 
                strokeWidth={1}
                minPointSize={2}
              >
                {monthlyData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={getBarColor(entry)}
                    stroke={entry.isToday ? '#059669' : (entry.completions === 0 ? '#d1d5db' : 'none')}
                    strokeWidth={entry.isToday ? 2 : (entry.completions === 0 ? 1 : 0)}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="chart-legend">
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: '#10b981' }}></div>
            <span>Today</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: '#3b82f6' }}></div>
            <span>Completed</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: '#e5e7eb' }}></div>
            <span>Missed</span>
          </div>
        </div>
      </div>

      {/* Habit Performance Table */}
      {analytics.habit_stats && analytics.habit_stats.length > 0 ? (
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
                  <tr key={stat.habit_id || `habit-${stat.habit_name}`}>
                    <td className="table-habit-name">{stat.habit_name || 'Unknown Habit'}</td>
                    <td>{stat.total_completions ?? 0}</td>
                    <td>
                      <span className="streak-badge current">{stat.current_streak ?? 0} days</span>
                    </td>
                    <td>
                      <span className="streak-badge longest">{stat.longest_streak ?? 0} days</span>
                    </td>
                    <td>
                      <div className="completion-rate-cell">
                        <span>{(stat.completion_rate ?? 0).toFixed(1)}%</span>
                        <div className="completion-rate-bar">
                          <div 
                            className="completion-rate-fill" 
                            style={{ width: `${Math.min(stat.completion_rate ?? 0, 100)}%` }}
                          ></div>
                        </div>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="card">
          <h2 className="card-title">Habit Performance</h2>
          <p className="empty-state-message">No habit statistics available yet. Create and complete habits to see your performance!</p>
        </div>
      )}
    </div>
  );
};

export default Analytics;

