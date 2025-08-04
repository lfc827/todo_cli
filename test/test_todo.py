import pytest
from datetime import datetime, timedelta
from todo_cli.todo import TodoList, Task
import time

def test_add_task_with_due_date():
    todo = TodoList()
    due_date = datetime.now() + timedelta(days=3)
    task = todo.add_task("Pay bills", due_date)
    assert task.title == "Pay bills"
    assert task.due_date == due_date

def test_start_stop_timer():
    todo = TodoList()
    task = todo.add_task("Task with timer")
    
    # Start timer
    assert todo.start_timer(task.id) is True
    assert task.timer_start is not None
    
    # Try to start again (should fail)
    assert todo.start_timer(task.id) is False
    
    # Stop timer
    time.sleep(0.1)  # Ensure some time passes
    elapsed = todo.stop_timer(task.id)
    assert elapsed > 0
    assert task.time_spent > 0
    assert task.timer_start is None

def test_overdue_task():
    todo = TodoList()
    past_date = datetime.now() - timedelta(days=1)
    task = todo.add_task("Overdue task", past_date)
    assert task.is_overdue() is True

def test_get_upcoming_tasks():
    todo = TodoList()
    now = datetime.now()
    
    # Add tasks with different due dates
    todo.add_task("Today", now + timedelta(hours=2))
    todo.add_task("Tomorrow", now + timedelta(days=1))
    todo.add_task("Next week", now + timedelta(days=7))
    todo.add_task("Overdue", now - timedelta(days=1))
    
    upcoming = todo.get_upcoming_tasks(days=3)
    assert len(upcoming) == 2
    assert upcoming[0].title == "Today"
    assert upcoming[1].title == "Tomorrow"

def test_total_time_spent():
    todo = TodoList()
    task1 = todo.add_task("Task 1")
    task2 = todo.add_task("Task 2")
    
    task1.time_spent = 3600  # 1 hour
    task2.time_spent = 1800  # 30 minutes
    
    assert todo.get_total_time_spent() == 5400  # 1.5 hours