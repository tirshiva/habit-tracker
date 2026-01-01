import React, { useState, useEffect } from 'react';
import { habitService } from '../services/habitService';
import './Habits.css';

const Habits = () => {
  const [habits, setHabits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingHabit, setEditingHabit] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    frequency: 'daily',  // Backend expects lowercase
    color: '#3B82F6',
    reminder_time: '',
  });

  useEffect(() => {
    loadHabits();
  }, []);

  const loadHabits = async () => {
    try {
      const data = await habitService.getAll();
      setHabits(data);
    } catch (error) {
      console.error('Error loading habits:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingHabit) {
        await habitService.update(editingHabit.id, formData);
      } else {
        await habitService.create(formData);
      }
      setShowForm(false);
      setEditingHabit(null);
      setFormData({
        name: '',
        description: '',
        frequency: 'daily',  // Backend expects lowercase
        color: '#3B82F6',
        reminder_time: '',
      });
      loadHabits();
    } catch (error) {
      console.error('Error saving habit:', error);
      const errorMessage = error.response?.data?.detail || 
                          (Array.isArray(error.response?.data) ? error.response.data.map(e => e.msg).join(', ') : null) ||
                          error.message || 
                          'Failed to save habit';
      alert(`Failed to save habit: ${errorMessage}`);
    }
  };

  const handleEdit = (habit) => {
    setEditingHabit(habit);
    setFormData({
      name: habit.name,
      description: habit.description || '',
      frequency: habit.frequency,
      color: habit.color,
      reminder_time: habit.reminder_time || '',
    });
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this habit?')) {
      try {
        await habitService.delete(id);
        loadHabits();
      } catch (error) {
        console.error('Error deleting habit:', error);
        alert('Failed to delete habit');
      }
    }
  };

  const handleToggleActive = async (habit) => {
    try {
      await habitService.update(habit.id, { is_active: !habit.is_active });
      loadHabits();
    } catch (error) {
      console.error('Error updating habit:', error);
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="container">
      <div className="page-header">
        <h1 className="page-title">My Habits</h1>
        <button
          onClick={() => {
            setShowForm(!showForm);
            setEditingHabit(null);
            setFormData({
              name: '',
              description: '',
              frequency: 'daily',  // Backend expects lowercase
              color: '#3B82F6',
              reminder_time: '',
            });
          }}
          className="btn btn-primary"
        >
          {showForm ? 'Cancel' : '+ New Habit'}
        </button>
      </div>

      {showForm && (
        <div className="card">
          <h2 className="card-title">
            {editingHabit ? 'Edit Habit' : 'Create New Habit'}
          </h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Name *</label>
              <input
                type="text"
                name="name"
                className="form-input"
                value={formData.name}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Description</label>
              <textarea
                name="description"
                className="form-input"
                value={formData.description}
                onChange={handleChange}
                rows="3"
              />
            </div>

            <div className="form-group">
              <label className="form-label">Frequency</label>
              <select
                name="frequency"
                className="form-input"
                value={formData.frequency}
                onChange={handleChange}
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="custom">Custom</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Color</label>
              <input
                type="color"
                name="color"
                className="form-input"
                value={formData.color}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Reminder Time (HH:MM)</label>
              <input
                type="time"
                name="reminder_time"
                className="form-input"
                value={formData.reminder_time}
                onChange={handleChange}
              />
            </div>

            <button type="submit" className="btn btn-primary">
              {editingHabit ? 'Update' : 'Create'}
            </button>
          </form>
        </div>
      )}

      <div className="habits-grid">
        {habits.map((habit) => (
          <div key={habit.id} className={`habit-card ${!habit.is_active ? 'inactive' : ''}`}>
            <div className="habit-card-header">
              <div
                className="habit-color-indicator"
                style={{ backgroundColor: habit.color }}
              ></div>
              <div className="habit-card-title">
                <h3>{habit.name}</h3>
                <span className="habit-frequency">{habit.frequency}</span>
              </div>
            </div>
            {habit.description && (
              <p className="habit-card-description">{habit.description}</p>
            )}
            {habit.reminder_time && (
              <p className="habit-reminder">Reminder: {habit.reminder_time}</p>
            )}
            <div className="habit-card-actions">
              <button
                onClick={() => handleToggleActive(habit)}
                className={`btn ${habit.is_active ? 'btn-secondary' : 'btn-primary'}`}
              >
                {habit.is_active ? 'Deactivate' : 'Activate'}
              </button>
              <button
                onClick={() => handleEdit(habit)}
                className="btn btn-secondary"
              >
                Edit
              </button>
              <button
                onClick={() => handleDelete(habit.id)}
                className="btn btn-danger"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>

      {habits.length === 0 && (
        <div className="card">
          <p className="empty-state">
            No habits yet. Create your first habit to get started!
          </p>
        </div>
      )}
    </div>
  );
};

export default Habits;

