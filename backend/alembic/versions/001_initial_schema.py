"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    # Create habits table
    op.create_table(
        'habits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('frequency', sa.Enum('DAILY', 'WEEKLY', 'CUSTOM', name='habitfrequency'), nullable=True),
        sa.Column('target_days', sa.String(), nullable=True),
        sa.Column('color', sa.String(), nullable=True),
        sa.Column('icon', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('reminder_time', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_habits_id'), 'habits', ['id'], unique=False)
    op.create_index(op.f('ix_habits_user_id'), 'habits', ['user_id'], unique=False)
    
    # Create habit_completions table
    op.create_table(
        'habit_completions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('habit_id', sa.Integer(), nullable=False),
        sa.Column('completion_date', sa.Date(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['habit_id'], ['habits.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'habit_id', 'completion_date', name='uq_user_habit_date')
    )
    op.create_index(op.f('ix_habit_completions_id'), 'habit_completions', ['id'], unique=False)
    op.create_index(op.f('ix_habit_completions_user_id'), 'habit_completions', ['user_id'], unique=False)
    op.create_index(op.f('ix_habit_completions_habit_id'), 'habit_completions', ['habit_id'], unique=False)
    op.create_index(op.f('ix_habit_completions_completion_date'), 'habit_completions', ['completion_date'], unique=False)
    
    # Create user_preferences table
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('timezone', sa.String(), nullable=True),
        sa.Column('language', sa.String(), nullable=True),
        sa.Column('theme', sa.String(), nullable=True),
        sa.Column('email_notifications', sa.Boolean(), nullable=True),
        sa.Column('push_notifications', sa.Boolean(), nullable=True),
        sa.Column('reminder_enabled', sa.Boolean(), nullable=True),
        sa.Column('weekly_report', sa.Boolean(), nullable=True),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_user_preferences_id'), 'user_preferences', ['id'], unique=False)
    op.create_index(op.f('ix_user_preferences_user_id'), 'user_preferences', ['user_id'], unique=True)
    
    # Create streaks table
    op.create_table(
        'streaks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('habit_id', sa.Integer(), nullable=False),
        sa.Column('current_streak', sa.Integer(), nullable=True),
        sa.Column('longest_streak', sa.Integer(), nullable=True),
        sa.Column('last_completion_date', sa.Date(), nullable=True),
        sa.Column('streak_start_date', sa.Date(), nullable=True),
        sa.Column('last_calculated_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['habit_id'], ['habits.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'habit_id', name='uq_user_habit_streak')
    )
    op.create_index(op.f('ix_streaks_id'), 'streaks', ['id'], unique=False)
    op.create_index(op.f('ix_streaks_user_id'), 'streaks', ['user_id'], unique=False)
    op.create_index(op.f('ix_streaks_habit_id'), 'streaks', ['habit_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_streaks_habit_id'), table_name='streaks')
    op.drop_index(op.f('ix_streaks_user_id'), table_name='streaks')
    op.drop_index(op.f('ix_streaks_id'), table_name='streaks')
    op.drop_table('streaks')
    op.drop_index(op.f('ix_user_preferences_user_id'), table_name='user_preferences')
    op.drop_index(op.f('ix_user_preferences_id'), table_name='user_preferences')
    op.drop_table('user_preferences')
    op.drop_index(op.f('ix_habit_completions_completion_date'), table_name='habit_completions')
    op.drop_index(op.f('ix_habit_completions_habit_id'), table_name='habit_completions')
    op.drop_index(op.f('ix_habit_completions_user_id'), table_name='habit_completions')
    op.drop_index(op.f('ix_habit_completions_id'), table_name='habit_completions')
    op.drop_table('habit_completions')
    op.drop_index(op.f('ix_habits_user_id'), table_name='habits')
    op.drop_index(op.f('ix_habits_id'), table_name='habits')
    op.drop_table('habits')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    op.execute('DROP TYPE IF EXISTS habitfrequency')

