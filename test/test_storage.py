import pytest
import tempfile
import os
import json
import csv
from datetime import datetime
from unittest.mock import patch, mock_open

from todo_cli.todo import Task
from todo_cli.storage import load_tasks, save_tasks, StorageError


@pytest.fixture
def sample_tasks():
    """Create sample tasks for testing."""
    return [
        Task(1, "Task with due date", False, datetime(2024, 12, 31, 23, 59)),
        Task(2, "Completed task", True, None),
        Task(3, "Task with time", False, datetime(2024, 11, 15, 10, 30))
    ]


@pytest.fixture
def temp_json_file():
    """Create a temporary JSON file."""
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
        yield f.name
    try:
        os.unlink(f.name)
    except FileNotFoundError:
        pass


@pytest.fixture
def temp_csv_file():
    """Create a temporary CSV file."""
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
        yield f.name
    try:
        os.unlink(f.name)
    except FileNotFoundError:
        pass


class TestJSONStorage:
    """Test cases for JSON storage functionality."""
    
    def test_save_and_load_json(self, sample_tasks, temp_json_file):
        """Test saving and loading tasks in JSON format."""
        # Add time spent to tasks
        sample_tasks[0].time_spent = 3600  # 1 hour
        sample_tasks[2].time_spent = 1800  # 30 minutes
        
        # Save tasks
        save_tasks(sample_tasks, temp_json_file)
        
        # Verify file exists and contains valid JSON
        assert os.path.exists(temp_json_file)
        with open(temp_json_file) as f:
            data = json.load(f)
            assert isinstance(data, list)
            assert len(data) == 3
        
        # Load tasks
        loaded_tasks = load_tasks(temp_json_file)
        
        # Verify loaded data
        assert len(loaded_tasks) == 3
        
        # Check first task (with due date and time)
        task1 = loaded_tasks[0]
        assert task1.id == 1
        assert task1.title == "Task with due date"
        assert task1.done is False
        assert task1.due_date == datetime(2024, 12, 31, 23, 59)
        assert task1.time_spent == 3600
        
        # Check second task (completed, no due date)
        task2 = loaded_tasks[1]
        assert task2.id == 2
        assert task2.done is True
        assert task2.due_date is None
        assert task2.time_spent == 0
        
        # Check third task (with time spent)
        task3 = loaded_tasks[2]
        assert task3.time_spent == 1800
    
    def test_load_nonexistent_json_file(self):
        """Test loading from non-existent file returns empty list."""
        result = load_tasks('nonexistent.json')
        assert result == []
    
    def test_load_empty_json_file(self, temp_json_file):
        """Test loading from empty JSON file."""
        # Create empty JSON array
        with open(temp_json_file, 'w') as f:
            json.dump([], f)
        
        result = load_tasks(temp_json_file)
        assert result == []
    
    def test_load_invalid_json_file(self, temp_json_file):
        """Test loading from invalid JSON file raises StorageError."""
        # Write invalid JSON
        with open(temp_json_file, 'w') as f:
            f.write('invalid json content')
        
        with pytest.raises(StorageError, match="Error reading.*json"):
            load_tasks(temp_json_file)
    
    def test_load_json_missing_fields(self, temp_json_file):
        """Test loading JSON with missing optional fields."""
        # Create JSON with missing optional fields
        data = [{
            'id': 1,
            'title': 'Minimal task',
            'done': False
            # missing due_date and time_spent
        }]
        
        with open(temp_json_file, 'w') as f:
            json.dump(data, f)
        
        loaded = load_tasks(temp_json_file)
        assert len(loaded) == 1
        task = loaded[0]
        assert task.due_date is None
        assert task.time_spent == 0.0
    
    def test_save_json_backup_creation(self, sample_tasks, temp_json_file):
        """Test that backup is created when saving over existing file."""
        # Create initial file
        with open(temp_json_file, 'w') as f:
            json.dump([{'id': 999, 'title': 'Old task', 'done': False}], f)
        
        # Save new tasks (should create backup)
        save_tasks(sample_tasks, temp_json_file)
        
        # Check backup exists
        backup_file = f"{temp_json_file}.backup"
        assert os.path.exists(backup_file)
        
        # Cleanup backup
        try:
            os.unlink(backup_file)
        except FileNotFoundError:
            pass


class TestCSVStorage:
    """Test cases for CSV storage functionality."""
    
    def test_save_and_load_csv(self, sample_tasks, temp_csv_file):
        """Test saving and loading tasks in CSV format."""
        # Add time spent
        sample_tasks[1].time_spent = 1800  # 30 minutes
        
        # Save tasks
        save_tasks(sample_tasks, temp_csv_file)
        
        # Verify file exists and contains valid CSV
        assert os.path.exists(temp_csv_file)
        
        # Load tasks
        loaded_tasks = load_tasks(temp_csv_file)
        
        # Verify loaded data
        assert len(loaded_tasks) == 3
        
        # Check data integrity
        task1 = loaded_tasks[0]
        assert task1.id == 1
        assert task1.title == "Task with due date"
        assert task1.done is False
        assert task1.due_date == datetime(2024, 12, 31, 23, 59)
        
        task2 = loaded_tasks[1]
        assert task2.id == 2
        assert task2.done is True
        assert task2.due_date is None
        assert task2.time_spent == 1800
    
    def test_csv_with_unicode(self, temp_csv_file):
        """Test CSV handling with Unicode characters."""
        unicode_tasks = [
            Task(1, "Tâche français", False, None),
            Task(2, "タスク日本語", True, None),
            Task(3, "Задача русский", False, None)
        ]
        
        save_tasks(unicode_tasks, temp_csv_file)
        loaded = load_tasks(temp_csv_file)
        
        assert len(loaded) == 3
        assert loaded[0].title == "Tâche français"
        assert loaded[1].title == "タスク日本語"
        assert loaded[2].title == "Задача русский"
    
    def test_csv_special_characters(self, temp_csv_file):
        """Test CSV handling with special characters."""
        special_tasks = [
            Task(1, 'Task with "quotes"', False, None),
            Task(2, "Task with, comma", False, None),
            Task(3, "Task with\nnewline", False, None)
        ]
        
        save_tasks(special_tasks, temp_csv_file)
        loaded = load_tasks(temp_csv_file)
        
        assert len(loaded) == 3
        assert loaded[0].title == 'Task with "quotes"'
        assert loaded[1].title == "Task with, comma"
        assert loaded[2].title == "Task with\nnewline"


class TestStorageErrors:
    """Test error handling in storage operations."""
    
    def test_unsupported_file_format(self, sample_tasks):
        """Test saving/loading unsupported file format raises StorageError."""
        with pytest.raises(StorageError, match="Unsupported file format"):
            save_tasks(sample_tasks, "test.txt")
        
        with pytest.raises(StorageError, match="Unsupported file format"):
            load_tasks("test.xml")
    
    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_permission_error_saving(self, mock_open_func, sample_tasks):
        """Test permission error during save raises StorageError."""
        with pytest.raises(StorageError, match="Error saving"):
            save_tasks(sample_tasks, "test.json")
    
    @patch('builtins.open', side_effect=IOError("Disk full"))
    def test_io_error_saving(self, mock_open_func, sample_tasks):
        """Test I/O error during save raises StorageError."""
        with pytest.raises(StorageError, match="Error saving"):
            save_tasks(sample_tasks, "test.json")
    
    def test_corrupted_csv_file(self, temp_csv_file):
        """Test loading from corrupted CSV file."""
        # Write invalid CSV content
        with open(temp_csv_file, 'w') as f:
            f.write('id,title\n1,"Unclosed quote task\n2,Another task')
        
        with pytest.raises(StorageError, match="Error reading"):
            load_tasks(temp_csv_file)
    
    def test_invalid_task_data_json(self, temp_json_file):
        """Test loading JSON with invalid task data."""
        # Write JSON with invalid task structure
        invalid_data = [
            {'id': 'not_a_number', 'title': 'Invalid task'}
        ]
        
        with open(temp_json_file, 'w') as f:
            json.dump(invalid_data, f)
        
        with pytest.raises(StorageError, match="Error reading"):
            load_tasks(temp_json_file)


class TestStorageIntegration:
    """Integration tests for storage functionality."""
    
    def test_round_trip_consistency(self, temp_json_file, temp_csv_file):
        """Test that data remains consistent through save/load cycles."""
        original_tasks = [
            Task(1, "Consistency test", False, datetime(2024, 6, 15, 14, 30)),
            Task(2, "Another test", True, None)
        ]
        original_tasks[0].time_spent = 7200  # 2 hours
        
        # Test JSON round-trip
        save_tasks(original_tasks, temp_json_file)
        loaded_json = load_tasks(temp_json_file)
        
        # Test CSV round-trip
        save_tasks(original_tasks, temp_csv_file)
        loaded_csv = load_tasks(temp_csv_file)
        
        # Verify both formats preserve data
        for loaded in [loaded_json, loaded_csv]:
            assert len(loaded) == 2
            
            task1 = next(t for t in loaded if t.id == 1)
            assert task1.title == "Consistency test"
            assert task1.done is False
            assert task1.due_date == datetime(2024, 6, 15, 14, 30)
            assert task1.time_spent == 7200
            
            task2 = next(t for t in loaded if t.id == 2)
            assert task2.title == "Another test"
            assert task2.done is True
            assert task2.due_date is None