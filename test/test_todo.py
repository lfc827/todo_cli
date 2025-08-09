import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from datetime import datetime, timedelta
from todo_cli.todo import TodoList, Task
import time

# Test adding a task with a due date
def test_add_task_with_due_date():
    # Create a new todo list
    todo = TodoList()

    # Set a due date 3 days from now
    due_date = datetime.now() + timedelta(days=3)

    # Add task with title and due date
    task = todo.add_task("Pay bills", due_date)
    
    # Verify task properties
    assert task.title == "Pay bills"
    assert task.due_date == due_date       

# Test starting and stopping the timer for a task
def test_start_stop_timer():
    todo = TodoList()
    # Add a new task without due date
    task = todo.add_task("Task with timer")
    
    # Start timer
    assert todo.start_timer(task.id) is True
    assert task.timer_started is not None
    
    # Try to start again (should fail)
    assert todo.start_timer(task.id) is False
    
    # Stop timer
    time.sleep(0.1)  # Ensure some time passes
    elapsed = todo.stop_timer(task.id)
    assert elapsed > 0
    assert task.time_spent > 0
    assert task.timer_started is None

# Test overdue task detection
def test_overdue_task():
    todo = TodoList()
    # Create a due date in the past (1 day ago)
    past_date = datetime.now() - timedelta(days=1)
    task = todo.add_task("Overdue task", past_date)
    assert task.is_overdue() is True

# Test retrieval of upcoming tasks
def test_get_upcoming_tasks():
    todo = TodoList()
    now = datetime.now()
    
    # Add tasks with different due dates
    # - Within 2 hours
    # - Tomorrow
    # - Next week
    # - Overdue (yesterday)
    todo.add_task("Today", now + timedelta(hours=2))
    todo.add_task("Tomorrow", now + timedelta(days=1))
    todo.add_task("Next week", now + timedelta(days=7))
    todo.add_task("Overdue", now - timedelta(days=1))
    
    # Get tasks due within next 3 days
    upcoming = todo.get_upcoming_tasks(days=3)

    # Verify only relevant tasks are returned
    assert len(upcoming) == 2  # Should get "Today" and "Tomorrow"
    assert upcoming[0].title == "Today"  # Soonest first
    assert upcoming[1].title == "Tomorrow"

# Test calculation of total time spent across all tasks
def test_total_time_spent():
    todo = TodoList()
    task1 = todo.add_task("Task 1")
    task2 = todo.add_task("Task 2")
    
    # Manually set time spent values
    task1.time_spent = 3600  # 1 hour (3600 seconds)
    task2.time_spent = 1800  # 30 minutes (1800 seconds)
    
    assert todo.get_total_time_spent() == 5400  # 1.5 hours