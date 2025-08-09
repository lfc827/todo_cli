import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import tempfile
from datetime import datetime
from todo_cli.todo import Task
from todo_cli.storage import load_tasks, save_tasks

# Fixture to create sample tasks
@pytest.fixture
def sample_tasks():
    return [
        Task(1, "Task 1", False, datetime(2023, 12, 31)),
        Task(2, "Task 2", True, None),
        Task(3, "Task 3", False, datetime(2023, 11, 15))
    ]

# Test JSON storage functionality including time tracking
def test_json_storage_with_time(sample_tasks):
    # Create a temporary JSON file
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmpfile:
        filename = tmpfile.name
    
    try:
        # Set time spent
        sample_tasks[0].time_spent = 3600  # 1 hour
        
        # Save and load
        save_tasks(sample_tasks, filename)
        loaded = load_tasks(filename)
        
        # Verify data integrity
        assert len(loaded) == 3
        assert loaded[0].id == 1
        assert loaded[0].due_date == datetime(2023, 12, 31)
        assert loaded[0].time_spent == 3600
        assert loaded[1].due_date is None
    finally:
        os.unlink(filename)

# Test CSV storage functionality including time tracking
def test_csv_storage_with_time(sample_tasks):
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmpfile:
        filename = tmpfile.name
    
    try:
        # Set time spent
        sample_tasks[1].time_spent = 1800  # 30 minutes
        
        # Save and load
        save_tasks(sample_tasks, filename)
        loaded = load_tasks(filename)
        
        # Verify data integrity
        # Verify loaded data integrity:
        # 1. Correct number of tasks loaded
        # 2. Second task has correct ID and handles None due date
        # 3. Time spent value is preserved
        # 4. Third task has correct due date
        assert len(loaded) == 3
        assert loaded[1].id == 2
        assert loaded[1].due_date is None
        assert loaded[1].time_spent == 1800
        assert loaded[2].due_date == datetime(2023, 11, 15)
    finally:
        # Clean up temporary file
        os.unlink(filename)