import pytest
import tempfile
import os
from datetime import datetime, timedelta
import shutil

from todo_cli.todo import Task, TodoList


@pytest.fixture
def clean_environment():
    """Ensure clean test environment."""
    # Store original working directory
    original_cwd = os.getcwd()
    
    # Create temporary directory for test files
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)
    
    yield temp_dir
    
    # Cleanup
    os.chdir(original_cwd)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_task():
    """Create a single sample task."""
    return Task(1, "Sample task", due_date=datetime.now() + timedelta(days=1))


@pytest.fixture
def sample_todo_list():
    """Create a TodoList with sample tasks."""
    todo = TodoList()
    now = datetime.now()
    
    # Add various types of tasks
    todo.add_task("Active task")
    todo.add_task("Completed task")
    todo.tasks[1].done = True
    todo.add_task("Due soon", now + timedelta(hours=2))
    todo.add_task("Due later", now + timedelta(days=5))
    todo.add_task("Overdue", now - timedelta(days=1))
    
    return todo


@pytest.fixture
def mock_datetime_now():
    """Mock datetime.now() for consistent testing."""
    fixed_time = datetime(2024, 6, 15, 12, 0, 0)
    
    with pytest.mock.patch('todo_cli.todo.datetime') as mock_dt:
        mock_dt.now.return_value = fixed_time
        mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
        yield fixed_time


# Test markers
pytest_plugins = []

def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "cli: marks tests for CLI functionality"
    )
    config.addinivalue_line(
        "markers", "storage: marks tests for storage functionality"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically add markers based on test file names."""
    for item in items:
        # Add markers based on test file
        if "test_cli" in item.nodeid:
            item.add_marker(pytest.mark.cli)
        elif "test_storage" in item.nodeid:
            item.add_marker(pytest.mark.storage)
        
        # Mark slow tests
        if any(keyword in item.name for keyword in ['integration', 'full_workflow']):
            item.add_marker(pytest.mark.slow)


# Custom assertions
class TodoAssertions:
    """Custom assertions for todo testing."""
    
    @staticmethod
    def assert_task_equals(task1: Task, task2: Task, ignore_timer=True):
        """Assert two tasks are equal, optionally ignoring timer state."""
        assert task1.id == task2.id
        assert task1.title == task2.title
        assert task1.done == task2.done
        assert task1.due_date == task2.due_date
        assert abs(task1.time_spent - task2.time_spent) < 0.01  # Allow small float differences
        
        if not ignore_timer:
            assert task1.timer_start == task2.timer_start
    
    @staticmethod
    def assert_task_list_contains(task_list: list, task_id: int, title: str):
        """Assert task list contains a task with given ID and title."""
        task = next((t for t in task_list if t.id == task_id), None)
        assert task is not None, f"Task with ID {task_id} not found"
        assert task.title == title


@pytest.fixture
def todo_assertions():
    """Provide custom todo assertions."""
    return TodoAssertions