import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import time

from todo_cli.todo import Task, TodoList


class TestTask:
    """Test cases for the Task class."""
    
    def test_task_creation_valid(self):
        """Test creating a task with valid parameters."""
        due_date = datetime.now() + timedelta(days=1)
        task = Task(1, "Test task", due_date=due_date)
        
        assert task.id == 1
        assert task.title == "Test task"
        assert task.done is False
        assert task.due_date == due_date
        assert task.time_spent == 0.0
        assert task.timer_start is None
    
    def test_task_creation_invalid_id(self):
        """Test task creation with invalid ID raises ValueError."""
        with pytest.raises(ValueError, match="Task ID must be a positive integer"):
            Task(0, "Test task")
        
        with pytest.raises(ValueError, match="Task ID must be a positive integer"):
            Task(-1, "Test task")
    
    def test_task_creation_empty_title(self):
        """Test task creation with empty title raises ValueError."""
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            Task(1, "")
        
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            Task(1, "   ")  # Only whitespace
    
    def test_task_title_stripped(self):
        """Test that task title is stripped of whitespace."""
        task = Task(1, "  Test task  ")
        assert task.title == "Test task"
    
    def test_timer_functionality(self):
        """Test timer start/stop functionality."""
        task = Task(1, "Timer test")
        
        # Start timer
        assert task.start_timer() is True
        assert task.timer_start is not None
        assert task.is_timer_running() is True
        
        # Can't start timer twice
        assert task.start_timer() is False
        
        # Stop timer
        time.sleep(0.01)  # Small delay to ensure elapsed time > 0
        elapsed = task.stop_timer()
        assert elapsed > 0
        assert task.time_spent > 0
        assert task.timer_start is None
        assert task.is_timer_running() is False
        
        # Can't stop timer twice
        assert task.stop_timer() == 0.0
    
    def test_timer_completed_task(self):
        """Test timer cannot start on completed task."""
        task = Task(1, "Completed task", done=True)
        assert task.start_timer() is False
    
    def test_overdue_detection(self):
        """Test overdue task detection."""
        past_date = datetime.now() - timedelta(days=1)
        future_date = datetime.now() + timedelta(days=1)
        
        # Overdue task
        overdue_task = Task(1, "Overdue", due_date=past_date)
        assert overdue_task.is_overdue() is True
        
        # Future task
        future_task = Task(2, "Future", due_date=future_date)
        assert future_task.is_overdue() is False
        
        # Completed overdue task should not be overdue
        completed_overdue = Task(3, "Done", done=True, due_date=past_date)
        assert completed_overdue.is_overdue() is False
        
        # No due date
        no_due_date = Task(4, "No date")
        assert no_due_date.is_overdue() is False
    
    def test_remaining_time_calculation(self):
        """Test remaining time calculation."""
        # Future task
        future_date = datetime.now() + timedelta(hours=2)
        task = Task(1, "Future task", due_date=future_date)
        remaining = task.remaining_time_seconds()
        assert remaining is not None
        assert 7000 < remaining < 7300  # Approximately 2 hours
        
        # Past task
        past_date = datetime.now() - timedelta(hours=1)
        overdue_task = Task(2, "Past task", due_date=past_date)
        remaining = overdue_task.remaining_time_seconds()
        assert remaining is not None
        assert remaining < 0
        
        # No due date
        no_date_task = Task(3, "No date")
        assert no_date_task.remaining_time_seconds() is None
        
        # Completed task
        completed_task = Task(4, "Done", done=True, due_date=future_date)
        assert completed_task.remaining_time_seconds() is None
    
    def test_time_formatting(self):
        """Test time formatting functions."""
        task = Task(1, "Time test")
        
        # Test various durations
        task.time_spent = 0
        assert "0s" in task.format_time_spent()
        
        task.time_spent = 45
        assert "45s" in task.format_time_spent()
        
        task.time_spent = 125  # 2m 5s
        formatted = task.format_time_spent()
        assert "2m" in formatted
        assert "5s" in formatted
        
        task.time_spent = 3665  # 1h 1m 5s
        formatted = task.format_time_spent()
        assert "1h" in formatted
        assert "1m" in formatted
        assert "5s" in formatted
        
        task.time_spent = 90000  # 1d 1h
        formatted = task.format_time_spent()
        assert "1d" in formatted
        assert "1h" in formatted
        assert "m" not in formatted  # Minutes should be skipped for days
    
    def test_remaining_time_formatting(self):
        """Test remaining time formatting."""
        # No due date
        task = Task(1, "No date")
        assert task.format_remaining_time() == "No deadline"
        
        # Very soon (< 1 minute)
        soon_date = datetime.now() + timedelta(seconds=30)
        task = Task(2, "Soon", due_date=soon_date)
        assert "very soon" in task.format_remaining_time().lower()
        
        # Future
        future_date = datetime.now() + timedelta(days=2, hours=3)
        task = Task(3, "Future", due_date=future_date)
        formatted = task.format_remaining_time()
        assert "remaining" in formatted
        assert "2d" in formatted
        
        # Overdue
        past_date = datetime.now() - timedelta(hours=5)
        task = Task(4, "Overdue", due_date=past_date)
        formatted = task.format_remaining_time()
        assert "Overdue by" in formatted
        assert "5h" in formatted
    
    def test_task_serialization(self):
        """Test task to_dict and from_dict methods."""
        due_date = datetime(2024, 12, 31, 23, 59)
        task = Task(1, "Serialization test", done=True, due_date=due_date)
        task.time_spent = 3600
        
        # Test to_dict
        data = task.to_dict()
        expected_keys = {'id', 'title', 'done', 'due_date', 'time_spent'}
        assert set(data.keys()) == expected_keys
        assert data['id'] == 1
        assert data['title'] == "Serialization test"
        assert data['done'] is True
        assert data['due_date'] == due_date.isoformat()
        assert data['time_spent'] == 3600
        
        # Test from_dict
        restored_task = Task.from_dict(data)
        assert restored_task.id == task.id
        assert restored_task.title == task.title
        assert restored_task.done == task.done
        assert restored_task.due_date == task.due_date
        assert restored_task.time_spent == task.time_spent
    
    def test_task_serialization_invalid_data(self):
        """Test task deserialization with invalid data."""
        with pytest.raises(ValueError, match="Invalid task data"):
            Task.from_dict({})  # Missing required keys
        
        with pytest.raises(ValueError, match="Invalid task data"):
            Task.from_dict({'id': 'not_an_int', 'title': 'Test'})
        
        # Negative time_spent should be corrected
        task = Task.from_dict({
            'id': 1,
            'title': 'Test',
            'done': False,
            'due_date': None,
            'time_spent': -100  # Negative value
        })
        assert task.time_spent == 0.0  # Should be corrected to 0


class TestTodoList:
    """Test cases for the TodoList class."""
    
    def test_initialization(self):
        """Test TodoList initialization."""
        todo = TodoList()
        assert todo.tasks == []
        assert todo.next_id == 1
    
    def test_add_task(self):
        """Test adding tasks to the list."""
        todo = TodoList()
        due_date = datetime.now() + timedelta(days=1)
        
        task1 = todo.add_task("First task")
        assert task1.id == 1
        assert task1.title == "First task"
        assert task1.due_date is None
        assert len(todo.tasks) == 1
        
        task2 = todo.add_task("Second task", due_date)
        assert task2.id == 2
        assert task2.due_date == due_date
        assert len(todo.tasks) == 2
        
        assert todo.next_id == 3
    
    def test_find_task(self):
        """Test finding tasks by ID."""
        todo = TodoList()
        task = todo.add_task("Find me")
        
        found = todo.find_task(task.id)
        assert found is task
        
        not_found = todo.find_task(999)
        assert not_found is None
    
    def test_list_tasks(self):
        """Test listing tasks with filtering."""
        todo = TodoList()
        task1 = todo.add_task("Active task")
        task2 = todo.add_task("Completed task")
        task2.done = True
        
        # Show active only (default)
        active = todo.list_tasks()
        assert len(active) == 1
        assert active[0] is task1
        
        # Show all tasks
        all_tasks = todo.list_tasks(show_all=True)
        assert len(all_tasks) == 2
        assert task1 in all_tasks
        assert task2 in all_tasks
    
    def test_mark_done(self):
        """Test marking tasks as done."""
        todo = TodoList()
        task = todo.add_task("Complete me")
        task.start_timer()  # Start timer to test it stops
        
        completed = todo.mark_done(task.id)
        assert completed is task
        assert task.done is True
        assert not task.is_timer_running()  # Timer should be stopped
        
        # Can't mark already completed task
        already_done = todo.mark_done(task.id)
        assert already_done is None
        
        # Can't mark non-existent task
        not_found = todo.mark_done(999)
        assert not_found is None
    
    def test_delete_task(self):
        """Test deleting tasks."""
        todo = TodoList()
        task = todo.add_task("Delete me")
        task_id = task.id
        
        deleted = todo.delete_task(task_id)
        assert deleted is task
        assert len(todo.tasks) == 0
        assert todo.find_task(task_id) is None
        
        # Can't delete non-existent task
        not_found = todo.delete_task(999)
        assert not_found is None
    
    def test_timer_operations(self):
        """Test timer start/stop operations."""
        todo = TodoList()
        task = todo.add_task("Timer task")
        task_id = task.id
        
        # Start timer
        assert todo.start_timer(task_id) is True
        assert task.is_timer_running()
        
        # Can't start timer for completed task
        completed_task = todo.add_task("Completed")
        completed_task.done = True
        assert todo.start_timer(completed_task.id) is False
        
        # Stop timer
        time.sleep(0.01)
        elapsed = todo.stop_timer(task_id)
        assert elapsed > 0
        assert not task.is_timer_running()
        
        # Timer operations on non-existent task
        assert todo.start_timer(999) is False
        assert todo.stop_timer(999) == 0.0
    
    def test_upcoming_tasks(self):
        """Test getting upcoming tasks."""
        todo = TodoList()
        now = datetime.now()
        
        # Create tasks with various due dates
        task1 = todo.add_task("Today", now + timedelta(hours=12))
        task2 = todo.add_task("Tomorrow", now + timedelta(days=1))
        task3 = todo.add_task("Next week", now + timedelta(days=7))
        task4 = todo.add_task("Completed", now + timedelta(days=2))
        task4.done = True
        task5 = todo.add_task("No due date")
        task6 = todo.add_task("Overdue", now - timedelta(days=1))
        
        # Get upcoming tasks (default 3 days)
        upcoming = todo.get_upcoming_tasks()
        assert len(upcoming) == 2  # task1 and task2
        assert task1 in upcoming
        assert task2 in upcoming
        
        # Get upcoming tasks with custom days
        upcoming_7 = todo.get_upcoming_tasks(days=7)
        assert len(upcoming_7) == 3  # task1, task2, task3
        
        # Invalid days parameter
        assert todo.get_upcoming_tasks(days=0) == []
        assert todo.get_upcoming_tasks(days=-1) == []
    
    def test_overdue_tasks(self):
        """Test getting overdue tasks."""
        todo = TodoList()
        now = datetime.now()
        
        task1 = todo.add_task("Overdue 1", now - timedelta(days=1))
        task2 = todo.add_task("Overdue 2", now - timedelta(hours=1))
        task3 = todo.add_task("Future", now + timedelta(days=1))
        task4 = todo.add_task("Completed overdue", now - timedelta(days=2))
        task4.done = True
        
        overdue = todo.get_overdue_tasks()
        assert len(overdue) == 2
        assert task1 in overdue
        assert task2 in overdue
        assert task3 not in overdue
        assert task4 not in overdue
    
    def test_total_time_spent(self):
        """Test calculating total time spent."""
        todo = TodoList()
        
        task1 = todo.add_task("Task 1")
        task2 = todo.add_task("Task 2")
        task1.time_spent = 3600  # 1 hour
        task2.time_spent = 1800  # 30 minutes
        
        total = todo.get_total_time_spent()
        assert total == 5400  # 1.5 hours
        
        # Empty list
        empty_todo = TodoList()
        assert empty_todo.get_total_time_spent() == 0